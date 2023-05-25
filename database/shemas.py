from pydantic import BaseModel
from uuid import UUID


class UserBase(BaseModel):
    user_name: str


class UserCreate(UserBase):
    token: UUID


class AudioCreate(BaseModel):
    url: str
