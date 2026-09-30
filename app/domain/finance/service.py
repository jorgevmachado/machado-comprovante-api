from app.domain.finance.beneficiary.schema import BeneficiarySchema
from app.domain.finance.beneficiary.service import BeneficiaryService
from app.domain.finance.institution.schema import InstitutionSchema
from app.domain.finance.payment.schema import PaymentSchema
from app.domain.finance.payment.service import PaymentService
from app.domain.finance.receipt.interpretation.schema import ExtractedReceiptData
from app.domain.finance.receipt.schema import ReceiptSchema
from app.domain.finance.receipt.service import ReceiptService
from app.domain.finance.institution.service import InstitutionService
from typing import Annotated
from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.domain.finance.schema import (
    FinanceConfirmResponseSchema,
    FinanceConfirmRequestSchema,
)
from app.models import ProcessingStatusEnum

Session = Annotated[AsyncSession, Depends(get_session)]


class FinanceService:
    def __init__(
        self,
        session: Session,
        receipt_service: ReceiptService | None = None,
        payment_service: PaymentService | None = None,
        beneficiary_service: BeneficiaryService | None = None,
        institution_service: InstitutionService | None = None,
    ):
        self.session = session
        self.receipt_service = receipt_service or ReceiptService.from_session(session)
        self.payment_service = payment_service or PaymentService.from_session(session)
        self.beneficiary_service = (
            beneficiary_service or BeneficiaryService.from_session(session)
        )
        self.institution_service = (
            institution_service or InstitutionService.from_session(session)
        )

    async def confirm(
        self, receipt_id: str, payload: FinanceConfirmRequestSchema, user
    ) -> FinanceConfirmResponseSchema:
        try:
            receipt = await self.receipt_service.validate_confirm_receipt(
                receipt_id=receipt_id, user=user
            )
            await self.payment_service.check_receipt(receipt_id=receipt.id, user=user)
            await self.receipt_service.update_receipt_status(
                receipt=receipt,
                status=ProcessingStatusEnum.PROCESSING,
            )
            beneficiary = await self.beneficiary_service.resolve(
                name=payload.beneficiary
            )
            source_institution = await self.institution_service.resolve(
                name=payload.source_institution
            )
            destination_institution = None
            if payload.destination_institution:
                destination_institution = await self.institution_service.resolve(
                    name=payload.destination_institution
                )

            payment = await self.payment_service.create(
                amount=payload.paid_amount,
                user_id=user.id,
                receipt_id=receipt.id,
                payment_date=payload.payment_date,
                beneficiary_id=beneficiary.id,
                source_institution_id=source_institution.id,
                destination_institution_id=destination_institution.id
                if destination_institution
                else None,
            )

            receipt_updated = await self.receipt_service.confirm_receipt(
                receipt=receipt, payload=payload.model_dump(mode="json")
            )
            beneficiary_schema = BeneficiarySchema(
                id=beneficiary.id,
                name=beneficiary.name,
                created_at=beneficiary.created_at
            )
            source_institution_schema = InstitutionSchema(
                id=source_institution.id,
                name=source_institution.name,
                created_at=source_institution.created_at
            )
            destination_institution_schema = (
                InstitutionSchema(
                    id=destination_institution.id,
                    name=destination_institution.name,
                    created_at=destination_institution.created_at
                )
                if destination_institution
                else None
            )

            return FinanceConfirmResponseSchema(
                beneficiary=beneficiary_schema,
                payment=PaymentSchema(
                    id=payment.id,
                    amount=payment.amount,
                    receipt=ReceiptSchema(
                        id=receipt_updated.id,
                        file_name=receipt_updated.file_name,
                        file_type=receipt_updated.file_type,
                        file_size=receipt_updated.file_size,
                        created_at=receipt_updated.created_at,
                        updated_at=receipt_updated.updated_at,
                        deleted_at=receipt_updated.deleted_at,
                        extracted_data=(
                            ExtractedReceiptData.model_validate(receipt_updated.extracted_data)
                            if receipt_updated.extracted_data is not None else None
                        ),
                        processing_status=receipt_updated.processing_status
                    ),
                    created_at=payment.created_at,
                    beneficiary=beneficiary_schema,
                    payment_date=payment.payment_date,
                    source_institution=source_institution_schema,
                    destination_institution=destination_institution_schema,
                ),
                source_institution=source_institution_schema,
                destination_institution=destination_institution_schema,
            )
        except Exception as e:
            raise e
