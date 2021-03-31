from pydantic import BaseModel
from pymongo import ASCENDING, ReturnDocument
from typing import List, Tuple, Dict, Any, Optional
import os
import motor.motor_asyncio


def _make_url(db_config: dict):
    """
    Return the url to connect to mongo
    """
    url = db_config.get("type")
    url += f'://{db_config.get("user")}'
    url += f':{db_config.get("password")}'
    url += f'@{db_config.get("host")}'
    url += f':{db_config.get("port")}'

    return url


class ApiRepository:
    """
    Methods that interact with the db
    """

    def __init__(self):
        client = motor.motor_asyncio.AsyncIOMotorClient(
            _make_url(
                db_config={
                    "type": os.getenv("DB_TYPE"),
                    "host": os.getenv("MONGO_HOST"),
                    "user": os.getenv("MONGO_USER"),
                    "password": os.getenv("MONGO_PASSWORD"),
                    "port": os.getenv("MONGO_PORT"),
                    "db": os.getenv("DB_NAME"),
                }
            )
        )

        self._db = client[os.getenv("DB_NAME")]

    def set_collection(self, collection: str, index_fields: Tuple[str] = ()) -> None:
        """
        Set the collection in the mongodb that will be affected
        """
        self._collection = self._db[collection]
        self._collection.create_index([(index, ASCENDING) for index in index_fields], unique=True)

    def find_one(self, filters: dict) -> bool:
        """
        Find a single document based on filters
        """
        return self._collection.find_one(filters)

    async def update_or_insert(self, obj_to_save: BaseModel, filters: dict):
        """
        Create or update a document based on filters
        """
        return await self._collection.find_one_and_update(
            filters, {"$set": obj_to_save.dict()}, upsert=True, return_document=ReturnDocument.AFTER
        )

    async def update_list_by(self, filters: dict, elements_push: List[BaseModel], tag: str):
        """
        Add new elements to a list field of a document found it byfilters
        """
        return await self._collection.find_one_and_update(
            filters,
            {"$addToSet": {tag: {"$each": [o.dict() for o in elements_push]}}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

    def fetch_records(
        self,
        filters: Dict[str, Any],
        sortby_params: List[Tuple[str, int]] = None,
        skip: int = 0,
        limit: int = 0,
    ):
        """
        Return many documents paginated
        """
        if not sortby_params:
            return self._collection.find(filters).limit(limit).skip(skip)

        return self._collection.find(filters).sort(sortby_params).limit(limit).skip(skip)

    def fetch_records_fields(self, filters: Dict[str, Any], fields: Optional[Dict[str, Any]]):
        """
        Return only specific fields of many documents by filters
        """        
        if not fields:
            return self._collection.find(filters)

        return self._collection.find(filters, fields)

    def fetch_records_aggregate(
        self,
        filters_list: List[Dict[str, Any]],
    ):
        """
        Return many documents by aggregate
        """
        return self._collection.aggregate(filters_list)
