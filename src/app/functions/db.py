import psycopg2
from .dbconfig import config
from functions.log import logErrorToDB
from fastapi import HTTPException
import traceback


# this func. returns the version of the sql database.
# good for testing if this works.
async def returnVersion():
    try:
        conn = psycopg2.connect(config())

        with conn.cursor() as cur:
            cur.execute("SELECT version()")  # execute this command in the database
            db_version = cur.fetchall()

        return {
            "db_version": str(db_version),
            "error_code": 0
        }

    except (Exception, psycopg2.DatabaseError):
        await logErrorToDB(str(traceback.format_exc()))
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "1",
                "http_code": "500",
                "error": "Database communication error.",
            }
        )
