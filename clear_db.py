from app import create_app, db
from app.models import Task, TaskDoneToday, TaskHistory, User

app = create_app()

with app.app_context():
    # Delete all tasks
    Task.query.delete()
    # Delete today's done tasks
    TaskDoneToday.query.delete()
    # Delete task history
    TaskHistory.query.delete()
    # Optionally, delete users (be careful with admin!)
    # User.query.delete()

    # Commit changes
    db.session.commit()

    print("Database cleared!")
