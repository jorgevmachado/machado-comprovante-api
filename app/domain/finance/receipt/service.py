from __future__ import annotations

import logging

from http import HTTPStatus

import hashlib

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, HTTPException

from app.core.exceptions import handle_service_exception
from app.core.logging import LoggingParams, log_service_success
from app.core.service import BaseService
from app.domain.finance.receipt.extraction.service import ExtractionService
from app.domain.finance.receipt.interpretation.schema import (
    InterpretationResult,
    ExtractedReceiptData,
)
from app.domain.finance.receipt.interpretation.service import InterpretationService

from app.domain.finance.receipt.repository import (
    ReceiptRepository,
)
from app.domain.finance.receipt.schema import ReceiptSchema, UploadReceiptResponseSchema
from app.domain.finance.receipt.validation import validate_file

from app.models import (
    Receipt,
    User,
    ProcessingStatusEnum,
)

logger = logging.getLogger(__name__)


class ReceiptService(BaseService[ReceiptRepository, Receipt]):
    def __init__(self, repository: ReceiptRepository) -> None:
        super().__init__(
            alias="Receipt",
            repository=repository,
            logger_params=LoggingParams(
                logger=logger, service="ReceiptService", operation="receipt"
            ),
            schema_class=ReceiptSchema,
            cache_prefix="receipt",
        )
        self.extraction_service = ExtractionService()
        self.interpretation_service = InterpretationService()

    @classmethod
    def from_session(cls, session: AsyncSession) -> ReceiptService:
        return cls(ReceiptRepository(session))

    def _calculate_hash(self, content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    async def _check_duplicate(self, file_hash: str, user_id: UUID) -> None:
        existing_receipt = await self.find_by(
            file_hash=file_hash, user_id=str(user_id), without_throw=True
        )
        if (
            existing_receipt
            and existing_receipt.processing_status == ProcessingStatusEnum.RECEIVED
        ):
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail="Duplicate receipt"
            )

        return existing_receipt

    async def persist_received_receipt(
        self,
        file: UploadFile,
        user_id: UUID,
        file_size: int,
        file_hash: str,
        interpretation: InterpretationResult,
        receipt: Receipt | None = None,
    ) -> Receipt:
        try:
            processing_status = (
                ProcessingStatusEnum.RECEIVED
                if not interpretation.errors
                else ProcessingStatusEnum.FAILED
            )
            interpretation_data = (
                interpretation.data.model_dump(mode="json")
                if processing_status == ProcessingStatusEnum.RECEIVED
                else None
            )
            if receipt:
                receipt.file_name = file.filename
                receipt.file_type = file.content_type
                receipt.file_size = file_size
                receipt.extracted_data = interpretation_data
                receipt.processing_status = processing_status
                return await self.repository.save(entity=receipt)
            return await self.repository.save(
                entity=Receipt(
                    user_id=user_id,
                    file_hash=file_hash,
                    file_name=file.filename,
                    file_type=file.content_type,
                    file_size=file_size,
                    extracted_data=interpretation_data,
                    processing_status=processing_status,
                )
            )
        except Exception as exception:
            handle_service_exception(
                exception,
                logger=self.logger_params.logger,
                service=self.logger_params.service,
                operation="persist_received_receipt",
                raise_exception=True,
            )

    async def received_receipt(
        self, file: UploadFile, user: User
    ) -> UploadReceiptResponseSchema:
        try:
            content = await validate_file(file)
            file_hash = self._calculate_hash(content)
            receipt = await self._check_duplicate(file_hash=file_hash, user_id=user.id)

            text = await self.extraction_service.extract(
                content=content, content_type=file.content_type
            )

            interpretation = self.interpretation_service.interpret(text)

            file_size = len(content)
            entity = await self.persist_received_receipt(
                file=file,
                user_id=user.id,
                file_size=file_size,
                file_hash=file_hash,
                interpretation=interpretation,
                receipt=receipt,
            )

            return UploadReceiptResponseSchema(
                id=entity.id,
                data=interpretation.data,
                errors=interpretation.errors,
                file_name=entity.file_name,
                file_type=entity.file_type,
                file_size=entity.file_size,
                processing_status=entity.processing_status,
            )
        except Exception as exception:
            handle_service_exception(
                exception,
                logger=self.logger_params.logger,
                service=self.logger_params.service,
                operation="received_receipt",
                raise_exception=True,
            )
        finally:
            log_service_success(
                self.logger_params,
                operation="received_receipt",
                message="Receipt file validated successfully",
                user_request=f"User ID: {user.id}, File Name: {file.filename}",
            )

    async def validate_confirm_receipt(self, receipt_id: str, user: User) -> Receipt:
        receipt = await self.find_by(
            id=receipt_id, user_id=str(user.id), without_throw=True
        )
        if not receipt:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="Receipt not found"
            )
        if receipt.processing_status != ProcessingStatusEnum.RECEIVED:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Receipt is not ready for confirmation",
            )
        return receipt

    async def update_receipt_status(
        self, receipt: Receipt, status: ProcessingStatusEnum
    ) -> Receipt:
        receipt.processing_status = status
        return await self.repository.save(entity=receipt)

    async def confirm_receipt(
        self,
        receipt: Receipt,
        payload: dict[str, object],
    ) -> Receipt:
        extracted_data = self.interpretation_service.convert(payload)
        receipt.extracted_data = extracted_data.model_dump(mode="json")
        receipt.processing_status = ProcessingStatusEnum.PROCESSED
        return await self.repository.save(entity=receipt)

    async def get_receipt(self, receipt_id: str, user: User) -> ReceiptSchema:
        receipt = await self.find_by(
            id=receipt_id, user_id=str(user.id), without_throw=True
        )
        if not receipt:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="Receipt not found"
            )

        extracted_data = (
            ExtractedReceiptData.model_validate(receipt.extracted_data)
            if receipt.extracted_data is not None
            else None
        )

        return ReceiptSchema(
            id=receipt.id,
            file_name=receipt.file_name,
            file_type=receipt.file_type,
            file_size=receipt.file_size,
            processing_status=receipt.processing_status,
            extracted_data=extracted_data,
            created_at=receipt.created_at,
            updated_at=receipt.updated_at,
            deleted_at=receipt.deleted_at,
        )
