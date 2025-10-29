from dotenv import load_dotenv
load_dotenv()

from fastapi import APIRouter, HTTPException, Depends
import models
from database import SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

import os




pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

secret_key = os.getenv("SECRET_KEY")

if not secret_key:
    # This will raise an error if the key is not loaded, stopping your server early
    raise ValueError("SECRET_KEY environment variable not set or loaded correctly.")
    
# Use .strip() to remove any accidental whitespace from the .env file
secret_key = secret_key.strip()




# Use APIRouter instead of FastAPI
router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    role: models.roleEnum
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    role: models.roleEnum | None = None
    password: str | None = Field(None, min_length=8)


# Define an optional auth scheme for the user creation endpoint
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)

def get_optional_current_user(token: str | None = Depends(optional_oauth2_scheme), db: Session = Depends(get_db)):
    if token is None:
        return None
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            return None
        user = db.query(models.User).filter(models.User.email == email).first()
        return user
    except JWTError:
        return None

@router.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db), current_user: models.User | None = Depends(get_optional_current_user)):
    if user.role == models.roleEnum.ADMIN:
        if not current_user or current_user.role != models.roleEnum.ADMIN:
            raise HTTPException(status_code=403, detail="Only an admin can create another admin user.")

    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    print(f"Password: {user.password}, Type: {type(user.password)}")
    new_user = models.User(name=user.name, email=user.email, role=user.role,password=pwd_context.hash(user.password)) 
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/users/")
def read_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

@router.post("/login/")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    # Generate JWT token
    token_data = {"sub": user.email}
    token = jwt.encode(token_data, secret_key, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    print(f"Secret Key hin nuser: {secret_key}")
    try:
        payload = jwt.decode(
        token, 
        secret_key, # OR secret_key.encode("utf-8") 
        algorithms=["HS256"]
        
    )
        print(f"Payload: {token}")
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError as e:
        print(f"JWT Error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    print(f"User: {user.email}, Role: {user.role}")
    return user

@router.post("/setup/create-first-admin")
def create_first_admin(secret_code: str, db: Session = Depends(get_db)):
    """
    Creates the very first admin user. This is a one-time setup endpoint.
    It is protected by a secret code set in the environment variables.
    """
    admin_secret = os.getenv("ADMIN_CREATION_SECRET")

    if not admin_secret or secret_code != admin_secret:
        raise HTTPException(status_code=403, detail="Not authorized")

    if db.query(models.User).filter(models.User.role == models.roleEnum.ADMIN).first():
        raise HTTPException(status_code=400, detail="An admin user already exists.")

    print("Creating the first admin user...")
    hashed_password = pwd_context.hash("admin123")
    admin_user = models.User(
        name="Admin User",
        email="admin@example.com",
        role=models.roleEnum.ADMIN,
        password=hashed_password
    )
    db.add(admin_user)
    db.commit()
    
    print("First admin user created successfully.")
    return {"message": "Admin user created successfully."}

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role not in [models.roleEnum.ADMIN]:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


@router.put("/users/{user_id}")
def update_user(user_id: int, updated_user: UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role not in [models.roleEnum.ADMIN]:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = updated_user.dict(exclude_unset=True)

    if 'email' in update_data and update_data['email'] != user.email:
        existing_user = db.query(models.User).filter(models.User.email == update_data['email']).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

    if 'password' in update_data and update_data['password']:
        hashed_password = pwd_context.hash(update_data['password'])
        update_data['password'] = hashed_password
    elif 'password' in update_data:
        del update_data['password']

    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


class CourseCreate(BaseModel):
    title: str
    description: str

@router.post("/courses/")
def create_course(course: CourseCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    if current_user.role not in [models.roleEnum.ADMIN, models.roleEnum.TEACHER]:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    new_course = models.Course(title=course.title, description=course.description)
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

@router.get("/courses/")
def read_courses(db: Session = Depends(get_db)):
    courses = db.query(models.Course).all()
    return courses

@router.delete("/courses/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role not in [models.roleEnum.ADMIN, models.roleEnum.TEACHER]:
        raise HTTPException(status_code=403, detail="Permission denied")
     
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    db.delete(course)
    db.commit()
    return {"message": "Course deleted successfully"}

@router.put("/courses/{course_id}")
def update_course(course_id: int,newCourse: CourseCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role not in [models.roleEnum.ADMIN, models.roleEnum.TEACHER]:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    course.title = newCourse.title
    course.description = newCourse.description
    db.commit()
    db.refresh(course)
    return course

@router.get("/courses/{course_id}")
def read_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return course

class RegistrationCreate(BaseModel):
    user_id: int
    course_id: int

@router.post("/registrations/")
def create_registration(reg: RegistrationCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    print(current_user.role)
    if current_user.role not in [models.roleEnum.STUDENT, models.roleEnum.ADMIN]:
         raise HTTPException(status_code=403, detail="Permission denied")
    
    exists = db.query(models.Registration).filter(
        models.Registration.user_id == reg.user_id,
        models.Registration.course_id == reg.course_id
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="User already registered for this course")
    
    new_reg = models.Registration(user_id=reg.user_id, course_id=reg.course_id)
    db.add(new_reg)
    db.commit()
    db.refresh(new_reg)
    return new_reg

@router.get("/registrations/")
def read_registrations(db: Session = Depends(get_db)):
    return db.query(models.Registration).all()

@router.delete("/registrations/{registration_id}")
def delete_registration(registration_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role not in [models.roleEnum.STUDENT, models.roleEnum.ADMIN, models.roleEnum.TEACHER]:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    reg = db.query(models.Registration).filter(models.Registration.id == registration_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")
    
    db.delete(reg)
    db.commit()
    return {"message": "Registration deleted successfully"}



@router.get("/me/")
def read_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    print(f"hina nme Key: {secret_key}")
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    print(f"User: {user.email}, Role: {user.role}")
    return user

@router.post("/logout/")
def logout(token: str = Depends(oauth2_scheme)):
    return {"message": "Logout successful"}

@router.get("/resgistrations/{user_id}")
def get_user_registrations(user_id: int, db: Session = Depends(get_db)):
    registrations = db.query(models.Registration).filter(models.Registration.user_id == user_id).all()

    if registrations is None:
        raise HTTPException(status_code=404, detail="No Courses Found for this User")

    return registrations


@router.get("/users/{user_id}/courses")
def get_user_courses(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    courses = db.query(models.Course).filter(models.Course.registrations.any(models.Registration.user_id == user_id)).all()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    if courses is None:
        raise HTTPException(status_code=404, detail="No Courses Found for this User")
    
    return courses