import io
import os
from uuid import UUID
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, HTTPException, status

from database.database_config import SessionLocal
from database.models import User, Audio
from database.shemas import UserBase, UserCreate, AudioCreate

from pydub import AudioSegment


app = FastAPI(title="converter")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post('/users', response_model=UserCreate, status_code=status.HTTP_201_CREATED)
def create_user(user_name: UserBase) -> UserCreate:
    with SessionLocal() as db:
        try:
            new_user = User(user_name=user_name.user_name)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status, detail=str(e))
        return UserCreate(user_name=new_user.user_name, token=new_user.token)

@app.post("/record")
async def create_audio(user_id: int, user_token: UUID, file: UploadFile) -> AudioCreate:
    with SessionLocal() as db:
        # Проверка наличия пользователя в базе данных
        user = db.query(User).filter_by(id=user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        # Проверка соответствия токена доступа
        if user.token != user_token:
            raise HTTPException(status_code=403, detail="Access token is invalid")
        # Преобразование файла в формат mp3 и сохранение на сервере
        audio_bytes = await file.read()
        temp_wav_file = f'audio_file/{file.filename}'
        with open(temp_wav_file, "wb") as f:
            f.write(audio_bytes)
        mp3_path = f'audio_file/{file.filename.split(".")[0]}.mp3'
        sound = AudioSegment.from_file(temp_wav_file, format="wav")
        sound.export(mp3_path, format="mp3")
        os.remove(temp_wav_file)
        fifa = f'{file.filename.split(".")[0]}.mp3'
            
        # Сохранение записи в базе данных
        record = Audio(
            user_id=user_id,
            user_token=user_token,
            file_name=fifa,
            file_path=mp3_path
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        # Возвращение URL для скачивания записи
        url = f'http://0.0.0.0:8000/record?id={user.id}&user={user.token}'
        return AudioCreate(url=url)
    