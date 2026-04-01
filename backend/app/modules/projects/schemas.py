import datetime
import typing
from pydantic import ConfigDict
from beanie import PydanticObjectId
from app.core.base_schema import MongoBaseSchema
from app.modules.issues.models import GlobalTaskStatus

class ProjectBase(MongoBaseSchema):
    name: str
    description: str | None = None
    client_id: PydanticObjectId
    pm_id: PydanticObjectId
    status: GlobalTaskStatus | None = GlobalTaskStatus.OPEN
    start_date: datetime.datetime | None = None
    end_date: datetime.datetime | None = None
    budget: float | None = 0.0
    model_config = ConfigDict(from_attributes=True)


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(MongoBaseSchema):
    name: str | None = None
    description: str | None = None
    pm_id: PydanticObjectId | None = None
    status: GlobalTaskStatus | None = None
    start_date: datetime.datetime | None = None
    end_date: datetime.datetime | None = None
    budget: float | None = None


class ProjectRead(ProjectBase):
    id: PydanticObjectId
    created_at: datetime.datetime
    updated_at: datetime.datetime

    # Extra names and contact info for UI
    client_name: str | None = None
    pm_name: str | None = None
    contact_person: str | None = None
    phone: str | None = None
    email: str | None = None
    project_type: str | None = None

    # Progress metrics (calculated in service)
    total_issues: int | None = 0
    resolved_issues: int | None = 0
    progress_percentage: float | None = 0.0
