from __future__ import annotations
from uuid import UUID
import hashlib
from datetime import date, datetime, timezone
from decimal import Decimal
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException, UploadFile
from starlette.datastructures import Headers

from app.domain.finance.receipt.interpretation.schema import (
    ExtractedField,
    ExtractedReceiptData,
    ExtractionStatusEnum,
    InterpretationResult,
    InterpretationValidationError,
)
from app.domain.finance.receipt.service import ReceiptService
from app.models import ProcessingStatusEnum, Receipt, User


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


def create_service() -> ReceiptService:
    repository = MagicMock()
    return ReceiptService(repository=repository)


def create_user() -> MagicMock:
    user = MagicMock(spec=User)
    user.id = "11111111-1111-1111-1111-111111111111"
    return user


def create_interpretation(
    *,
    errors: list[InterpretationValidationError] | None = None,
) -> InterpretationResult:
    data = ExtractedReceiptData(
        payment_date=ExtractedField(
            value=date(2026, 9, 15),
            status=ExtractionStatusEnum.FOUND,
        ),
        document_amount=ExtractedField(
            value=Decimal("100.00"),
            status=ExtractionStatusEnum.FOUND,
        ),
        paid_amount=ExtractedField(
            value=Decimal("95.00"),
            status=ExtractionStatusEnum.FOUND,
        ),
        beneficiary=ExtractedField(
            value="EMPRESA EXEMPLO",
            status=ExtractionStatusEnum.FOUND,
        ),
        source_institution=ExtractedField(
            value="Banco Exemplo",
            status=ExtractionStatusEnum.FOUND,
        ),
        destination_institution=ExtractedField(
            value=None,
            status=ExtractionStatusEnum.NOT_FOUND,
        ),
        due_date=ExtractedField(
            value=None,
            status=ExtractionStatusEnum.NOT_FOUND,
        ),
        discount=ExtractedField(
            value=None,
            status=ExtractionStatusEnum.NOT_FOUND,
        ),
        interest=ExtractedField(
            value=None,
            status=ExtractionStatusEnum.NOT_FOUND,
        ),
        fine=ExtractedField(
            value=None,
            status=ExtractionStatusEnum.NOT_FOUND,
        ),
        total_charges=ExtractedField(
            value=None,
            status=ExtractionStatusEnum.NOT_FOUND,
        ),
        payer=ExtractedField(
            value=None,
            status=ExtractionStatusEnum.NOT_FOUND,
        ),
        effective_payer=ExtractedField(
            value=None,
            status=ExtractionStatusEnum.NOT_FOUND,
        ),
        barcode=ExtractedField(
            value=None,
            status=ExtractionStatusEnum.NOT_FOUND,
        ),
        authentication=ExtractedField(
            value=None,
            status=ExtractionStatusEnum.NOT_FOUND,
        ),
        transaction_id=ExtractedField(
            value=None,
            status=ExtractionStatusEnum.NOT_FOUND,
        ),
    )

    return InterpretationResult(
        data=data,
        errors=errors or [],
    )


