from flask import Blueprint, render_template
from flask_login import login_required

from ..services.data import get_exhibition, get_hs_codes, get_market_insight, get_regulations
from ..services.exchange import get_exchange_rate

bp = Blueprint("exhibition", __name__, url_prefix="/exhibitions")


@bp.route("/<int:exhibition_id>")
@login_required
def detail(exhibition_id):
    """박람회 상세. 개요 / 시장·트렌드 / HS코드 / 수출 주의사항 4탭 + 실시간 환율."""
    exhibition = get_exhibition(exhibition_id)
    exchange_rate = get_exchange_rate(base="USD", target="KRW")
    market_insight = get_market_insight(exhibition)
    hs_codes = get_hs_codes(exhibition)
    regulations = get_regulations(exhibition)

    return render_template(
        "exhibition.html",
        exhibition=exhibition,
        exchange_rate=exchange_rate,
        market_insight=market_insight,
        hs_codes=hs_codes,
        regulations=regulations,
    )
