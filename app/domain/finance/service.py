from app.domain.finance.beneficiary.schema import BeneficiarySchema
from app.domain.finance.beneficiary.service import BeneficiaryService
from app.domain.finance.institution.schema import InstitutionSchema
from app.domain.finance.payment.schema import PaymentSchema
from app.domain.finance.payment.service import PaymentService
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

            await self.receipt_service.confirm_receipt(receipt=receipt, payload=payload.model_dump(mode="json"))

            return FinanceConfirmResponseSchema(
                beneficiary=BeneficiarySchema(id=beneficiary.id, name=beneficiary.name),
                payment=PaymentSchema(
                    id=payment.id,
                    amount=payment.amount,
                    payment_date=payment.payment_date,
                ),
                source_institution=InstitutionSchema(
                    id=source_institution.id, name=source_institution.name
                ),
                destination_institution=InstitutionSchema(
                    id=destination_institution.id, name=destination_institution.name
                )
                if destination_institution
                else None,
            )
        except Exception as e:
            raise e
