"""raw_exhibitions 테이블 조회/가공. legacy/streamlit_prototype.py 의
mock 데이터 로직을 실제 DB 조회로 대체하는 자리."""

from ..models import Exhibition


def count_exhibitions_by_continent():
    rows = (
        Exhibition.query.filter_by(is_active=1)
        .with_entities(Exhibition.continent, Exhibition.id)
        .all()
    )
    counts = {}
    for continent, _ in rows:
        if not continent:
            continue
        counts[continent] = counts.get(continent, 0) + 1
    return counts


def list_exhibitions_by_continent(continent):
    return Exhibition.query.filter_by(is_active=1, continent=continent).all()


def get_exhibition(exhibition_id):
    return Exhibition.query.get_or_404(exhibition_id)


def get_market_insight(exhibition):
    """TODO: YoY 성장률 등 시장 인사이트 카드용 데이터 계산 (pandas)."""
    return {}


def get_hs_codes(exhibition):
    """TODO: data/hs_codes.csv 등 정적 참조 데이터에서 product_fit 기준으로 조회."""
    return []


def get_regulations(exhibition):
    """TODO: data/regulations.csv 등에서 국가·품목 기준 규제 카드 조회."""
    return []
