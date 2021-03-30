from fastapi import APIRouter
from typing import List
from datetime import datetime

from models.repository import ApiRepository
from models.mb import MetroBus, MbPositionRecordDetails

from handlers.mb_h import mb_response_serializer


repo = ApiRepository()

mb_router = APIRouter(
    prefix="/mb",
    tags=["metrobus"],
    responses={404: {"description": "Not found"}},
)


@mb_router.get(
    "/",
    response_description="Get all the metrobuses",
    status_code=200,
    response_model=List[MetroBus],
)
async def get_mb_bus(page: int, results_per_page: int):
    repo.set_collection(collection="mb_units", index_fields=("vehicle_id",))

    cursor = repo.fetch_records(
        filters={},
        sortby_params=[("vehicle_id", 1)],
        skip=(results_per_page * (page - 1)),
        limit=results_per_page,
    )

    return [
        mb_response_serializer(document)
        for document in await cursor.to_list(length=100)
    ]


@mb_router.get(
    "/position-history",
    response_description="Get history mb unit positions",
    status_code=200,
    response_model=List[MbPositionRecordDetails],
)
async def get_mb_bus_pos_history(mb_id: int, start_date: datetime, end_date: datetime):
    repo.set_collection(collection="mb_units_pos", index_fields=("vehicle_id",))

    cursor = repo.fetch_records_aggregate(
        filters_list=[
            {"$match": {"vehicle_id": mb_id}},
            {
                "$project": {
                    "_id": False,
                    "posHistory": {
                        "$filter": {
                            "input": "$position_records",
                            "as": "item",
                            "cond": {
                                "$and": [
                                    {"$gte": ["$$item.datetime_record", start_date]},
                                    {"$lte": ["$$item.datetime_record", end_date]},
                                ]
                            },
                        }
                    },
                }
            },
        ]
    )

    return [
        MbPositionRecordDetails(**record)
        for posHist in await cursor.to_list(length=100)
        for record in posHist.get("posHistory")
    ]