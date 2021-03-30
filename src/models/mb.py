from pydantic import BaseModel
from typing import List, Optional, Tuple
from datetime import datetime
from enum import IntEnum


class VehicleStatusEnum(IntEnum):
    IN_TRANSIT_TO = 1
    STOPPED_AT = 2


class MetroBusRaw(BaseModel):
    vehicle_id: int
    vehicle_label: int
    vehicle_status: VehicleStatusEnum
    date_updated: datetime
    position_latitude: float
    position_longitude: float


class MetroBus(BaseModel):
    vehicle_id: int
    vehicle_label: int
    vehicle_status: VehicleStatusEnum


class MbPositionRecordDetails(BaseModel):
    position: Tuple[float, float]
    datetime_record: datetime
    full_address: Optional[str]
    alcaldia_name: Optional[str]


class MetroHistory(BaseModel):
    vehicle_id: int
    position_records: List[MbPositionRecordDetails]


class MetroBusByAlRes(BaseModel):
    vehicle_id: int
    datetime_record: datetime