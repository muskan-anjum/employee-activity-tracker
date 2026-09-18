from app import app
from models import db, User


def create_test_users():
    with app.app_context():

        admin_email = "admin@workai.com"
        employee_email = "employee@workai.com"

        # Create admin only if it does not already exist
        admin = db.session.scalar(
            db.select(User).where(User.email == admin_email)
        )

        if not admin:
            admin = User(
                name="WorkAI Admin",
                email=admin_email,
                role="admin"
            )
            admin.set_password("Admin@123")
            db.session.add(admin)

        # Create employee only if it does not already exist
        employee = db.session.scalar(
            db.select(User).where(User.email == employee_email)
        )

        if not employee:
            employee = User(
                name="Demo Employee",
                email=employee_email,
                role="employee"
            )
            employee.set_password("Employee@123")
            db.session.add(employee)

        db.session.commit()

        print("Test users created successfully.")
        print("Admin: admin@workai.com")
        print("Employee: employee@workai.com")


if __name__ == "__main__":
    create_test_users()