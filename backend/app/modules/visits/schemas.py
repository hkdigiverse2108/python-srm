import datetime
from beanie import PydanticObjectId
from app.core.base_schema import MongoBaseSchema
from app.modules.visits.models import VisitStatus

class VisitBase(MongoBaseSchema):
    shop_id: PydanticObjectId
    status: VisitStatus | None = VisitStatus.SATISFIED
    remarks: str | None = None
    decline_remarks: str | None = None
    visit_date: datetime.datetime | None = None
    duration_seconds: int | None = 0

class VisitCreate(VisitBase):
    pass

class VisitUpdate(MongoBaseSchema):
    status: VisitStatus | None = None
    remarks: str | None = None
    decline_remarks: str | None = None
    visit_date: datetime.datetime | None = None

class VisitRead(VisitBase):

    id: PydanticObjectId
    user_id: PydanticObjectId
    shop_name: str | None = None
    area_name: str | None = None
    user_name: str | None = None
    photo_url: str | None = None  # Legacy/fallback
    storefront_photo_url: str | None = None
    selfie_photo_url: str | None = None
    project_manager_name: str | None = None
    shop_status: str | None = None
    shop_demo_stage: int | None = 0
    created_at: datetime.datetime
    updated_at: datetime.datetime

