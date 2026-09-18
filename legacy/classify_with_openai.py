#!/usr/bin/env python3
"""
[DEPRECATED] scripts/classify/preprocess.py로 대체됨.

raw_exhibitions 스키마가 (박람회명/시작일/종료일/참관대상 등 한글 컬럼 + 대륙/food_yn/규모/키워드)
로 바뀌면서, 이 스크립트가 쓰던 continent/product_fit/scale/audience_type 영문 컬럼 체계는
더 이상 앱이 참조하지 않음. 참고용으로만 남겨둠 — 그대로 실행하면 새 스키마와 이름이
겹치지 않는 별도의 영문 컬럼들이 추가될 뿐, raw_exhibitions의 대륙/규모 컬럼과 연동되지 않음.

raw_exhibitions(SQLite) 테이블의 박람회를 OpenAI API로 자동 분류하는 스크립트.

sync_to_db.py 로 크롤링/적재를 마친 뒤 이 스크립트를 실행하면:
    - 아직 분류 안 된 박람회 (신규로 추가된 것)
    - 정보가 업데이트됐는데 분류는 그대로인 박람회 (재분류 필요)
  만 골라서 OpenAI에 보내 분류하고, 그 결과를 같은 DB에 저장합니다.
  (이미 최신으로 분류된 건 다시 부르지 않아 API 비용을 아낍니다)

분류 기준 (3가지, 사용자 확정):
    1. 대륙/권역   -> 아메리카 / 유럽 / 중동·아프리카 / 아시아 / 오세아니아
    2. 제품군 적합도 -> 김부각 / 유과 / 약과 / 누룽지칩 / 고구마스틱 중 해당되는 것 (복수 가능)
    3. 박람회 규모·성격 -> 규모(대형/중형/소형) + 유형(B2B/B2C/B2B·B2C)

사전 준비:
    pip install openai python-dotenv
    .env 파일에 다음을 넣어두세요:
        OPENAI_API_KEY=sk-...

실행:
    python classify_with_openai.py                       # 기본 DB(sabuzak.db), 미분류/재분류 필요분만
    python classify_with_openai.py --db ../instance/sabuzak.db
    python classify_with_openai.py --force                # 전부 다시 분류
    python classify_with_openai.py --limit 20             # 테스트로 20건만
    python classify_with_openai.py --model gpt-4o-mini    # 모델 지정(기본값도 이것)
"""

import argparse
import json
import os
import sqlite3
import sys
import time

from dotenv import load_dotenv
from openai import OpenAI

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sabuzak.db")
DEFAULT_MODEL = "gpt-4o-mini"

CONTINENTS = ["아메리카", "유럽", "중동·아프리카", "아시아", "오세아니아"]
PRODUCTS = ["김부각", "유과", "약과", "누룽지칩", "고구마스틱"]
SCALES = ["대형", "중형", "소형", "미상"]
AUDIENCE_TYPES = ["B2B", "B2C", "B2B/B2C", "미상"]

CLASSIFY_SCHEMA = {
    "name": "exhibition_classification",
    "schema": {
        "type": "object",
        "properties": {
            "continent": {"type": "string", "enum": CONTINENTS},
            "product_fit": {
                "type": "array",
                "items": {"type": "string", "enum": PRODUCTS},
                "description": "이 박람회에 출품하기 적합한 K-전통스낵 제품군. 해당 없으면 빈 배열.",
            },
            "scale": {"type": "string", "enum": SCALES},
            "audience_type": {"type": "string", "enum": AUDIENCE_TYPES},
            "reasoning": {
                "type": "string",
                "description": "판단 근거를 한 문장으로 (내부 참고용)",
            },
        },
        "required": ["continent", "product_fit", "scale", "audience_type", "reasoning"],
        "additionalProperties": False,
    },
    "strict": True,
}

SYSTEM_PROMPT = f"""당신은 K-전통스낵(김부각, 유과, 약과, 누룽지칩, 고구마스틱) 수출기업의
해외 박람회 담당자를 돕는 분류 어시스턴트입니다.
주어진 박람회 정보를 보고 아래 기준으로 정확히 분류하세요.

1. continent: 개최국을 기준으로 다음 중 하나만 선택 - {", ".join(CONTINENTS)}
   (중동·아프리카는 중동 및 아프리카 국가 전체를 포함)
2. product_fit: 박람회의 성격(식품 전반/베이커리/수산물/주류 등)을 보고
   김부각·유과·약과·누룽지칩·고구마스틱 중 이 박람회에 출품하기 적합한 제품만 골라 배열로.
   - 베이커리/제과 박람회 -> 약과, 유과, 고구마스틱 등 단과자류가 잘 맞을 수 있음
   - 수산물 박람회 -> 전통스낵과는 관련 낮음(빈 배열 가능)
   - 종합 식품박람회 -> 여러 제품군이 해당될 수 있음
   - 확신이 없으면 보수적으로 판단
3. scale: 박람회 설명에 방문객 수, 참가기업 수, "국제/세계 최대" 등의 표현이 있으면 참고해서
   대형/중형/소형 중 추정. 정보가 전혀 없으면 "미상".
4. audience_type: 설명에 "trade"/"professional"/"B2B"가 있으면 B2B, "public"/"consumer"가 있으면
   B2C, 둘 다 있으면 B2B/B2C. 알 수 없으면 "미상"."""


