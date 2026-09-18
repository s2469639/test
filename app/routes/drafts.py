from flask import Blueprint, render_template
from flask_login import login_required

from ..models import ConceptDraft, ProposalDraft

bp = Blueprint("drafts", __name__, url_prefix="/drafts")


@bp.route("/")
@login_required
def index():
    """작성 중인 박람회: 컨셉/기안서 진행 상태 관리 및 이어서 작성."""
    concept_drafts = ConceptDraft.query.filter_by(status="draft").all()
    proposal_drafts = ProposalDraft.query.filter_by(status="draft").all()
    return render_template(
        "drafts.html",
        concept_drafts=concept_drafts,
        proposal_drafts=proposal_drafts,
    )
