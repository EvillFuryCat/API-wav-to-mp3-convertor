from pydantic import BaseModel
from uuid import UUID, uuid4


class UserBase(BaseModel):
    user_name: str


class UserCreate(UserBase):
    token: UUID = uuid4


class AudioCreate(BaseModel):
    url: str
