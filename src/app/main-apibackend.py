from fastapi import FastAPI

import uvicorn

from routers import db
from routers import users
from routers import media
from routers import posts
from routers import search
from routers import profilepic


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

app.include_router(
    search.router,
    tags=["search"]
)

app.include_router(
    profilepic.router,
    tags=["profilepic"]
)


@app.get("/", tags=["index"])
async def index_show_paths():
    return "index."