def get_client():
    load_dotenv()
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("오류: OPENAI_API_KEY가 설정되어 있지 않습니다 (.env 파일 확인).")
        sys.exit(1)
    return OpenAI(api_key=api_key)


def ensure_columns(conn):
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(raw_exhibitions)")
    existing_cols = {row[1] for row in cur.fetchall()}

    new_cols = {
        "continent": "TEXT",
        "product_fit": "TEXT",          # 콤마로 구분된 문자열로 저장 (예: "약과,유과")
        "scale": "TEXT",
        "audience_type": "TEXT",
        "classify_reasoning": "TEXT",
        "classified_at": "TEXT",
    }
    for col, coltype in new_cols.items():
        if col not in existing_cols:
            cur.execute(f"ALTER TABLE raw_exhibitions ADD COLUMN {col} {coltype}")
    conn.commit()


def fetch_targets(conn, force: bool, limit: int):
    cur = conn.cursor()
    if force:
        query = """
            SELECT id, detail_url, name, period, country, city, venue, intro
            FROM raw_exhibitions
            WHERE is_active = 1
            ORDER BY id
        """
        cur.execute(query)
    else:
        # 미분류(classified_at NULL) 이거나, 내용이 분류 이후에 업데이트된 것만
        query = """
            SELECT id, detail_url, name, period, country, city, venue, intro
            FROM raw_exhibitions
            WHERE is_active = 1
              AND (classified_at IS NULL OR last_updated_at > classified_at)
            ORDER BY id
        """
        cur.execute(query)

    rows = cur.fetchall()
    if limit:
        rows = rows[:limit]
    return rows


def classify_row(client, model, row):
    _, detail_url, name, period, country, city, venue, intro = row

    user_content = (
        f"전시회명: {name}\n"
        f"개최기간: {period}\n"
        f"개최국: {country}\n"
        f"개최도시: {city}\n"
        f"개최장소: {venue}\n"
        f"소개: {intro or '(정보 없음)'}"
    )

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        response_format={"type": "json_schema", "json_schema": CLASSIFY_SCHEMA},
    )
    return json.loads(resp.choices[0].message.content)


def save_classification(conn, exhibition_id, result, ts):
    conn.execute(
        """
        UPDATE raw_exhibitions
        SET continent=?, product_fit=?, scale=?, audience_type=?,
            classify_reasoning=?, classified_at=?
        WHERE id=?
        """,
        (
            result["continent"],
            ",".join(result["product_fit"]),
            result["scale"],
            result["audience_type"],
            result["reasoning"],
            ts,
            exhibition_id,
        ),
    )
    conn.commit()


def main():
    parser = argparse.ArgumentParser(description="OpenAI로 박람회 분류 -> DB 저장")
    parser.add_argument("--db", default=DEFAULT_DB_PATH)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--force", action="store_true", help="이미 분류된 것도 전부 재분류")
    parser.add_argument("--limit", type=int, default=0, help="테스트용: 최대 N건만 처리 (0=전체)")
    args = parser.parse_args()

    client = get_client()
    conn = sqlite3.connect(args.db)
    ensure_columns(conn)

    targets = fetch_targets(conn, args.force, args.limit)
    if not targets:
        print("분류할 신규/변경 항목이 없습니다. (모두 최신 상태)")
        return

    print(f"분류 대상: {len(targets)}건")
    from datetime import datetime, timezone

    success = 0
    failed = 0
    for i, row in enumerate(targets, 1):
        name = row[2]
        print(f"[{i}/{len(targets)}] {name}")
        try:
            result = classify_row(client, args.model, row)
            ts = datetime.now(timezone.utc).isoformat()
            save_classification(conn, row[0], result, ts)
            print(
                f"  -> {result['continent']} / "
                f"{result['product_fit'] or '해당없음'} / "
                f"{result['scale']} / {result['audience_type']}"
            )
            success += 1
        except Exception as e:
            print(f"  -> 실패: {e}")
            failed += 1
        time.sleep(0.3)  # API rate limit 여유

    conn.close()
    print(f"\n완료: 성공 {success}건, 실패 {failed}건")


if __name__ == "__main__":
    main()
