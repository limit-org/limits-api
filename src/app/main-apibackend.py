from fastapi import FastAPI
from loguru import logger

from routers import db
from routers import users
from routers import media
from routers import posts

# init logging
# logger.add("file_{time}.log", rotation="1GB", enqueue=True)  # makes log files
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

app.include_router(
    media.router,
    tags=["media"]
)

app.include_router(
    posts.router,
    tags=["posts"]
)


@app.get("/", tags=["index"])
async def index_show_paths():
    return "index."
