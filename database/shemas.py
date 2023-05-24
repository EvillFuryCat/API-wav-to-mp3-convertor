from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class UserBase(BaseModel):
    user_name: str = Field()


class UserCreate(UserBase):
    token: UUID = uuid4()
