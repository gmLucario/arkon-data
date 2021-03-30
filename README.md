# Content
1. [Requerimientos](#requerimientos)
2. [Desarrollo](#desarrollo)
    1. [Entries Project](#useful_links)
    2. [Stack](#stack)
    3. [Links to useful docs](#links_docs)
    4. [About .env](#about_env_file)
3. [Create proyect locally](#create_proyect_locally)



## Requerimientos
<p>
Utilizando los datos abiertos de la Ciudad de México correspondientes a la ubicación de las unidades del metrobús durante la última hora para obtener un histórico de la posición en la que se encuentra cada unidad que pueda ser consultado mediante un API Rest filtrando por unidad o por alcaldía.
</p>

**EndPoints Requeridos:**
- [X] Obtener una lista de unidades disponibles, de las que se tiene registro.
- [X] Consultar el/los historial de ubicaciones/fechas de una unidad dado su ID
- [X] Obtener una lista de alcaldías disponibles
    - Se entiende que alcaldías con unidades
- [X] Obtener una lista de unidades que hayan estado dentro de una alcaldía

## Desarrollo

### Useful_links
Description | Link 
--- | --- 
MONGOExpress | http://127.0.0.1:20048/
SWAGGER_DOC | http://127.0.0.1:8000/docs


### stack
- [fastAPI](https://fastapi.tiangolo.com/)
    - Pydantic
    - uvicorn
- AsyncIOMotorClient
- docker y docker-compose
- git  

### links_docs
- [Datos MB](https://datos.cdmx.gob.mx/organization/metrobus)
- [GTFS Google example py](https://developers.google.com/transit/gtfs-realtime/examples/python-sample)
- [Noticia Cooperación](https://www.metrobus.cdmx.gob.mx/portal-ciudadano/datos-abiertos)
- [Google reverse decoding about](https://developers.google.com/maps/documentation/geocoding/start#reverse)
- [Reverse decoding](https://nominatim.openstreetmap.org)
- [Post Code Info CDMX](https://api-sepomex.hckdrk.mx/query/info_cp/)


#### Example response GTFS mb
```json
{

    "id": "170",
    "vehicle": {
        "trip": {
            "trip_id": "10999597",
            "start_time": "13:15:00",
            "start_date": "20210328",
            "schedule_relationship": 1,//SCHEDULED
            "route_id": "437"
        },
        "position": {
            "latitude": 19.507200241088867,
            "longitude": -99.08599853515625,
            "bearing": 0.0,
            "odometer": 0.0,
            "speed": 0.0
        }
    },
    "current_stop_sequence": 1,
    "current_status": 0, //STOPPED_AT
    "timestamp": 1616958827,
    "congestion_level": 0,//UNKNOWN_CONGESTION_LEVEL,
    "stop_id": "501",
    "vehicle": {
        "id": "1304",
        "label": "2602"
    }

}
```

### About_env_file
Change .env_example for your own .env
```
MONGO_USER=usuario_mongo
MONGO_PASSWORD=mongo_password
MONGO_HOST=host_of_mongo
MONGO_PORT=27017
DB_NAME=metrobus_track_db
DB_TYPE=mongodb
URL_API_MB=http://your_own_url_after_filled_form
URL_API_POSTCODE=https://api-sepomex.hckdrk.mx/query/info_cp/
URL_API_POSTCODE_KEY=your_key_api
URL_GEO_REVERSE=https://nominatim.openstreetmap.org/reverse
```

## Create_proyect_locally
Firts you must have your .env with the right env values

1. create image
```sh
docker build --no-cache -t arkon-app:dev .
```

2. Up docker compose
```sh
docker-compose \
 -f docker-compose.yml \
 --env-file .env \
up $@
```

3. Kill docker-compose
```sh
docker-compose \
 -f docker-compose.yml \
kill $@
docker-compose \
 -f docker-compose.yml \
down $@
```