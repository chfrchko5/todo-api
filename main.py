from fastapi import Depends, FastAPI, status, HTTPException
from db_init import engine, Base
from schemas import Register, RegisterResponse, Login, LoginResponse, AddTodo
from db_init import get_db
from sqlalchemy.orm import Session
from sqlalchemy_db import User, Todo
from sqlalchemy.exc import IntegrityError
from security import hash_password, verify_password, create_access_token, decode_token
from api_check import get_current_user

app = FastAPI()

# TODO: replace the on_event with lifespan ting
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@app.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register_user(
        user_data: Register,
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

@app.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
def login_user(
        user_data: Login,
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    token = create_access_token({"sub": str(user.user_id)})
    return {
        "email": user_data.email,
        "access_token": token,
        "token_type": "bearer"
    }

@app.post("/todos")
def add_todo(
        todo_data: AddTodo, current_user: dict = Depends(get_current_user())
        # TODO: add the database table for todos
):
    user_id = current_user["user_id"]
    new_todo = Todo(title=todo_data.title, owner_id=user_id)
