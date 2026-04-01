import datetime
import typing
from pydantic import BaseModel
from app.core.base_schema import MongoBaseSchema

class IDCardData(BaseModel):
    employee_name: str
    employee_code: str
    role: str
    joining_date: datetime.date
    photo_url: typing.Optional[str] = None
    qr_data: str
