"""instance/sabuzak.db에서 일부 박람회만 뽑아 원본.csv를 만드는 연습용 스크립트.

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
    # audience_note는 최근에 추가된 컬럼이라, sync_to_db.py를 다시 돌리기 전의
    # 기존 DB에는 없을 수 있음 -> 있으면 쓰고 없으면 빈 값으로 채움
    cols = {row[1] for row in conn.execute("PRAGMA table_info(raw_exhibitions)")}
    audience_expr = "audience_note" if "audience_note" in cols else "''"

    cur = conn.execute(
        f"SELECT name, country, website, {audience_expr}, intro FROM raw_exhibitions "
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
