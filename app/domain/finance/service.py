from app.domain.finance.beneficiary.schema import BeneficiarySchema
from app.domain.finance.beneficiary.service import BeneficiaryService
from app.domain.finance.category.schema import CategorySchema
from app.domain.finance.category.service import CategoryService
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
    FinanceUpdatePaymentRequestSchema,
)
from app.models import ProcessingStatusEnum, User

Session = Annotated[AsyncSession, Depends(get_session)]


class FinanceService:
    def __init__(
        self,
        session: Session,
        receipt_service: ReceiptService | None = None,
        payment_service: PaymentService | None = None,
        category_service: CategoryService | None = None,
        beneficiary_service: BeneficiaryService | None = None,
        institution_service: InstitutionService | None = None,
    ):
        self.session = session
        self.receipt_service = receipt_service or ReceiptService.from_session(session)
        self.payment_service = payment_service or PaymentService.from_session(session)
        self.category_service = category_service or CategoryService.from_session(session)
        self.beneficiary_service = (
            beneficiary_service or BeneficiaryService.from_session(session)
        )
        self.institution_service = (
            institution_service or InstitutionService.from_session(session)
        )

    async def confirm(
        self, receipt_id: str, payload: FinanceConfirmRequestSchema, user: User
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

            category = await self.category_service.resolve(
                name=payload.category,
                user_id=user.id,
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
                category_id=category.id,
                description=payload.description,
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

            category_schema = CategorySchema(
                id=category.id,
                name=category.name,
                created_at=category.created_at,
            )

            beneficiary_schema = BeneficiarySchema(
                id=beneficiary.id,
                name=beneficiary.name,
                created_at=beneficiary.created_at,
            )
            source_institution_schema = InstitutionSchema(
                id=source_institution.id,
                name=source_institution.name,
                created_at=source_institution.created_at,
            )
            destination_institution_schema = (
                InstitutionSchema(
                    id=destination_institution.id,
                    name=destination_institution.name,
                    created_at=destination_institution.created_at,
                )
                if destination_institution
                else None
            )

            return FinanceConfirmResponseSchema(
                category=category_schema,
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
                            ExtractedReceiptData.model_validate(
                                receipt_updated.extracted_data
                            )
                            if receipt_updated.extracted_data is not None
                            else None
                        ),
                        processing_status=receipt_updated.processing_status,
                    ),
                    created_at=payment.created_at,
                    beneficiary=beneficiary_schema,
                    payment_date=payment.payment_date,
                    source_institution=source_institution_schema,
                    destination_institution=destination_institution_schema,
                    category=category_schema,
                ),
                source_institution=source_institution_schema,
                destination_institution=destination_institution_schema,
            )
        except Exception as e:
            raise e

    async def update_payment(
        self,
        payment_id: str,
        payload: FinanceUpdatePaymentRequestSchema,
        user: User,
    ):
        try:

            payment =  await self.payment_service.find_by(id=payment_id, user_id=str(user.id))

            raw_payload: dict[str, object] = {}

            if payload.amount is not None:
                raw_payload["amount"] = payload.amount

            if payload.payment_date is not None:
                raw_payload["payment_date"] = payload.payment_date

            if payload.beneficiary is not None:
                beneficiary = await self.beneficiary_service.resolve(
                    name=payload.beneficiary
                )
                raw_payload["beneficiary_id"] = beneficiary.id

            if payload.category is not None:
                category = await self.category_service.resolve(
                    user_id=user.id,
                    name=payload.category
                )
                raw_payload["category_id"] = category.id

            if  payload.source_institution is not None:
                source_institution = await self.institution_service.resolve(
                    name=payload.source_institution
                )
                raw_payload["source_institution_id"] = source_institution.id

            if  payload.destination_institution is not None:
                destination_institution = await self.institution_service.resolve(
                    name=payload.destination_institution
                )
                raw_payload["destination_institution_id"] = destination_institution.id

            if not raw_payload:
                return payment

            updated_payment = await self.payment_service.update_payment(
                payment_id=payment_id, payload=raw_payload, user=user
            )

            payment.receipt = await self.receipt_service.update_receipt_payment(
                user=user,
                receipt_id=updated_payment.receipt.id,
                payload={
                    "payer": payload.payer,
                    "category": updated_payment.category.name,
                    "paid_amount": updated_payment.amount,
                    "beneficiary": updated_payment.beneficiary.name,
                    "payment_date": updated_payment.payment_date,
                    "source_institution": updated_payment.source_institution.name,
                    "destination_institution": updated_payment.destination_institution.name
                    if updated_payment.destination_institution
                    else None,
                },
            )
            return updated_payment
        except Exception as e:
            raise e
