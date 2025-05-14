from pydantic import BaseModel


class UserRegister(BaseModel):
    username: str
    password: str
    password_confirm: str


class UserLogin(BaseModel):
    username: str
    password: str
