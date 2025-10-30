# 🎓 Student Management System

A full-stack web application that allows administrators, teachers, and students to manage courses, registrations, and user roles efficiently.

This project is designed to demonstrate clean architecture, RESTful API design, authentication with JWT, and role-based access control — built to simulate a small educational management system.

Check live demo: https://sc-system1.vercel.app/homepage
Note: The backend might take a couple minutes until it starts, due to free usage.

---

## 🚀 Tech Stack

### Frontend
- **React.js** (Vite or Create React App)
- **Bootstrap** for UI styling
- **JWT Authentication** (stored client-side)

### Backend
- **Python (FastAPI)**
- **SQLAlchemy** ORM for database modeling
- **JWT** for secure authentication
- **PostgreSQL / SQLite** as the database
- **Render** for backend hosting

---

## ✨ Features

### 👨‍🎓 Students
- Register and log in
- Browse available courses
- Enroll and view their enrollments

### 👩‍🏫 Teachers
- Create and manage courses
- View students enrolled in their courses

### 🛠️ Admin
- Manage all users, courses, and registrations
- Assign roles to new users (Admin / Teacher / Student)

---

## ⚙️ Installation and Setup

### Backend
1. Navigate to the backend folder:
   ```bash
   cd backend
2. Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate  # for mac/linux
venv\Scripts\activate     # for windows

3. Install dependencies:

pip install -r requirements.txt

4. Run the development server:

uvicorn main:app --reload

### Frontend

1. Navigate to the frontend folder:

cd frontend


2. Install dependencies and start the dev server:

npm install
npm start


### Deployment
Frontend

Deployed on Vercel — automatically built from GitHub.

Backend

Deployed on Render as a Web Service.

Start Command (Render):

uvicorn main:app --host 0.0.0.0 --port 10000

📷 Screenshots

<img width="1903" height="918" alt="image" src="https://github.com/user-attachments/assets/e0f9536f-539e-4cc1-8baa-1f491716b139" />
<img width="1901" height="914" alt="image" src="https://github.com/user-attachments/assets/976ce394-bf08-4719-ad07-60b4452b011f" />
<img width="1898" height="910" alt="image" src="https://github.com/user-attachments/assets/691f01d5-24fb-472a-a3e4-03fb4d7f6368" />

🧠 Future Improvements

Add pagination and search for courses

Add assignment uploads and grading

Create analytics dashboard for teachers

Containerize with Docker for easier deployment

Advance front error handeling

Update the design to be responsive

🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

📜 License

MIT License — free to use and modify.

Built with dedication and curiosity — an exploration of code, structure, and simplicity.


