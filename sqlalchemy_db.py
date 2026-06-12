from sqlalchemy.orm import relationship
from db_init import Base
from sqlalchemy import Column, Integer, String, Text, ForeignKey


class User(Base):
    __tablename__ = "users"

    id       = Column(Integer, primary_key=True, nullable=False)
    # TODO: constraint for the email (must fit the <>@<>.<>)
    email    = Column(String(50), unique=True, nullable=False)
    password = Column(String, nullable=False)

    todos    = relationship("Todo", back_populates="owner")

class Todo(Base):
    __tablename__ = "todos"

    id          =    Column(Integer, primary_key=True, nullable=False)
    title       = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    owner_id    = Column(Integer, ForeignKey("users.id"))

    owner       = relationship("User", back_populates="todos")