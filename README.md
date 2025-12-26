Task Management & Points Tracking System

A Flask-based web application for managing daily tasks, tracking points, and maintaining a complete task history with admin control, user dashboards, dark mode, and Excel exports.

Features
User

View tasks grouped by category

Complete tasks once per day

Optional comment/description when completing a task

Prevents duplicate task completion per day

View tasks completed today

Dark mode toggle (saved in browser)


Admin

Add and delete users
Reset user passwords
Add, update, and delete tasks
Update task points and methods
View task history by selected date
Reassign task history entries to different users
Export monthly task history to Excel
View monthly point totals per user

Tech Stack

Backend: Flask, Flask-Login
Frontend: HTML, CSS, JavaScript, Jinja2
Database: SQLAlchemy (SQLite or configurable)
Export: Excel (openpyxl)

Tech Stack

Backend: Flask, Flask-Login
Frontend: HTML, CSS, JavaScript, Jinja2
Database: SQLAlchemy (SQLite or configurable)
Export: Excel (openpyxl)

app/
├── __init__.py
├── auth.py
├── dashboard_routes.py
├── models.py
├── _pycache_/
├── templates/
│   ├── admin_dashboard.html
│   └── user_dashboard.html
│   └── login.html
_pycache_
instance/
├── app.db
├── task_manager.db
├── db.sqlite3
├── task_manager.sqlite
venv/
init_db.py
clear_db.py
config.py
create_admin.py
run.py
requirements.txt

python -m venv venv
source venv/bin/activate
python -m venv venv
source venv/bin/activate
flask db init
flask db migrate
flask db upgrade
python init_db.py
python create_admin.py
python run.py
