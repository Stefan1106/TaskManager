from app import create_app, db
from app.models import User, Task, TaskHistory, TaskDoneToday

app = create_app()

with app.app_context():
    db.create_all()   # Creates ALL tables if not existing
    print("Database initialized.")
    print("Existing tasks:", Task.query.all())
