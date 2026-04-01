# backend/app/modules/settings/models.py
from typing import Dict, Any, Optional, Union, List
from beanie import Document, Indexed
from pydantic import Field

class SystemSettings(Document):
    feature_flags: Dict[str, Any] = Field(default_factory=dict)
    access_policy: Dict[str, Any] = Field(default_factory=dict)
    policy_version: int = 1
    delete_policy: Optional[str] = "SOFT"

    class Settings:
        name = "system_settings"

class AppSetting(Document):
    key: Indexed(str, unique=True)
    value: Union[str, List[Any], Dict[str, Any], int, float]

    class Settings:
        name = "app_settings"
