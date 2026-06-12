from fastapi import Depends, FastAPI, status, HTTPException
from db_init import engine, Base
from schemas import UserCreate, UserResponse
from db_init import get_db
from sqlalchemy.orm import Session
from sqlalchemy_db import User
from sqlalchemy.exc import IntegrityError
from password_hash import hash_password, verify_password

app = FastAPI()

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
        user_data: UserCreate,
        db: Session = Depends(get_db)
):
    user = User(
        email = user_data.email,
        password = hash_password(user_data.password)
    )

    try:
        db.add(user)  # 2. Stage the insert
        db.commit()  # 3. Write to the DB
        db.refresh(user)  # 4. Reload to get DB-generated fields (id, created_at)
    except IntegrityError:  # handles duplicate email
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with that email already exists."
        )

    return user