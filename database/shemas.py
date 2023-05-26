from pydantic import BaseModel, validator
from uuid import UUID


class UserBase(BaseModel):
    user_name: str
    
    @validator("user_name")
    def check_alnum(cls, item: str) -> str:
        assert item.replace(' ', '').isalnum(), "only alphanumeric characters are allowed"
        return item


class UserCreate(UserBase):
    token: UUID


class AudioCreate(BaseModel):
    url: str
