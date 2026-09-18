from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user

from ..extensions import db
from ..models import User

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        # TODO: 비밀번호 해시 검증 (werkzeug.security.check_password_hash)
        if user:
            login_user(user)
            return redirect(url_for("dashboard.index"))
        return render_template("login.html", error="아이디 또는 비밀번호가 올바르지 않습니다.")

    return render_template("login.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
