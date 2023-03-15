from fastapi import APIRouter

from functions.db import returnVersion

router = APIRouter()


@router.get("/db/version", tags=["db"], status_code=200)
async def get_db_version():
    return await returnVersion()
    # return "This endpoint is potentially dangerous in a production environment: It has been disabled."
