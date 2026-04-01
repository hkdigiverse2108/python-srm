from typing import Dict, Any
from beanie import PydanticObjectId
from app.core.base_schema import MongoBaseSchema

class SystemSettingsRead(MongoBaseSchema):
    id: PydanticObjectId
    feature_flags: Dict[str, Any]
    access_policy: Dict[str, Any] = {}

class SystemSettingsUpdate(MongoBaseSchema):
    feature_flags: Dict[str, Any] | None = None
    access_policy: Dict[str, Any] | None = None
