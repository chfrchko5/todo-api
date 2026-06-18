from pydantic import BaseModel, ConfigDict, EmailStr, Field

class Register(BaseModel):
    email: EmailStr
    password: str

class RegisterResponse(BaseModel):
    user_id: int
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)

class Login(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    email: EmailStr
    message: str = "Login Successful"
    access_token: str
    token_type: str

class AddTodo(BaseModel):
    title: str
    description: str = Field(min_length=1, max_length=3000)