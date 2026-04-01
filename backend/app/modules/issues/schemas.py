from datetime import datetime
from beanie import PydanticObjectId
from app.core.base_schema import MongoBaseSchema
from app.modules.issues.models import GlobalTaskStatus, IssueSeverity

class IssueBase(MongoBaseSchema):
    title: str
    description: str | None = None
    status: GlobalTaskStatus = GlobalTaskStatus.OPEN
    severity: IssueSeverity = IssueSeverity.MEDIUM
    client_id: PydanticObjectId
    project_id: PydanticObjectId | None = None
    reporter_id: PydanticObjectId | None = None
    remarks: str | None = None
    opened_at: datetime | None = None


class IssueCreate(MongoBaseSchema):
    title: str
    description: str | None = None
    status: GlobalTaskStatus = GlobalTaskStatus.OPEN
    severity: IssueSeverity = IssueSeverity.MEDIUM
    project_id: PydanticObjectId | None = None
    assigned_to_id: PydanticObjectId | None = None
    assigned_group: str | None = None
    remarks: str | None = None


class IssueUpdate(MongoBaseSchema):
    title: str | None = None
    description: str | None = None
    status: GlobalTaskStatus | None = None
    severity: IssueSeverity | None = None
    remarks: str | None = None


class IssueAssign(MongoBaseSchema):
    assigned_to_id: PydanticObjectId


class IssueRead(IssueBase):
    id: PydanticObjectId
    assigned_to_id: PydanticObjectId | None = None
    assigned_group: str | None = None
    pm_name: str | None = None
    project_name: str | None = None
    created_at: datetime | None = None
    reporter_name: str | None = None
