from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.domain.finance.receipt.route import (
    get_receipt,
    received_receipt,
    receipt_service,
    received_receipt_batch,
)
from app.domain.finance.receipt.service import ReceiptService


class TestReceiptRoutes:
    @staticmethod
    def test_receipt_service_builds_service():
        service = receipt_service(AsyncMock())

        assert isinstance(service, ReceiptService)

    @staticmethod
    @pytest.mark.asyncio
    async def test_received_receipt_route_returns_service_result():
        service = AsyncMock()

        current_user = SimpleNamespace(
            id=uuid4(),
        )

        file = SimpleNamespace(
            filename="comprovante.pdf",
            content_type="application/pdf",
        )

        expected = SimpleNamespace(
            id=uuid4(),
        )

        service.received_receipt.return_value = expected

        result = await received_receipt(
            service=service,
            current_user=current_user,
            file=file,
        )

        assert result is expected

        service.received_receipt.assert_awaited_once_with(
            file=file,
            user=current_user,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_received_receipt_batch_route_returns_service_result():
        service = AsyncMock()

        current_user = SimpleNamespace(
            id=uuid4(),
        )

        file_1 = SimpleNamespace(
            filename="comprovante.pdf",
            content_type="application/pdf",
        )
        file_2 = SimpleNamespace(
            filename="comprovante.png",
            content_type="image/png",
        )
        file_3 = SimpleNamespace(
            filename="comprovante.jpeg",
            content_type="image/jpeg",
        )

        expected = SimpleNamespace(
            total=3,
            receipts=[
                SimpleNamespace(
                    id=uuid4(),
                    file_name=file_1.filename,
                    file_type=file_1.content_type,
                    file_size=12345,
                    processing_status="RECEIVED",
                ),
                SimpleNamespace(
                    id=uuid4(),
                    file_name=file_2.filename,
                    file_type=file_2.content_type,
                    file_size=67890,
                    processing_status="RECEIVED",
                ),
                SimpleNamespace(
                    id=uuid4(),
                    file_name=file_3.filename,
                    file_type=file_3.content_type,
                    file_size=13579,
                    processing_status="FAILED",
                ),
            ],
            failed=1,
            received=2,
        )

        service.received_receipt_batch.return_value = expected

        result = await received_receipt_batch(
            service=service,
            current_user=current_user,
            files=[file_1, file_2, file_3],
        )

        assert result is expected

        service.received_receipt_batch.assert_awaited_once_with(
            files=[file_1, file_2, file_3],
            user=current_user,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_receipt_route_returns_service_result():
        service = AsyncMock()

        receipt_id = "22222222-2222-2222-2222-222222222222"

        current_user = SimpleNamespace(
            id="11111111-1111-1111-1111-111111111111",
        )

        expected = SimpleNamespace(
            id=receipt_id,
        )

        service.get_receipt.return_value = expected

        result = await get_receipt(
            service=service,
            receipt_id=receipt_id,
            current_user=current_user,
        )

        assert result is expected

        service.get_receipt.assert_awaited_once_with(
            receipt_id=receipt_id,
            user=current_user,
        )
