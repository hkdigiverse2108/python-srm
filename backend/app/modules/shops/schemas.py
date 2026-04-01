from datetime import datetime
from beanie import PydanticObjectId
from app.core.base_schema import MongoBaseSchema
from app.modules.shops.models import MasterPipelineStage

class ShopBase(MongoBaseSchema):
    name: str
    address: str | None = None
    contact_person: str | None = None
    phone: str | None = None
    email: str | None = None
    source: str | None = "Other"
    project_type: str | None = None
    requirements: str | None = None
    area_id: PydanticObjectId | None = None
    pipeline_stage: MasterPipelineStage | None = MasterPipelineStage.LEAD
    owner_id: PydanticObjectId | None = None


class ShopCreate(ShopBase):
    pass


class ShopUpdate(MongoBaseSchema):
    name: str | None = None
    address: str | None = None
    contact_person: str | None = None
    phone: str | None = None
    email: str | None = None
    source: str | None = None
    project_type: str | None = None
    requirements: str | None = None
    area_id: PydanticObjectId | None = None
    pipeline_stage: MasterPipelineStage | None = None
    owner_id: PydanticObjectId | None = None
    project_manager_id: PydanticObjectId | None = None
    demo_stage: int | None = None
    demo_scheduled_at: datetime | None = None


class AssignPMRequest(MongoBaseSchema):
    pm_id: PydanticObjectId
    demo_scheduled_at: datetime | None = None


class AssignedUser(MongoBaseSchema):
    id: PydanticObjectId
    name: str | None = None
    role: str | None = None


class ShopRead(ShopBase):
    id: PydanticObjectId
    owner_name: str | None = None
    area_name: str | None = None
    created_at: datetime
    is_archived: bool | None = False
    archived_by_id: PydanticObjectId | None = None
    archived_by_name: str | None = None
    created_by_id: PydanticObjectId | None = None
    created_by_name: str | None = None
    assignment_status: str | None = "UNASSIGNED"
    assigned_users: list[AssignedUser] = []
    last_visitor_name: str | None = None
    last_visit_status: str | None = None
    project_manager_id: PydanticObjectId | None = None
    project_manager_name: str | None = None
    pm_name: str | None = None
    assigned_pm_name: str | None = None
    scheduled_by_id: PydanticObjectId | None = None
    scheduled_by_name: str | None = None
    demo_stage: int | None = 0
    demo_scheduled_at: datetime | None = None
    demo_title: str | None = None
    demo_type: str | None = None
    demo_notes: str | None = None
    demo_meet_link: str | None = None
    # Client sync fields (populated at runtime by _overlay_client_data)
    client_id: PydanticObjectId | None = None
    client_organization: str | None = None
    onboarding_pm_id: PydanticObjectId | None = None
    onboarding_pm_name: str | None = None
