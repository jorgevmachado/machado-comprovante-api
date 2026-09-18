from http import HTTPStatus
from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile
from starlette.datastructures import Headers

from app.domain.finance.receipt.validation import (
    MAX_FILE_SIZE,
    validate_file,
    validate_batch_size,
    MAX_BATCH_FILES,
)


def create_upload_file(
    *,
    filename: str | None = "comprovante.pdf",
    content_type: str = "application/pdf",
    content: bytes = b"conteudo do arquivo",
) -> UploadFile:
    return UploadFile(
        file=BytesIO(content),
        filename=filename,
        headers=Headers(
            {
                "content-type": content_type,
            }
        ),
    )


class TestValidateFile:
    @pytest.mark.asyncio
    async def test_validate_file_returns_content_for_valid_pdf(self):
        content = b"conteudo PDF"
        file = create_upload_file(
            filename="documento.pdf",
            content_type="application/pdf",
            content=content,
        )

        result = await validate_file(file)

        assert result == content

    @pytest.mark.asyncio
    async def test_validate_file_accepts_jpeg(self):
        content = b"conteudo JPEG"
        file = create_upload_file(
            filename="imagem.jpg",
            content_type="image/jpeg",
            content=content,
        )

        result = await validate_file(file)

        assert result == content

    @pytest.mark.asyncio
    async def test_validate_file_accepts_png(self):
        content = b"conteudo PNG"
        file = create_upload_file(
            filename="imagem.png",
            content_type="image/png",
            content=content,
        )

        result = await validate_file(file)

        assert result == content

    @pytest.mark.asyncio
    async def test_validate_file_raises_when_filename_is_missing(self):
        file = create_upload_file(
            filename=None,
            content_type="application/pdf",
        )

        with pytest.raises(HTTPException) as exc_info:
            await validate_file(file)

        assert exc_info.value.status_code == HTTPStatus.BAD_REQUEST
        assert exc_info.value.detail == "File name is required."

    @pytest.mark.asyncio
    async def test_validate_file_raises_for_unsupported_content_type(self):
        file = create_upload_file(
            filename="documento.txt",
            content_type="text/plain",
        )

        with pytest.raises(HTTPException) as exc_info:
            await validate_file(file)

        assert exc_info.value.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert (
            exc_info.value.detail
            == "Unsupported file type. Allowed types are: PDF, JPEG, PNG."
        )

    @pytest.mark.asyncio
    async def test_validate_file_raises_when_content_is_empty(self):
        file = create_upload_file(
            filename="documento.pdf",
            content_type="application/pdf",
            content=b"",
        )

        with pytest.raises(HTTPException) as exc_info:
            await validate_file(file)

        assert exc_info.value.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert exc_info.value.detail == "File is empty."

    @pytest.mark.asyncio
    async def test_validate_file_raises_when_file_exceeds_maximum_size(self):
        content = b"x" * (MAX_FILE_SIZE + 1)

        file = create_upload_file(
            filename="documento.pdf",
            content_type="application/pdf",
            content=content,
        )

        with pytest.raises(HTTPException) as exc_info:
            await validate_file(file)

        assert exc_info.value.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert exc_info.value.detail == (
            f"File size exceeds the maximum allowed size of {MAX_FILE_SIZE} bytes."
        )

    @pytest.mark.asyncio
    async def test_validate_file_accepts_file_at_maximum_size(self):
        content = b"x" * MAX_FILE_SIZE

        file = create_upload_file(
            filename="documento.pdf",
            content_type="application/pdf",
            content=content,
        )

        result = await validate_file(file)

        assert result == content


class TestValidateBatchSize:
    @pytest.mark.asyncio
    async def test_validate_batch_size_more_than_max(self):
        files = [
            create_upload_file(
                filename=f"documento_{i}.pdf",
                content_type="application/pdf",
            )
            for i in range(MAX_BATCH_FILES + 1)
        ]

        with pytest.raises(HTTPException) as exc_info:
            validate_batch_size(files)

        assert exc_info.value.status_code == HTTPStatus.BAD_REQUEST
        assert exc_info.value.detail == (
            f"A maximum of {MAX_BATCH_FILES} files can be uploaded at once."
        )
