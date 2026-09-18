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
    """scripts/crawl/sync_to_db.py가 채우는 raw_exhibitions 테이블을 그대로 매핑한다.

    DB 컬럼명은 영문 그대로 쓴다 (SQL/ORM에서 매번 따옴표 처리가 필요 없고 다른
    도구와의 호환성도 좋음). 화면에 한글로 보여주는 건 템플릿의 라벨/필터가 담당한다
    (예: app/services/data.py의 format_period, 템플릿의 "박람회명" 같은 고정 라벨)."""

    __tablename__ = "raw_exhibitions"

    id = db.Column(db.Integer, primary_key=True)
    detail_url = db.Column(db.String(500), unique=True, nullable=False)
    name = db.Column(db.String(255))
    # YYYYMMDD 정수. UNKNOWN_DATE(99999999)=날짜 전체 미상, 일자만 미상이면 일(day)=32
    # (tradefairdates_scraper.UNKNOWN_DATE와 동일한 값 — 정렬 시 항상 맨 뒤로 가도록 큰 값)
    start_date = db.Column(db.Integer)
    end_date = db.Column(db.Integer)
    country = db.Column(db.String(120))
    city = db.Column(db.String(120))
    venue = db.Column(db.String(255))
    audience_note = db.Column(db.Text)
    website = db.Column(db.String(255))
    intro = db.Column(db.Text)
    category = db.Column(db.String(120))
    is_active = db.Column(db.Integer, default=1)
    last_updated_at = db.Column(db.String(64))

    # scripts/classify/preprocess.py가 채우는 분류 결과
    continent = db.Column(db.String(40))
    food_yn = db.Column(db.Integer)
    scale = db.Column(db.String(20))
    keywords = db.Column(db.Text)
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
