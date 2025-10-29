import os
import sys
from dotenv import load_dotenv

# Ensure the script can locate the 'Backend' module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env for local testing (Render will use environment variables)
load_dotenv()

# Import backend components
from Backend.database import SessionLocal, engine, Base
from Backend.models import User, Course, Registration, roleEnum
from Backend.endpoints import pwd_context  # For hashing passwords


def seed_database():
    """Populates the database with initial data."""
    db = SessionLocal()

    try:
        print("🌱 Seeding database...")

        # --- Create Users ---
        if db.query(User).count() == 0:
            print("👥 Creating users...")
            users_data = [
                ("Admin User", "admin@example.com", roleEnum.ADMIN, "lopalopes2008"),
                ("Student One", "student1@example.com", roleEnum.STUDENT, "student123"),
                ("Student Two", "student2@example.com", roleEnum.STUDENT, "student234"),
                ("Student Three", "student3@example.com", roleEnum.STUDENT, "student345"),
                ("Teacher One", "teacher1@example.com", roleEnum.TEACHER, "teacher123"),
                ("Teacher Two", "teacher2@example.com", roleEnum.TEACHER, "teacher234"),
                ("Teacher Three", "teacher3@example.com", roleEnum.TEACHER, "teacher345"),
            ]

            users = []
            for name, email, role, password in users_data:
                hashed_pw = pwd_context.hash(password)
                users.append(User(name=name, email=email, role=role, password=hashed_pw))

            db.add_all(users)
            db.commit()
            print("✅ Users created successfully.")
        else:
            print("⚠️ Users already exist, skipping creation.")

        # --- Create Courses ---
        if db.query(Course).count() == 0:
            print("📘 Creating courses...")
            courses_data = [
                ("Introduction to Python", "A beginner's course on Python programming."),
                ("Web Development with FastAPI", "Learn to build modern and scalable web APIs."),
                ("Database Management", "Fundamentals of SQL, normalization, and design."),
                ("Machine Learning Basics", "An introduction to algorithms that learn from data."),
                ("Frontend Development with React", "Build interactive interfaces using React."),
                ("Data Structures and Algorithms", "Master the foundations of problem solving."),
                ("Software Engineering Principles", "Learn best practices in software design."),
                ("Operating Systems", "Understand how computers manage resources and processes."),
                ("Cybersecurity Fundamentals", "Basics of security, encryption, and ethical hacking."),
            ]

            courses = [Course(title=title, description=desc) for title, desc in courses_data]
            db.add_all(courses)
            db.commit()
            print("✅ Courses created successfully.")
        else:
            print("⚠️ Courses already exist, skipping creation.")

        # --- Create Registrations ---
        if db.query(Registration).count() == 0:
            print("🧾 Creating registrations...")

            # Fetch users and courses
            students = db.query(User).filter(User.role == roleEnum.STUDENT).all()
            courses = db.query(Course).all()

            if not students or not courses:
                print("❌ Missing users or courses. Cannot create registrations.")
            else:
                registrations = []

                # Assign each student to multiple random courses
                for i, student in enumerate(students):
                    assigned_courses = courses[i % len(courses): (i % len(courses)) + 3]
                    # Ensure wrap-around if needed
                    if len(assigned_courses) < 3:
                        assigned_courses += courses[:3 - len(assigned_courses)]

                    for course in assigned_courses:
                        registrations.append(Registration(user_id=student.id, course_id=course.id))

                db.add_all(registrations)
                db.commit()
                print(f"✅ Created {len(registrations)} registrations successfully.")
        else:
            print("⚠️ Registrations already exist, skipping creation.")

        print("\n🌸 Database seeding complete! All is alive and connected.\n")

    finally:
        db.close()


if __name__ == "__main__":
    if not os.getenv("DATABASE_URL"):
        print("🚫 ERROR: DATABASE_URL environment variable is not set.")
    else:
        seed_database()

