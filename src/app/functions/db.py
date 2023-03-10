import psycopg2
from .dbconfig import config
import time
from functions.log import logErrorToDB
from fastapi import HTTPException
import traceback


# this func. returns the version of the sql database.
# good for testing if this works.
async def returnVersion():
    # start timer
    task_start_time = time.time()

    """ Connect to the PostgreSQL database server """
    try:
        conn = psycopg2.connect(config())

        with conn.cursor() as cur:
            cur.execute("SELECT version()")  # execute this command in the database
            db_version = cur.fetchall()

        # calculate time taken to do the thing
        time_task_took = time.time() - task_start_time
        return {
            "db_version": str(db_version),
            "time_took": time_task_took,
            "error_code": 0
        }

    except (Exception, psycopg2.DatabaseError):
        time_task_took = time.time() - task_start_time
        await logErrorToDB(str(traceback.format_exc()), timetaken=time_task_took)
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "1",
                "http_code": "500",
                "error": "Database communication error.",
                "time_took": time_task_took
            }
        )
