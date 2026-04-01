from datetime import datetime
from beanie import PydanticObjectId
from app.core.base_schema import MongoBaseSchema
from app.modules.payments.models import PaymentStatus

class PaymentCreate(MongoBaseSchema):
    amount: float

class PaymentRead(MongoBaseSchema):
    id: PydanticObjectId
    client_id: PydanticObjectId
    amount: float
    qr_code_data: str | None = None
    status: PaymentStatus
    generated_by_id: PydanticObjectId
    verified_by_id: PydanticObjectId | None = None
    created_at: datetime
    verified_at: datetime | None = None

class InvoiceSendResponse(MongoBaseSchema):
    success: bool
    message: str
