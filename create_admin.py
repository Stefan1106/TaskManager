from app import create_app, db
from app.models import User
import getpass  # To hide password input

app = create_app()

with app.app_context():
    # Check if admin already exists
    if not User.query.filter_by(username="admin").first():
        admin_username = "admin"
        # Prompt for admin password securely
        admin_password = getpass.getpass("Enter admin password: ")

        # Create the admin user and set the password hash
        admin_user = User(username=admin_username)
        admin_user.set_password(admin_password)  # This hashes the password

        # Add the user to the database
        db.session.add(admin_user)
        db.session.commit()
        
        print("Admin user created successfully!")
    else:
        print("Admin user already exists.")
