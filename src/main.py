from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from routes.mb import mb_router
from routes.alcal import mb_alcal
from tasks.update_records import update_mb, up_mb_pos_alcal_mb


app = FastAPI(
    title="ArkonDataProjectExample",
    description="Endpoints for backend vacancie",
    version="0.0.1",
)

app.scheduler = AsyncIOScheduler()


# Routes
app.include_router(mb_router)
app.include_router(mb_alcal)

# Jobs
app.scheduler.add_job(update_mb, "interval", minutes=15, max_instances=5)
app.scheduler.add_job(up_mb_pos_alcal_mb, "interval", minutes=15, max_instances=5)
app.scheduler.start()
