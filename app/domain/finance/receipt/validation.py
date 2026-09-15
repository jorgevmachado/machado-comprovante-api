from http import HTTPStatus
from fastapi import UploadFile, HTTPException

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
}

MAX_FILE_SIZE = 10 * 1024 * 1024


async def validate_file(file: UploadFile) -> bytes:
    if not file.filename:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="File name is required."
        )

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="Unsupported file type. Allowed types are: PDF, JPEG, PNG.",
        )
    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="File is empty."
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail=f"File size exceeds the maximum allowed size of {MAX_FILE_SIZE} bytes.",
        )

    return content
