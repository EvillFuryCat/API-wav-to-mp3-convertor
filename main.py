import os
from uuid import UUID

from fastapi import Depends, FastAPI, Response, UploadFile, HTTPException, status
from fastapi.responses import FileResponse

from database.database_config import get_db
from database.models import User, Audio
from database.shemas import UserBase, UserCreate, AudioCreate

from sqlalchemy.orm import Session

from scripts import convert_wav_to_mp3


HOST = os.getenv("HOST")
PORT = os.getenv("PORT")

app = FastAPI(title="converter")


@app.post("/users", response_model=UserCreate, status_code=status.HTTP_201_CREATED)
def create_user(user_name: UserBase = None, db: Session = Depends(get_db)) -> UserCreate:
    try:
        new_user = User(user_name=user_name.user_name)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return UserCreate(user_name=new_user.user_name, token=new_user.token)


@app.post("/record", status_code=status.HTTP_201_CREATED)
async def create_audio(
    user_id: int, user_token: UUID, file: UploadFile, response: Response, db: Session = Depends(get_db)
) -> AudioCreate:
    if not (user_id and user_token and file.filename.endswith(".wav")):
        error_message = {"error": "Invalid request parameters."}
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error_message
        )

    try:
        # Проверка наличия пользователя в базе данных
        user = db.query(User).filter_by(id=user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Данного пользователя не существует"},
            )

        # Проверка соответствия токена доступа
        if user.token != user_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access token is invalid",
            )

        # Проверка наличия файла на сервере
        file_name = file.filename.replace("wav", "mp3")
        file_path = f"audio_file/{file_name}"
        if os.path.exists(file_path):
            record = (
                db.query(Audio)
                .filter(Audio.file_name == file_name, Audio.user_id == user_id)
                .first()
            )
            url = f"http://{HOST}:{PORT}/record?id={record.id}&user_id={user.id}"
            response.status_code = status.HTTP_200_OK
            return AudioCreate(url=url)

        # Преобразование файла в формат mp3 и сохранение на сервере
        mp3_file = await convert_wav_to_mp3(file)
        if not mp3_file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "File format is not valid."},
            )
        # Сохранение записи в базе данных
        record = Audio(
            user_id=user_id,
            user_token=user_token,
            file_name=mp3_file["file_name"],
            file_path=mp3_file["path"],
            size=mp3_file["size"],
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        # Возвращение URL для скачивания записи
        url = f"http://{HOST}:{PORT}/record?id={record.id}&user_id={user.id}"
        return AudioCreate(url=url)
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": str(e)},
        )


@app.get("/record", response_class=FileResponse, status_code=status.HTTP_200_OK)
async def get_upload_record(
    id: int, user_id: int, db: Session = Depends(get_db)
) -> FileResponse:
    audio_file = (
        db.query(Audio).filter(Audio.id == id, Audio.user_id == user_id).first()
    )
    if audio_file is None:
        error_message = {"error": "Record not found."}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)
    return FileResponse(
        path=audio_file.file_path,
        filename=audio_file.file_name,
        media_type="multipart/form-data",
    )
