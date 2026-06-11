from db_init import Base
from sqlalchemy import Column, Integer, String

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    # TODO: constraint for the email (must fit the <>@<>.<>)
    email = Column(String(50), unique=True, nullable=False)
    password = Column(String, nullable=False)