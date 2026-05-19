"""Blueprint xác thực người dùng (đăng nhập / đăng xuất)."""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from src.models.user import User
from src.utils.helpers import safe_redirect_url

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password) and user.is_active_user:
            login_user(user, remember=True)
            flash("Đăng nhập thành công!", "success")
            return redirect(safe_redirect_url(url_for("dashboard.index")))

        flash("Tên đăng nhập hoặc mật khẩu không đúng.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Đã đăng xuất.", "info")
    return redirect(url_for("auth.login"))
