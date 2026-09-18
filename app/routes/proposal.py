from flask import Blueprint, jsonify, render_template, request, send_file
from flask_login import login_required

from ..extensions import db
from ..models import ConceptDraft, ProposalDraft
from ..services.data import get_exhibition
from ..services.export import export_pdf, export_word
from ..services.llm import generate_proposal

bp = Blueprint("proposal", __name__, url_prefix="/exhibitions/<int:exhibition_id>/proposal")


@bp.route("/", methods=["GET"])
@login_required
def edit(exhibition_id):
    exhibition = get_exhibition(exhibition_id)
    draft = ProposalDraft.query.filter_by(exhibition_id=exhibition_id).first()
    return render_template("proposal.html", exhibition=exhibition, draft=draft)


@bp.route("/generate", methods=["POST"])
@login_required
def generate(exhibition_id):
    exhibition = get_exhibition(exhibition_id)
    concept = ConceptDraft.query.filter_by(exhibition_id=exhibition_id).first()
    result = generate_proposal(exhibition, concept)
    return jsonify(result)


@bp.route("/save", methods=["POST"])
@login_required
def save(exhibition_id):
    data = request.get_json(force=True)
    draft = ProposalDraft.query.filter_by(exhibition_id=exhibition_id).first()
    if draft is None:
        draft = ProposalDraft(exhibition_id=exhibition_id)
        db.session.add(draft)

    draft.content = data.get("content")
    db.session.commit()

    return jsonify({"status": "saved", "draft_id": draft.id})


@bp.route("/export/pdf")
@login_required
def export_as_pdf(exhibition_id):
    draft = ProposalDraft.query.filter_by(exhibition_id=exhibition_id).first_or_404()
    path = export_pdf(draft)
    return send_file(path, as_attachment=True)


@bp.route("/export/word")
@login_required
def export_as_word(exhibition_id):
    draft = ProposalDraft.query.filter_by(exhibition_id=exhibition_id).first_or_404()
    path = export_word(draft)
    return send_file(path, as_attachment=True)
