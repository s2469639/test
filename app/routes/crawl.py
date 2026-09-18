from flask import Blueprint, current_app, jsonify
from flask_login import login_required

from ..services.crawl_runner import get_status, start_crawl

bp = Blueprint("crawl", __name__, url_prefix="/crawl")


@bp.route("/run", methods=["POST"])
@login_required
def run():
    db_path = current_app.config["RAW_DB_PATH"]
    started = start_crawl(db_path)
    if not started:
        return jsonify({"status": "already_running", **get_status()}), 409
    return jsonify({"status": "started", **get_status()})


@bp.route("/status")
@login_required
def status():
    return jsonify(get_status())
