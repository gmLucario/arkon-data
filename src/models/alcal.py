from pydantic import BaseModel
from typing import List
from datetime import datetime


class MbUnitHistory(BaseModel):
    vehicle_id: int
    datetime_record: datetime


class Alcaldia(BaseModel):
    name: str
    updated_at: datetime