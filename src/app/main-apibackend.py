from fastapi import FastAPI
from loguru import logger

from routers import db
from routers import users

# init logging
logger.add("file_{time}.log", rotation="1GB", enqueue=True)
logger.info("Logging initiated")
logger.warning("Starting application")

# init fastapi thingy
app = FastAPI()

app.include_router(
    db.router,
    tags=["db"]
)

app.include_router(
    users.router,
    tags=["user"]
)


@app.get("/", tags=["index"])
async def index_show_paths():
    return "index."
