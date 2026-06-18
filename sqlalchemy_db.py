from sqlalchemy.orm import relationship
from db_init import Base
from sqlalchemy import Column, Integer, String, Text, ForeignKey


class User(Base):
    __tablename__ = "users"

    user_id  = Column(Integer, primary_key=True, nullable=False)
    email    = Column(String(50), unique=True, nullable=False)
    password = Column(String, nullable=False)

    todos    = relationship("Todo", back_populates="owner")

class Todo(Base):
    __tablename__ = "todos"

    todo_id     = Column(Integer, primary_key=True, nullable=False)
    title       = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    owner_id    = Column(Integer, ForeignKey("users.user_id"))

    owner       = relationship("User", back_populates="todos")