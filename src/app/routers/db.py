from fastapi import APIRouter, Request

from functions.db import returnVersion

router = APIRouter()


@router.get("/db/version", tags=["db"])
async def get_db_version():
    # return returnVersion()
    return "This endpoint is potentially dangerous in a production environment: It has been disabled."
