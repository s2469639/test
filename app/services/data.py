"""raw_exhibitions 테이블 조회/가공. legacy/streamlit_prototype.py 의
mock 데이터 로직을 실제 DB 조회로 대체하는 자리."""

from ..models import Exhibition


def format_date(ymd):
    """시작일/종료일(YYYYMMDD 정수)을 표시용 문자열로. 0=미정, 일=32=일자만 미정."""
    if not ymd:
        return "날짜 미정"
    year, month, day = ymd // 10000, (ymd // 100) % 100, ymd % 100
    if day == 32:
        return f"{year}년 {month}월 (일자 미정)"
    return f"{year:04d}-{month:02d}-{day:02d}"


def format_period(start_date, end_date):
    if not start_date and not end_date:
        return "날짜 미정"
    if start_date == end_date:
        return format_date(start_date)
    return f"{format_date(start_date)} ~ {format_date(end_date)}"


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
    """임박한 날짜 순으로 정렬. 날짜 미상(start_date=0)은 맨 뒤로 보낸다."""
    return (
        Exhibition.query.filter_by(is_active=1, continent=continent)
        .order_by(
            (Exhibition.start_date == 0).asc(),
            Exhibition.start_date.asc(),
        )
        .all()
    )


def get_exhibition(exhibition_id):
    return Exhibition.query.get_or_404(exhibition_id)


def get_market_insight(exhibition):
    """TODO: YoY 성장률 등 시장 인사이트 카드용 데이터 계산 (pandas)."""
    return {}


def get_hs_codes(exhibition):
    """TODO: data/hs_codes.csv 등 정적 참조 데이터에서 조회."""
    return []


def get_regulations(exhibition):
    """TODO: data/regulations.csv 등에서 국가·품목 기준 규제 카드 조회."""
    return []
