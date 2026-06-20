from fastapi import Depends, FastAPI, status, HTTPException
from contextlib import asynccontextmanager
from db_init import engine, Base
from schemas import Register, RegisterResponse, Login, LoginResponse, TodoData
from db_init import get_db
from sqlalchemy.orm import Session
from sqlalchemy_db import User, Todo
from sqlalchemy.exc import IntegrityError
from security import hash_password, verify_password, create_access_token, decode_token
from api_check import get_current_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

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

@app.get("/todos")
def get_todos(
        page: int = 1,
        limit: int = 10,
        current_user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    offset = (page - 1) * limit

    todos = (
        db.query(Todo)
        .filter(Todo.owner_id == current_user["user_id"])
        .offset(offset)
        .limit(limit)
        .all()
    )

    total = db.query(Todo).filter(Todo.owner_id == current_user["user_id"]).count()

    return {
        "data": todos,
        "page": page,
        "limit": limit,
        "total": total,
        "pages": -(-total // limit)  # ceiling division, e.g. 23 todos → 3 pages
    }


@app.post("/todos")
def add_todo(
        todo_data: TodoData,
        current_user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    user_id = current_user["user_id"]
    new_todo = Todo(title=todo_data.title, description=todo_data.description, owner_id=user_id)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

@app.put("/todos/{todo_id}")
def change_todo(
    todo_id: int,
    todo_data: TodoData,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    todo = db.query(Todo).filter(
        Todo.todo_id == todo_id,
        Todo.owner_id == current_user["user_id"]
    ).first()

    if not todo:
        raise HTTPException(status_code=404, detail="todo not found")

    todo.title = todo_data.title
    todo.description = todo_data.description
    db.commit()
    db.refresh(todo)
    return todo

@app.delete("/todos/{todo_id}")
def delete_todo(
    todo_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    todo = db.query(Todo).filter(
        Todo.todo_id == todo_id,
        Todo.owner_id == current_user["user_id"]
    ).first()

    db.delete(todo)
    db.commit()
    if not todo:
        raise HTTPException(status_code=404, detail="todo not found")

    return f"Successfully deleted task {todo_id}"