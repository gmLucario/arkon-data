from aiohttp import ClientSession
import asyncio
import os

from google.transit import gtfs_realtime_pb2
from unidecode import unidecode
from datetime import datetime
from typing import Dict

from models.mb import MetroBusRaw, MetroBus, MbPositionRecordDetails
from models.alcal import MbUnitHistory
from models.repository import ApiRepository


async def get_mb_records(s: ClientSession) -> MetroBus:
    """
    Get records from MB api
    """
    date_updated = datetime.now()
    feed = gtfs_realtime_pb2.FeedMessage()

    async with s.get(url=os.getenv("URL_API_MB")) as response:
        response.encoding = "utf-8"

        if response.status != 200:
            return

        feed.ParseFromString(await response.read())
        for entity in feed.entity:
            yield MetroBusRaw(
                vehicle_id=entity.vehicle.vehicle.id,
                vehicle_label=entity.vehicle.vehicle.label,
                vehicle_status=entity.vehicle.current_status,
                date_updated=date_updated,
                position_latitude=entity.vehicle.position.latitude,
                position_longitude=entity.vehicle.position.longitude,
            )


async def get_human_address(s: ClientSession, lat: float, lon: float) -> Dict[str, str]:
    """
    Get address based on (lat, lon)
    """
    result = {"full_add": None, "delegacion": None}

    async with s.get(
        url=os.getenv("URL_GEO_REVERSE"), params={"format": "json", "lat": lat, "lon": lon}
    ) as response:
        if response.status != 200:
            return result

        add_info = await response.json()
        result.update({"full_add": add_info.get("display_name")})

    async with s.get(
        url=f'{os.getenv("URL_API_POSTCODE")}{add_info.get("address").get("postcode")}',
        params={
            "type": "simplified",
            "token": os.getenv("URL_API_POSTCODE_KEY"),
        },
    ) as response:
        if response.status != 200:
            return result

        cdmx_info = await response.json()
        if not cdmx_info.get("error", False):
            result.update({"delegacion": cdmx_info.get("response").get("municipio")})

    return result


async def update_mb():
    """
    Update collection of metrobuses
    """
    repo = ApiRepository()
    repo.set_collection(collection="mb_units", index_fields=("vehicle_id",))

    async with ClientSession() as s:
        async for mb_raw in get_mb_records(s):
            await repo.update_or_insert(
                MetroBus(
                    vehicle_id=mb_raw.vehicle_id,
                    vehicle_label=mb_raw.vehicle_label,
                    vehicle_status=mb_raw.vehicle_status,
                ),
                filters={"vehicle_id": mb_raw.vehicle_id},
            )


async def up_mb_pos_alcal_mb():
    """
    Update collection of metrobus locations
    """
    repo = ApiRepository()

    async with ClientSession() as s:
        async for mb_raw in get_mb_records(s):

            add_info = await get_human_address(
                s=s, lat=mb_raw.position_latitude, lon=mb_raw.position_longitude
            )

            repo.set_collection(collection="mb_units_pos", index_fields=("vehicle_id",))
            await repo.update_list_by(
                filters={"vehicle_id": mb_raw.vehicle_id},
                elements_push=[
                    MbPositionRecordDetails(
                        position=(mb_raw.position_latitude, mb_raw.position_longitude),
                        datetime_record=mb_raw.date_updated,
                        full_address=add_info.get("full_add"),
                        alcaldia_name=add_info.get("delegacion"),
                    )
                ],
                tag="position_records",
            )

        repo.set_collection(collection="alcal_mb", index_fields=("name",))

        alcal_name = (add_info.get("delegacion") or "NOT_FOUND").replace(".", "")
        alcal_name = unidecode(alcal_name)
        alcal_name = alcal_name.upper()

        await repo.update_list_by(
            filters={"name": alcal_name},
            elements_push=[
                MbUnitHistory(
                    vehicle_id=mb_raw.vehicle_id,
                    datetime_record=mb_raw.date_updated,
                )
            ],
            tag="mb_units_history",
        )
