from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from datetime import datetime, date
from collections import defaultdict
from io import BytesIO
from openpyxl import Workbook

from .models import User, Task, TaskDoneToday, TaskHistory
from . import db

dashboard_bp = Blueprint('dashboard', __name__)

# -------------------- Admin Dashboard --------------------
@dashboard_bp.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if current_user.username != "admin":
        return redirect(url_for('dashboard.user_dashboard'))

    if request.method == "POST":
        new_username = request.form.get("username")
        new_password = request.form.get("password")
        task_name = request.form.get("task_name")
        task_points = request.form.get("task_points")
        task_category = request.form.get("task_category")
        task_method = request.form.get("task_method")

        # Add user
        if new_username:
            if User.query.filter_by(username=new_username).first():
                flash(f"Username '{new_username}' already exists!", "error")
            else:
                user = User(username=new_username)
                user.set_password(new_password)
                db.session.add(user)
                db.session.commit()
                flash(f"User '{new_username}' added!", "success")

        # Add task
        if task_name and task_points and task_category and task_method:
            existing_task = Task.query.filter(db.func.lower(Task.name) == task_name.lower()).first()
            if existing_task:
                flash(f"Task '{task_name}' already exists!", "error")
            else:
                task = Task(
                    name=task_name,
                    points=int(task_points),
                    category=task_category,
                    method=task_method
                )
                db.session.add(task)
                db.session.commit()
                flash(f"Task '{task_name}' added!", "success")
            return redirect(url_for('dashboard.admin_dashboard'))

    users = User.query.all()
    tasks = Task.query.all()
    return render_template("admin_dashboard.html", users=users, tasks=tasks)

# -------------------- Reset Password --------------------
@dashboard_bp.route('/admin/reset_password', methods=['POST'])
@login_required
def reset_password():
    if current_user.username != "admin":
        return redirect(url_for('dashboard.user_dashboard'))

    user_id = int(request.form.get("user_id"))
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    if new_password != confirm_password:
        flash("Passwords do not match!", "error")
        return redirect(url_for('dashboard.admin_dashboard'))

    user = User.query.get_or_404(user_id)
    user.set_password(new_password)
    db.session.commit()

    flash(f"Password for {user.username} updated!", "success")
    return redirect(url_for('dashboard.admin_dashboard'))

# -------------------- Delete User --------------------
@dashboard_bp.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    if current_user.username != "admin":
        return redirect(url_for('dashboard.user_dashboard'))

    user = User.query.get_or_404(user_id)
    username = user.username  # Save username before deleting
    db.session.delete(user)
    db.session.commit()
    flash(f"User '{username}' deleted!", "info")
    return redirect(url_for('dashboard.admin_dashboard'))

# -------------------- Delete Task --------------------
@dashboard_bp.route('/delete_task/<int:task_id>')
@login_required
def delete_task(task_id):
    if current_user.username != "admin":
        return redirect(url_for('dashboard.user_dashboard'))

    TaskDoneToday.query.filter_by(task_id=task_id).delete()
    task = Task.query.get_or_404(task_id)
    task_name = task.name  # Save task name before deleting
    db.session.delete(task)
    db.session.commit()
    flash(f"Task '{task_name}' deleted!", "info")
    return redirect(url_for('dashboard.admin_dashboard'))


# -------------------- Update Task --------------------
@dashboard_bp.route('/update_task/<int:task_id>', methods=['POST'])
@login_required
def update_task(task_id):
    if current_user.username != "admin":
        return redirect(url_for('dashboard.user_dashboard'))

    task = Task.query.get_or_404(task_id)
    task_name = task.name  # Save the current task name for the flash
    new_points = request.form.get("new_points")
    new_method = request.form.get("new_method")

    if new_points:
        task.points = int(new_points)

    if new_method:
        task.method = new_method

    db.session.commit()
    flash(f"Task '{task_name}' updated successfully!", "success")
    return redirect(url_for('dashboard.admin_dashboard'))

# -------------------- Update History (Admin) --------------------
@dashboard_bp.route('/admin/update_history', methods=['GET', 'POST'])
@login_required
def update_history():
    if current_user.username != "admin":
        return redirect(url_for('dashboard.user_dashboard'))

    users = User.query.all()
    tasks = Task.query.all()

    selected_date = date.today()
    if request.method == "POST" and request.form.get("date"):
        selected_date = datetime.strptime(request.form.get("date"), "%Y-%m-%d").date()

    start_dt = datetime.combine(selected_date, datetime.min.time())
    end_dt = datetime.combine(selected_date, datetime.max.time())

    history = TaskHistory.query.filter(TaskHistory.timestamp.between(start_dt, end_dt)).all()

    return render_template(
        "admin_dashboard.html",
        users=users,
        tasks=tasks,
        history=history,
        selected_date=selected_date.strftime("%Y-%m-%d")
    )

