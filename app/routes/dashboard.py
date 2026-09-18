from flask import Blueprint, render_template
from flask_login import login_required

from ..services.data import count_exhibitions_by_continent, list_exhibitions_by_continent

bp = Blueprint("dashboard", __name__)


@bp.route("/")
@login_required
def index():
    """세계 지도 화면. 대륙별 박람회 개수를 핀으로 표시한다."""
    counts = count_exhibitions_by_continent()
    return render_template("dashboard.html", counts=counts)


@bp.route("/continent/<continent>")
@login_required
def continent(continent):
    """선택한 대륙의 박람회 목록."""
    exhibitions = list_exhibitions_by_continent(continent)
    return render_template("continent.html", continent=continent, exhibitions=exhibitions)
