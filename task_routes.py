from flask import Blueprint, render_template

task_bp = Blueprint('task', __name__, template_folder='templates')

@task_bp.route('/tasks')
def tasks():
    # Here you can list tasks later
    return render_template('tasks.html')
