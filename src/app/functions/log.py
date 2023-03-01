import time
from loguru import logger
import psycopg2
from .dbconfig import config


async def logErrorToDB(errortext: str, timetaken: int):  # log any server side errors to db
    # replace empty string with "Unknown error"
    if not errortext:
        errortext = "Unknown error"

    unixtime = int(str(time.time()).split(".")[0])

    try:
        conn = psycopg2.connect(config())
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO errorlogs (errormessage, unixtimestamp, timetook) VALUES (%s, %s, %s)",
                (errortext.replace("''", "'"), unixtime, timetaken)
            )
            conn.commit()
            logger.info(f"Logged error to database. errormsg: {errortext}")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f"Error while logging error to database. errormsg: {error}")
