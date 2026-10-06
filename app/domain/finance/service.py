from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.domain.finance.beneficiary.schema import BeneficiarySchema
from app.domain.finance.beneficiary.service import BeneficiaryService
from app.domain.finance.category.schema import CategorySchema
from app.domain.finance.category.service import CategoryService
from app.domain.finance.institution.schema import InstitutionSchema
from app.domain.finance.institution.service import InstitutionService
from app.domain.finance.payer.schema import PayerSchema
from app.domain.finance.payer.service import PayerService
from app.domain.finance.payment.schema import PaymentSchema
from app.domain.finance.payment.service import PaymentService
from app.domain.finance.receipt.schema import ReceiptSchema
from app.domain.finance.receipt.service import ReceiptService
from app.domain.finance.schema import (
    FinanceConfirmRequestSchema,
    FinanceUpdatePaymentRequestSchema,
)
from app.models import ProcessingStatusEnum, User

Session = Annotated[AsyncSession, Depends(get_session)]


class FinanceService:
    def __init__(
            self,
            session: Session,
            payer_service: PayerService | None = None,
            receipt_service: ReceiptService | None = None,
            payment_service: PaymentService | None = None,
            category_service: CategoryService | None = None,
            beneficiary_service: BeneficiaryService | None = None,
            institution_service: InstitutionService | None = None,
    ):
        self.session = session
        self.payer_service = payer_service or PayerService.from_session(session)
        self.receipt_service = receipt_service or ReceiptService.from_session(session)
        self.payment_service = payment_service or PaymentService.from_session(session)
        self.category_service = category_service or CategoryService.from_session(
            session
        )
        self.beneficiary_service = (
                beneficiary_service or BeneficiaryService.from_session(session)
        )
        self.institution_service = (
                institution_service or InstitutionService.from_session(session)
        )

    async def confirm(
            self, receipt_id: str, payload: FinanceConfirmRequestSchema, user: User
    ) -> PaymentSchema:
        try:
            receipt = await self.receipt_service.validate_confirm_receipt(
                receipt_id=receipt_id, user=user
            )
            await self.payment_service.check_receipt(receipt_id=receipt.id, user=user)
            await self.receipt_service.update_receipt_status(
                receipt=receipt,
                status=ProcessingStatusEnum.PROCESSING,
            )

            payer = await self.payer_service.resolve(
                name=payload.payer,
                user_id=user.id,
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
                payer_id=payer.id,
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

            return PaymentSchema(
                id=payment.id,
                payer=PayerSchema.model_validate(payer),
                amount=payment.amount,
                receipt=ReceiptSchema.model_validate(receipt_updated),
                category=CategorySchema.model_validate(category),
                created_at=payment.created_at,
                beneficiary=BeneficiarySchema.model_validate(beneficiary),
                payment_date=payment.payment_date,
                source_institution=InstitutionSchema.model_validate(source_institution),
                destination_institution=(
                    InstitutionSchema.model_validate(destination_institution)
                    if destination_institution
                    else None
                ),
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
            payment = await self.payment_service.find_by(
                id=payment_id, user_id=str(user.id)
            )

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
                    user_id=user.id, name=payload.category
                )
                raw_payload["category_id"] = category.id

            if payload.payer is not None:
                payer = await self.payer_service.resolve(
                    user_id=user.id, name=payload.payer
                )
                raw_payload["payer_id"] = payer.id

            if payload.source_institution is not None:
                source_institution = await self.institution_service.resolve(
                    name=payload.source_institution
                )
                raw_payload["source_institution_id"] = source_institution.id

            if payload.destination_institution is not None:
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
