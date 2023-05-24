import os
from .database.models import Audio

UPLOADED_FILES_PATH = "audio_file/"

# async def save_file_to_uploads(file, filename):
#     with open(f'{UPLOADED_FILES_PATH}{filename}', "wb") as uploaded_file:
#         file_content = await file.read()
#         uploaded_file.write(file_content)
#         uploaded_file.close()

# def add_file_to_db(db, **kwargs):
#     new_file = Audio(
#                                 file_id=kwargs['file_id'],
#                                 name=kwargs['full_name'],
#                                 tag=kwargs['tag'],
#                                 size=kwargs['file_size'],
#                                 mime_type=kwargs['file'].content_type,
#                             )
#     db.add(new_file)
#     db.commit()
#     db.refresh(new_file)
#     return 