import os
from uuid import UUID
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, HTTPException, status
from fastapi.responses import FileResponse

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
            raise HTTPException(status_code=status, detail=str(e))
        return UserCreate(user_name=new_user.user_name, token=new_user.token)


@app.post("/record", status_code=status.HTTP_201_CREATED)
async def create_audio(user_id: int, user_token: UUID, file: UploadFile) -> AudioCreate:
    if not (user_id and user_token and file.filename.endswith(".wav")):
        error_message = {"error": "Invalid request parameters."}
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)
    with SessionLocal() as db:
        try:
            # Проверка наличия пользователя в базе данных
            user = db.query(User).filter_by(id=user_id).first()
            if user is None:
                raise HTTPException(status_code=404, detail={"error": "Данного пользователя не существует"})

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
            if mp3_path:
                file_size = os.path.getsize(mp3_path)
                
            # Сохранение записи в базе данных
            record = Audio(
                user_id=user_id,
                user_token=user_token,
                file_name=fifa,
                file_path=mp3_path,
                size=file_size
            )
            db.add(record)
            db.commit()
            db.refresh(record)

            # Возвращение URL для скачивания записи
            url = f'http://0.0.0.0:8000/record?id={record.id}&user_id={user.id}'
            return AudioCreate(url=url)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"error": str(e)})


@app.get("/record", response_class=FileResponse)
async def get_upload_record(id: int, user_id: int):
    with SessionLocal() as db:
        audio_file = db.query(Audio).filter(Audio.id == id, Audio.user_id == user_id).first()
        return FileResponse(path=audio_file.file_path, filename=audio_file.file_name, media_type='multipart/form-data')