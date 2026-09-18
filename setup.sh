#!/usr/bin/env bash
# 사부작 로컬 설치 스크립트
#   ./setup.sh          가상환경 생성 + 패키지 설치 + .env 준비 + DB 초기화
# 실행 후 안내에 따라 .env의 OPENAI_API_KEY 등을 채우고 run.py를 실행하세요.

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "[1/4] 가상환경 준비 (.venv)"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate

echo "[2/4] 패키지 설치"
pip install --upgrade pip
pip install -r requirements.txt

echo "[3/4] .env 준비"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "  -> .env 생성됨. OPENAI_API_KEY 등 값을 채워주세요."
else
    echo "  -> .env 이미 존재, 건너뜀"
fi

echo "[4/4] DB 초기화"
mkdir -p instance
export FLASK_APP=run.py
flask init-db

echo
echo "설치 완료."
echo "  1) .env 파일에 SECRET_KEY / OPENAI_API_KEY를 채워주세요."
echo "  2) 박람회 데이터가 필요하면: python scripts/crawl/sync_to_db.py --db instance/sabuzak.db --details"
echo "  3) 실행: source .venv/bin/activate && python run.py"
