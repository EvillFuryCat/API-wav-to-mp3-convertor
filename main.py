from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from database.database_config import SessionLocal
from database.models import User
from database.shemas import UserBase, UserCreate


app = FastAPI(title="converter")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post('/users', response_model=UserCreate)
def create_user(user_name: UserBase) -> UserCreate:
    with SessionLocal() as db:
        try:
            new_user = User(user_name=user_name.user_name)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        return UserCreate(user_name=new_user.user_name, token=new_user.token)

