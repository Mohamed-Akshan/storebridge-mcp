from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class ManagerCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    username: str = Field(min_length=3, max_length=80, pattern=r"^[a-zA-Z0-9._-]+$")
    branch: str
    password: str = Field(min_length=8, max_length=128)


class ManagerUpdate(BaseModel):
    branch: str | None = None
    active: bool | None = None


class PasswordReset(BaseModel):
    new_password: str = Field(min_length=8, max_length=128)


class MyPasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message] = Field(min_length=1, max_length=18)
