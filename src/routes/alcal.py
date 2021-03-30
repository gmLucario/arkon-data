from fastapi import APIRouter
from typing import List
from datetime import datetime

from models.repository import ApiRepository
from models.mb import MetroBusByAlRes


repo = ApiRepository()

mb_alcal = APIRouter(
    prefix="/alcal",
    tags=["alcaldias"],
    responses={404: {"description": "Not found"}},
)


@mb_alcal.get(
    "/",
    response_description="Get all the alcaldias",
    status_code=200,
    response_model=List[str],
)
async def get_all_alcal():
    repo.set_collection(collection="alcal_mb", index_fields=("name",))

    cursor = repo.fetch_records_fields(
        filters={"name": {"$ne": "NOT_FOUND"}},
        fields={"_id": False, "mb_units_history": False},
    )

    return [doc.get("name") for doc in await cursor.to_list(length=100)]


@mb_alcal.get(
    "/units",
    response_description="Get mb units by alcaldia",
    status_code=200,
    response_model=List[MetroBusByAlRes],
)
async def get_units_by_alcal(alcal_name: str, start_date: datetime, end_date: datetime):
    repo.set_collection(collection="alcal_mb", index_fields=("name",))

    cursor = repo.fetch_records_aggregate(
        filters_list=[
            {"$match": {"name": alcal_name}},
            {
                "$project": {
                    "_id": False,
                    "units_history": {
                        "$filter": {
                            "input": "$mb_units_history",
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
        MetroBusByAlRes(**record)
        for unit in await cursor.to_list(length=100)
        for record in unit.get("units_history")
    ]
