import os
from tempfile import NamedTemporaryFile
from fastapi import HTTPException, UploadFile, status
from pydub import AudioSegment


async def convert_wav_to_mp3(file: UploadFile):
    try:
        with NamedTemporaryFile(mode="wb", delete=False, suffix=".wav") as temp_wav_file:
            temp_wav_file.write(await file.read())
            # Создание директории, если ее нет
            os.makedirs("audio_file", exist_ok=True)
            # Конвертация .wav файла в .mp3 формат
            sound = AudioSegment.from_file(temp_wav_file.name, format="wav")
            file_name = f'{file.filename.split(".")[0]}.mp3'
            mp3_path = f"audio_file/{file_name}"
            sound.export(mp3_path, format="mp3")
            # Получаем размер файла
            file_size = os.path.getsize(mp3_path)
            
            result = {"path": mp3_path, "file_name": file_name, "size": file_size}
            # Удаляем переданный файл формата .wav
            os.remove(temp_wav_file.name)
            # Закрываем поток sound
            sound.close()
            return result 
    except (IOError, TypeError, IndexError, Exception) as e:
        msg = f"Conversion failed: {e}"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