class TestReceiptService:
    def test_calculate_hash(self):
        service = create_service()
        content = b"conteudo do arquivo"

        result = service._calculate_hash(content)

        assert result == hashlib.sha256(content).hexdigest()

    @pytest.mark.asyncio
    async def test_check_duplicate_raises_when_receipt_is_received(self):
        service = create_service()
        user_id = "11111111-1111-1111-1111-111111111111"

        existing_receipt = MagicMock()
        existing_receipt.processing_status = ProcessingStatusEnum.RECEIVED

        service.find_by = AsyncMock(return_value=existing_receipt)

        with pytest.raises(HTTPException) as exc_info:
            await service._check_duplicate(
                file_hash="abc123",
                user_id=user_id,
            )

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Duplicate receipt"

        service.find_by.assert_awaited_once_with(
            file_hash="abc123",
            user_id=user_id,
            without_throw=True,
        )

    @pytest.mark.asyncio
    async def test_check_duplicate_returns_existing_receipt_when_not_received(
        self,
    ):
        service = create_service()
        user_id = "11111111-1111-1111-1111-111111111111"

        existing_receipt = MagicMock()
        existing_receipt.processing_status = ProcessingStatusEnum.PROCESSED

        service.find_by = AsyncMock(return_value=existing_receipt)

        result = await service._check_duplicate(
            file_hash="abc123",
            user_id=user_id,
        )

        assert result is existing_receipt

    @pytest.mark.asyncio
    async def test_check_duplicate_returns_none_when_receipt_does_not_exist(
        self,
    ):
        service = create_service()
        user_id = "11111111-1111-1111-1111-111111111111"

        service.find_by = AsyncMock(return_value=None)

        result = await service._check_duplicate(
            file_hash="abc123",
            user_id=user_id,
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_persist_received_receipt_creates_received_receipt(
        self,
    ):
        service = create_service()

        file = create_upload_file(
            filename="comprovante.pdf",
            content_type="application/pdf",
            content=b"conteudo",
        )

        user_id = "11111111-1111-1111-1111-111111111111"
        file_hash = "abc123"
        interpretation = create_interpretation()

        saved_receipt = MagicMock()
        service.repository.save = AsyncMock(return_value=saved_receipt)

        result = await service.persist_received_receipt(
            file=file,
            user_id=user_id,
            file_size=9,
            file_hash=file_hash,
            interpretation=interpretation,
        )

        assert result is saved_receipt

        service.repository.save.assert_awaited_once()

        entity = service.repository.save.await_args.kwargs["entity"]

        assert isinstance(entity, Receipt)
        assert entity.user_id == user_id
        assert entity.file_hash == file_hash
        assert entity.file_name == "comprovante.pdf"
        assert entity.file_type == "application/pdf"
        assert entity.file_size == 9
        assert entity.processing_status == ProcessingStatusEnum.RECEIVED
        assert entity.extracted_data == interpretation.data.model_dump(mode="json")

    @pytest.mark.asyncio
    async def test_persist_received_receipt_creates_failed_receipt_when_interpretation_has_errors(
        self,
    ):
        service = create_service()

        file = create_upload_file()

        interpretation = create_interpretation(
            errors=[
                InterpretationValidationError(
                    field="beneficiary",
                    status=ExtractionStatusEnum.NOT_FOUND,
                )
            ]
        )

        service.repository.save = AsyncMock()

        await service.persist_received_receipt(
            file=file,
            user_id="11111111-1111-1111-1111-111111111111",
            file_size=18,
            file_hash="abc123",
            interpretation=interpretation,
        )

        entity = service.repository.save.await_args.kwargs["entity"]

        assert entity.processing_status == ProcessingStatusEnum.FAILED
        assert entity.extracted_data is None

    @pytest.mark.asyncio
    async def test_persist_received_receipt_updates_existing_receipt(
        self,
    ):
        service = create_service()

        file = create_upload_file(
            filename="novo.pdf",
            content_type="application/pdf",
        )

        receipt = MagicMock(spec=Receipt)

        interpretation = create_interpretation()

        service.repository.save = AsyncMock(return_value=receipt)

        result = await service.persist_received_receipt(
            file=file,
            user_id="11111111-1111-1111-1111-111111111111",
            file_size=100,
            file_hash="abc123",
            interpretation=interpretation,
            receipt=receipt,
        )

        assert result is receipt

        assert receipt.file_name == "novo.pdf"
        assert receipt.file_type == "application/pdf"
        assert receipt.file_size == 100
        assert receipt.extracted_data == interpretation.data.model_dump(mode="json")
        assert receipt.processing_status == ProcessingStatusEnum.RECEIVED

        service.repository.save.assert_awaited_once_with(entity=receipt)

    @pytest.mark.asyncio
    async def test_persist_received_receipt_raises_app_http_exception_on_repository_error(
        self,
    ):
        service = create_service()
        file = create_upload_file()
        service.repository.save = AsyncMock(side_effect=RuntimeError("db failure"))

        with pytest.raises(Exception) as exc_info:
            await service.persist_received_receipt(
                file=file,
                user_id="11111111-1111-1111-1111-111111111111",
                file_size=18,
                file_hash="abc123",
                interpretation=create_interpretation(),
            )

        assert exc_info.value.__class__.__name__ == "AppHTTPException"

    @pytest.mark.asyncio
    async def test_received_receipt_raises_app_http_exception_when_processing_fails(
        self,
        monkeypatch,
    ):
        service = create_service()
        user = create_user()
        file = create_upload_file()

        monkeypatch.setattr(
            "app.domain.finance.receipt.service.validate_file",
            AsyncMock(return_value=b"conteudo"),
        )
        service._check_duplicate = AsyncMock(return_value=None)
        service.extraction_service.extract = AsyncMock(side_effect=RuntimeError("extract failed"))

        with pytest.raises(Exception) as exc_info:
            await service.received_receipt(file=file, user=user)

        assert exc_info.value.__class__.__name__ == "AppHTTPException"

    @pytest.mark.asyncio
    async def test_received_receipt_processes_file_successfully(
        self,
        monkeypatch,
    ):
        service = create_service()
        user = create_user()

        file = create_upload_file(
            filename="comprovante.pdf",
            content_type="application/pdf",
            content=b"conteudo",
        )

        interpretation = create_interpretation()

        monkeypatch.setattr(
            "app.domain.finance.receipt.service.validate_file",
            AsyncMock(return_value=b"conteudo"),
        )

        service.extraction_service.extract = AsyncMock(return_value="texto extraido")

        service.interpretation_service.interpret = MagicMock(
            return_value=interpretation
        )

        service._check_duplicate = AsyncMock(return_value=None)

        receipt = MagicMock()
        receipt.id = UUID("22222222-2222-2222-2222-222222222222")
        receipt.file_name = "comprovante.pdf"
        receipt.file_type = "application/pdf"
        receipt.file_size = 9
        receipt.processing_status = ProcessingStatusEnum.PROCESSED

        service.persist_received_receipt = AsyncMock(return_value=receipt)

        result = await service.received_receipt(
            file=file,
            user=user,
        )

        assert result.id == receipt.id
        assert result.data == interpretation.data
        assert result.errors == interpretation.errors
        assert result.file_name == receipt.file_name
        assert result.file_type == receipt.file_type
        assert result.file_size == receipt.file_size
        assert result.processing_status == receipt.processing_status

        service.extraction_service.extract.assert_awaited_once_with(
            content=b"conteudo",
            content_type="application/pdf",
        )

        service.interpretation_service.interpret.assert_called_once_with(
            "texto extraido"
        )

        service.persist_received_receipt.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_received_receipt_raises_when_extracted_text_is_empty(
        self,
        monkeypatch,
    ):
        service = create_service()
        user = create_user()

        file = create_upload_file(
            filename="comprovante.pdf",
            content_type="application/pdf",
            content=b"conteudo",
        )

        interpretation = create_interpretation(
            errors=[
                InterpretationValidationError(
                    field="beneficiary",
                    status=ExtractionStatusEnum.NOT_FOUND,
                )
            ]
        )

        monkeypatch.setattr(
            "app.domain.finance.receipt.service.validate_file",
            AsyncMock(return_value=b"conteudo"),
        )

        service.extraction_service.extract = AsyncMock(return_value="")

        service.interpretation_service.interpret = MagicMock(
            return_value=interpretation
        )

        service._check_duplicate = AsyncMock(return_value=None)

        receipt = MagicMock()
        receipt.id = UUID("22222222-2222-2222-2222-222222222222")
        receipt.file_name = "comprovante.pdf"
        receipt.file_type = "application/pdf"
        receipt.file_size = 9
        receipt.processing_status = ProcessingStatusEnum.FAILED

        service.persist_received_receipt = AsyncMock(return_value=receipt)

        result = await service.received_receipt(
            file=file,
            user=user,
        )

        assert result.id == receipt.id
        assert result.data == interpretation.data
        assert result.errors == interpretation.errors
        assert result.file_name == receipt.file_name
        assert result.file_type == receipt.file_type
        assert result.file_size == receipt.file_size
        assert result.processing_status == receipt.processing_status

        service.extraction_service.extract.assert_awaited_once_with(
            content=b"conteudo",
            content_type="application/pdf",
        )

        service.interpretation_service.interpret.assert_called_once_with("")

        service.persist_received_receipt.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_validate_confirm_receipt_returns_received_receipt(
        self,
    ):
        service = create_service()
        user = create_user()

        receipt = MagicMock()
        receipt.processing_status = ProcessingStatusEnum.RECEIVED

        service.find_by = AsyncMock(return_value=receipt)

        result = await service.validate_confirm_receipt(
            receipt_id="22222222-2222-2222-2222-222222222222",
            user=user,
        )

        assert result is receipt

        service.find_by.assert_awaited_once_with(
            id="22222222-2222-2222-2222-222222222222",
            user_id=user.id,
            without_throw=True,
        )

    @pytest.mark.asyncio
    async def test_validate_confirm_receipt_raises_when_receipt_does_not_exist(
        self,
    ):
        service = create_service()
        user = create_user()

        service.find_by = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await service.validate_confirm_receipt(
                receipt_id="22222222-2222-2222-2222-222222222222",
                user=user,
            )

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Receipt not found"

    @pytest.mark.asyncio
    async def test_validate_confirm_receipt_raises_when_receipt_is_not_received(
        self,
    ):
        service = create_service()
        user = create_user()

        receipt = MagicMock()
        receipt.processing_status = ProcessingStatusEnum.FAILED

        service.find_by = AsyncMock(return_value=receipt)

        with pytest.raises(HTTPException) as exc_info:
            await service.validate_confirm_receipt(
                receipt_id="22222222-2222-2222-2222-222222222222",
                user=user,
            )

        assert exc_info.value.status_code == 409
        assert exc_info.value.detail == ("Receipt is not ready for confirmation")

    @pytest.mark.asyncio
    async def test_confirm_receipt_updates_data_and_status(self):
        service = create_service()

        receipt = MagicMock(spec=Receipt)

        payload = {
            "payment_date": "2026-09-15",
            "paid_amount": "95.00",
            "beneficiary": "EMPRESA EXEMPLO",
            "source_institution": "Banco Exemplo",
            "destination_institution": None,
        }

        service.repository.save = AsyncMock(return_value=receipt)

        result = await service.confirm_receipt(
            receipt=receipt,
            payload=payload,
        )

        assert result is receipt
        assert receipt.extracted_data == (
            service.interpretation_service
            .convert(payload)
            .model_dump(mode="json")
        )
        assert receipt.processing_status == ProcessingStatusEnum.PROCESSED

        service.repository.save.assert_awaited_once_with(entity=receipt)

    @pytest.mark.asyncio
    async def test_update_receipt_status_success(self):
        service = create_service()

        receipt = MagicMock(spec=Receipt)
        receipt.processing_status = ProcessingStatusEnum.RECEIVED

        service.repository.save = AsyncMock(return_value=receipt)

        result = await service.update_receipt_status(
            receipt=receipt,
            status=ProcessingStatusEnum.RECEIVED,
        )

        assert result is receipt
        assert receipt.processing_status == ProcessingStatusEnum.RECEIVED

        service.repository.save.assert_awaited_once_with(entity=receipt)

    @pytest.mark.asyncio
    async def test_get_receipt_returns_receipt_with_extracted_data(self):
        service = create_service()
        user = create_user()

        created_at = datetime(2026, 9, 15, 10, 30, tzinfo=timezone.utc)

        receipt = MagicMock(spec=Receipt)
        receipt.id = UUID("22222222-2222-2222-2222-222222222222")
        receipt.file_name = "comprovante.pdf"
        receipt.file_type = "application/pdf"
        receipt.file_size = 1024
        receipt.processing_status = ProcessingStatusEnum.PROCESSED
        receipt.extracted_data = {
            "payment_date": {
                "value": "2026-09-15",
                "status": "FOUND",
            },
            "document_amount": {
                "value": "100.00",
                "status": "FOUND",
            },
            "paid_amount": {
                "value": "95.00",
                "status": "FOUND",
            },
            "beneficiary": {
                "value": "EMPRESA EXEMPLO",
                "status": "FOUND",
            },
            "source_institution": {
                "value": "Banco Exemplo",
                "status": "FOUND",
            },
            "destination_institution": {
                "value": None,
                "status": "NOT_FOUND",
            },
            "due_date": {
                "value": None,
                "status": "NOT_FOUND",
            },
            "discount": {
                "value": None,
                "status": "NOT_FOUND",
            },
            "interest": {
                "value": None,
                "status": "NOT_FOUND",
            },
            "fine": {
                "value": None,
                "status": "NOT_FOUND",
            },
            "total_charges": {
                "value": None,
                "status": "NOT_FOUND",
            },
            "payer": {
                "value": None,
                "status": "NOT_FOUND",
            },
            "effective_payer": {
                "value": None,
                "status": "NOT_FOUND",
            },
            "barcode": {
                "value": None,
                "status": "NOT_FOUND",
            },
            "authentication": {
                "value": None,
                "status": "NOT_FOUND",
            },
            "transaction_id": {
                "value": None,
                "status": "NOT_FOUND",
            },
        }
        receipt.created_at = created_at
        receipt.updated_at = None
        receipt.deleted_at = None

        service.find_by = AsyncMock(return_value=receipt)

        result = await service.get_receipt(
            receipt_id=str(receipt.id),
            user=user,
        )

        assert result.id == receipt.id
        assert result.file_name == receipt.file_name
        assert result.file_type == receipt.file_type
        assert result.file_size == receipt.file_size
        assert result.processing_status == receipt.processing_status

        assert result.extracted_data is not None
        assert result.extracted_data.payment_date.value == date(2026, 9, 15)
        assert result.extracted_data.document_amount.value == Decimal("100.00")
        assert result.extracted_data.paid_amount.value == Decimal("95.00")
        assert result.extracted_data.beneficiary.value == "EMPRESA EXEMPLO"
        assert result.extracted_data.source_institution.value == "Banco Exemplo"

        assert result.extracted_data.destination_institution.value is None
        assert (
                result.extracted_data.destination_institution.status
                == ExtractionStatusEnum.NOT_FOUND
        )

        assert result.created_at == created_at
        assert result.updated_at is None
        assert result.deleted_at is None

        service.find_by.assert_awaited_once_with(
            id=str(receipt.id),
            user_id=str(user.id),
            without_throw=True,
        )

    @pytest.mark.asyncio
    async def test_get_receipt_returns_receipt_without_extracted_data(self):
        service = create_service()
        user = create_user()

        created_at = datetime(2026, 9, 15, 10, 30, tzinfo=timezone.utc)

        receipt = MagicMock(spec=Receipt)
        receipt.id = UUID("22222222-2222-2222-2222-222222222222")
        receipt.file_name = "comprovante.pdf"
        receipt.file_type = "application/pdf"
        receipt.file_size = 1024
        receipt.processing_status = ProcessingStatusEnum.RECEIVED
        receipt.extracted_data = None
        receipt.created_at = created_at
        receipt.updated_at = None
        receipt.deleted_at = None

        service.find_by = AsyncMock(return_value=receipt)

        result = await service.get_receipt(
            receipt_id=str(receipt.id),
            user=user,
        )

        assert result.id == receipt.id
        assert result.file_name == receipt.file_name
        assert result.file_type == receipt.file_type
        assert result.file_size == receipt.file_size
        assert result.processing_status == receipt.processing_status
        assert result.extracted_data is None
        assert result.created_at == created_at
        assert result.updated_at is None
        assert result.deleted_at is None

        service.find_by.assert_awaited_once_with(
            id=str(receipt.id),
            user_id=str(user.id),
            without_throw=True,
        )

    @pytest.mark.asyncio
    async def test_get_receipt_raises_when_receipt_does_not_exist(self):
        service = create_service()
        user = create_user()

        receipt_id = "22222222-2222-2222-2222-222222222222"

        service.find_by = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await service.get_receipt(
                receipt_id=receipt_id,
                user=user,
            )

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Receipt not found"

        service.find_by.assert_awaited_once_with(
            id=receipt_id,
            user_id=str(user.id),
            without_throw=True,
        )