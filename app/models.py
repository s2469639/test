from datetime import datetime

from flask_login import UserMixin

from .extensions import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Exhibition(db.Model):
    """scripts/crawl/sync_to_db.py + scripts/classify/classify_with_openai.py 가
    채우는 raw_exhibitions 테이블을 그대로 매핑한다."""

    __tablename__ = "raw_exhibitions"

    id = db.Column(db.Integer, primary_key=True)
    detail_url = db.Column(db.String(500), unique=True, nullable=False)
    name = db.Column(db.String(255))
    period = db.Column(db.String(255))
    country = db.Column(db.String(120))
    city = db.Column(db.String(120))
    venue = db.Column(db.String(255))
    website = db.Column(db.String(255))
    intro = db.Column(db.Text)
    category = db.Column(db.String(120))
    is_active = db.Column(db.Integer, default=1)
    first_seen_at = db.Column(db.String(64))
    last_seen_at = db.Column(db.String(64))
    last_updated_at = db.Column(db.String(64))

    # classify_with_openai.py 가 추가하는 컬럼
    continent = db.Column(db.String(40))
    product_fit = db.Column(db.String(255))  # 콤마 구분 문자열 (예: "약과,유과")
    scale = db.Column(db.String(20))
    audience_type = db.Column(db.String(20))
    classify_reasoning = db.Column(db.Text)
    classified_at = db.Column(db.String(64))


class ConceptDraft(db.Model):
    __tablename__ = "concept_drafts"

    id = db.Column(db.Integer, primary_key=True)
    exhibition_id = db.Column(db.Integer, db.ForeignKey("raw_exhibitions.id"), nullable=False)
    theme = db.Column(db.String(255))
    slogan = db.Column(db.String(255))
    selling_points = db.Column(db.Text)
    event_plan = db.Column(db.Text)
    status = db.Column(db.String(20), default="draft")  # draft / final
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    exhibition = db.relationship("Exhibition")


class ProposalDraft(db.Model):
    __tablename__ = "proposal_drafts"

    id = db.Column(db.Integer, primary_key=True)
    exhibition_id = db.Column(db.Integer, db.ForeignKey("raw_exhibitions.id"), nullable=False)
    concept_draft_id = db.Column(db.Integer, db.ForeignKey("concept_drafts.id"))
    content = db.Column(db.Text)
    status = db.Column(db.String(20), default="draft")  # draft / final
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    exhibition = db.relationship("Exhibition")
    concept_draft = db.relationship("ConceptDraft")
