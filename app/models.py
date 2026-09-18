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

    실제 SQLite 컬럼명은 한글(예: "박람회명")이지만, 코드에서는 영문 속성명으로
    다루도록 db.Column("<한글 컬럼명>", ...)으로 매핑한다."""

    __tablename__ = "raw_exhibitions"

    id = db.Column("순번", db.Integer, primary_key=True)
    detail_url = db.Column(db.String(500), unique=True, nullable=False)
    name = db.Column("박람회명", db.String(255))
    # YYYYMMDD 정수. 0=날짜 미상, 일자만 미상이면 일(day)=32 (예: 20271032)
    start_date = db.Column("시작일", db.Integer)
    end_date = db.Column("종료일", db.Integer)
    country = db.Column("국가", db.String(120))
    city = db.Column("도시", db.String(120))
    venue = db.Column("장소", db.String(255))
    audience_note = db.Column("참관대상", db.Text)
    website = db.Column("웹사이트", db.String(255))
    intro = db.Column("상세설명", db.Text)
    category = db.Column(db.String(120))
    is_active = db.Column(db.Integer, default=1)
    last_updated_at = db.Column(db.String(64))

    # scripts/classify/preprocess.py가 채우는 분류 결과
    continent = db.Column("대륙", db.String(40))
    food_yn = db.Column(db.Integer)
    scale = db.Column("규모", db.String(20))
    keywords = db.Column("키워드", db.Text)


class ConceptDraft(db.Model):
    __tablename__ = "concept_drafts"

    id = db.Column(db.Integer, primary_key=True)
    exhibition_id = db.Column(db.Integer, db.ForeignKey("raw_exhibitions.순번"), nullable=False)
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
    exhibition_id = db.Column(db.Integer, db.ForeignKey("raw_exhibitions.순번"), nullable=False)
    concept_draft_id = db.Column(db.Integer, db.ForeignKey("concept_drafts.id"))
    content = db.Column(db.Text)
    status = db.Column(db.String(20), default="draft")  # draft / final
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    exhibition = db.relationship("Exhibition")
    concept_draft = db.relationship("ConceptDraft")
