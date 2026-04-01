# backend/app/modules/attendance/models.py
from typing import Optional
import datetime as dt
from datetime import datetime, UTC, date as dt_date # Rename imported date to avoid clash
from pydantic import Field
from beanie import Document, Indexed, PydanticObjectId

class Attendance(Document):
    user_id: PydanticObjectId
    date: dt_date = Field(default_factory=lambda: datetime.now(UTC).date())
    punch_in: Optional[datetime] = None
    punch_out: Optional[datetime] = None
    total_hours: float = 0.0
    is_deleted: bool = False

    class Settings:
        name = "attendance"
