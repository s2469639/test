from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required

from ..extensions import db
from ..models import ConceptDraft
from ..services.data import get_exhibition
from ..services.llm import generate_booth_concept

bp = Blueprint("concept", __name__, url_prefix="/exhibitions/<int:exhibition_id>/concept")


@bp.route("/", methods=["GET"])
@login_required
def edit(exhibition_id):
    exhibition = get_exhibition(exhibition_id)
    draft = ConceptDraft.query.filter_by(exhibition_id=exhibition_id).first()
    return render_template("concept.html", exhibition=exhibition, draft=draft)


@bp.route("/generate", methods=["POST"])
@login_required
def generate(exhibition_id):
    """"AI 컨셉 자동 생성하기" 버튼 -> LLM 호출 -> JSON 반환 (JS가 화면에 렌더링)."""
    exhibition = get_exhibition(exhibition_id)
    result = generate_booth_concept(exhibition)
    return jsonify(result)


@bp.route("/save", methods=["POST"])
@login_required
def save(exhibition_id):
    """수정된 컨셉을 초안으로 저장."""
    data = request.get_json(force=True)
    draft = ConceptDraft.query.filter_by(exhibition_id=exhibition_id).first()
    if draft is None:
        draft = ConceptDraft(exhibition_id=exhibition_id)
        db.session.add(draft)

    draft.theme = data.get("theme")
    draft.slogan = data.get("slogan")
    draft.selling_points = data.get("selling_points")
    draft.event_plan = data.get("event_plan")
    db.session.commit()

    return jsonify({"status": "saved", "draft_id": draft.id})
