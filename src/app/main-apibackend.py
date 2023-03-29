import time

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import meilisearch
import uvicorn

from routers import db
from routers import users
from routers import media
from routers import posts
from routers import search
from routers import profilepic

from functions.dbconfig import meilisearchConfig

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
async def index() -> RedirectResponse:
    return RedirectResponse(url="/heartbeat")


@app.get("/heartbeat", tags=["heartbeat"])
async def heartbeat():
    return "API Online"

if __name__ == "__main__":
    # test if we can connect to meilisearch first
    # get keys for ms
    msdb = meilisearchConfig(filename='database.ini')[0]
    msdbkey = meilisearchConfig(filename='database.ini')[1]
    client = meilisearch.Client(msdb, msdbkey)
    try:
        print(f"""
        |=======================================================================|
        |  MEILISEARCH DATABASE HEALTH: {str(client.health())}                 |
        |  CONNECTION ESTABLISHED TO MEILISEARCH.                               |
        |  STARTING THE LimitsForum BACKEND AT {time.asctime()}.        |
        |    _      _           _ _       ______                                |
        |   | |    (_)         (_| |     |  ____|                               |
        |   | |     _ _ __ ___  _| |_ ___| |__ ___  _ __ _   _ _ __ ___         |
        |   | |    | | '_ ` _ \| | __/ __|  __/ _ \| '__| | | | '_ ` _ \        |
        |   | |____| | | | | | | | |_\__ | | | (_) | |  | |_| | | | | | |       |
        |   |______|_|_| |_| |_|_|\__|___|_|  \___/|_|   \__,_|_| |_| |_|       |
        |=======================================================================|""")

    except Exception as err:
        print("|=======================================================================|\n"
              "|  CANNOT CONNECT TO MEILISEARCH DATABASE.                              |\n"
              "|  APPLICATION WILL NOT START UNTIL A CONNECTION CAN BE ESTABLISHED.    |\n"
              "|  ERROR: Could not establish a Meilisearch database connection.        |\n"
              "|=======================================================================|\n")
        exit(1)

    # if it works, continue and run app.
    uvicorn.run("main-apibackend:app", host="127.0.0.1", port=8000,
                reload=True)  # false if running in prod.