@dashboard_bp.route('/admin/update_history_user/<int:history_id>', methods=['POST'])
@login_required
def update_history_user(history_id):
    if current_user.username != "admin":
        return redirect(url_for('dashboard.user_dashboard'))

    selected_date_str = request.form.get("selected_date")
    if not selected_date_str:
        return redirect(url_for('dashboard.update_history'))

    try:
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    except ValueError:
        return redirect(url_for('dashboard.update_history'))

    entry = TaskHistory.query.get_or_404(history_id)
    new_user_id = int(request.form.get("user_id"))
    new_user = User.query.get_or_404(new_user_id)

    entry.user_id = new_user.id
    entry.username = new_user.username

    done_today_entry = TaskDoneToday.query.filter_by(task_id=entry.task_id, date=selected_date).first()
    if done_today_entry:
        done_today_entry.user_id = new_user.id
        done_today_entry.username = new_user.username

    db.session.commit()
    flash("Task history updated successfully!", "success")
    return redirect(url_for('dashboard.update_history'))

# -------------------- Export Monthly History --------------------
@dashboard_bp.route("/admin/export_history", methods=["POST"])
@login_required
def export_history():
    if current_user.username != "admin":
        return redirect(url_for("dashboard.user_dashboard"))

    month = int(request.form.get("month"))
    year = int(request.form.get("year"))

    first_day = datetime(year, month, 1)
    next_month = datetime(year + (month // 12), (month % 12) + 1, 1)

    history_entries = TaskHistory.query.filter(TaskHistory.timestamp >= first_day, TaskHistory.timestamp < next_month).all()

    wb = Workbook()
    ws1 = wb.active
    ws1.title = "Task History"
    ws1.append(["Date", "Category", "Task", "User", "Points", "Method", "Comment"])

    for entry in history_entries:
        user_display = entry.user.username if entry.user else entry.username
        ws1.append([
            entry.timestamp.strftime("%Y-%m-%d %H:%M"),
            entry.task_category,
            entry.task_name,
            user_display,
            entry.points_at_completion,
            entry.method_at_completion,
            entry.comment
        ])

    ws2 = wb.create_sheet(title="Monthly Summary")
    ws2.append(["User", "Total Points"])
    points_per_user = defaultdict(int)
    for entry in history_entries:
        user_display = entry.user.username if entry.user else entry.username
        points_per_user[user_display] += entry.points_at_completion

    for username, total_points in points_per_user.items():
        ws2.append([username, total_points])

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    filename = f"task_history_{year}_{month}.xlsx"
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# -------------------- User Dashboard --------------------
@dashboard_bp.route('/user', methods=['GET', 'POST'])
@login_required
def user_dashboard():
    today = date.today()
    tasks = Task.query.all()
    categories = sorted({t.category for t in tasks})

    done_today = TaskDoneToday.query.filter_by(date=today).all()
    done_task_ids = [d.task_id for d in done_today]

    return render_template(
        "user_dashboard.html",
        tasks=tasks,
        categories=categories,
        done_task_ids=done_task_ids,
        done_today=done_today
    )

@dashboard_bp.route('/complete_task', methods=['POST'])
@login_required
def complete_task():
    from datetime import date

    task_id = int(request.form.get("task_id"))
    comment = request.form.get("comment")
    today = date.today()

    task = Task.query.get_or_404(task_id)

    # Prevent duplicates
    exists = TaskDoneToday.query.filter_by(
        user_id=current_user.id,
        task_id=task_id,
        date=today
    ).first()

    if exists:
        return redirect(url_for('dashboard.user_dashboard'))

    # Save today's completion
    done = TaskDoneToday(
        user_id=current_user.id,
        task_id=task.id,
        username=current_user.username,
        task_name=task.name,
        task_category=task.category,
        task_method=task.method,  # <- must add this
        date=today
    )
    db.session.add(done)

    # Save to history once
    history = TaskHistory(
        user_id=current_user.id,
        task_id=task.id,
        username=current_user.username,
        task_name=task.name,
        task_category=task.category,
        method_at_completion=task.method,
        comment=comment,
        points_at_completion=task.points
    )
    db.session.add(history)
    db.session.commit()

    flash(f"Task marked '{task.name}' as completed!", "success")
    return redirect(url_for('dashboard.user_dashboard'))
