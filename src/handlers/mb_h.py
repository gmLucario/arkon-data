from models.mb import MetroBus


def mb_response_serializer(mongo_result: dict) -> MetroBus:
    if not mongo_result:
        return None

    keys_delete = ("_id",)
    [mongo_result.pop(k) for k in list(mongo_result) if k in keys_delete]

    return MetroBus(**mongo_result)
