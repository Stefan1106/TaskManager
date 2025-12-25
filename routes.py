from flask import Blueprint, render_template
from flask_login import login_required

main_bp = Blueprint("main", __name__)

@main_bp.route("/admin")
@login_required
def admin_dashboard():
    return render_template("admin_dashboard.html")
