"""[DEPRECATED] scripts/classify/preprocess.py가 이제 DB를 직접 읽고 써서
(classified_at 기준으로 미분류/변경분만) 이 CSV 샘플 추출 단계가 필요 없어짐.
연습 시에는 `python preprocess.py --limit 5`처럼 --limit만 쓰면 됨.

instance/sabuzak.db에서 일부 박람회만 뽑아 원본.csv를 만드는 연습용 스크립트.

사용법 (scripts/classify 폴더에서 실행):
    python make_sample_csv.py            # 기본 5건
    python make_sample_csv.py --limit 30 # 30건
"""

import argparse
import csv
import os
import sqlite3

DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "instance", "sabuzak.db"
)


def main():
    parser = argparse.ArgumentParser(description="raw_exhibitions -> 원본.csv 샘플 추출")
    parser.add_argument("--db", default=DEFAULT_DB_PATH)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--out", default="원본.csv")
    args = parser.parse_args()

    if not os.path.exists(args.db):
        raise FileNotFoundError(f"DB 파일을 찾을 수 없습니다: {args.db}")

    conn = sqlite3.connect(args.db)
    cols = {row[1] for row in conn.execute("PRAGMA table_info(raw_exhibitions)")}
    if "name" not in cols:
        raise RuntimeError(
            "이 DB는 아직 예전 스키마입니다. 먼저 "
            "`python ../crawl/sync_to_db.py --db <이 DB 경로>`를 한 번 실행해서 "
            "새 스키마로 마이그레이션한 뒤 다시 시도해주세요."
        )

    cur = conn.execute(
        "SELECT name, country, website, audience_note, intro FROM raw_exhibitions "
        "WHERE is_active = 1 LIMIT ?",
        (args.limit,),
    )
    rows = cur.fetchall()
    conn.close()

    with open(args.out, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "country", "website", "참관대상", "intro"])
        writer.writerows(rows)

    print(f"{len(rows)}건 저장 완료 -> {args.out}")


if __name__ == "__main__":
    main()
