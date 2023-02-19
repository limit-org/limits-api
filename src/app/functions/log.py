import time
from loguru import logger
import psycopg2
from .dbconfig import config


def logErrorToDB(errortext: str):  # log any server side errors to db
    unixtimestamp = int(str(time.time()).split(".")[0])  # if you want to reduce imports, use the timestamp of

    # replace empty string with "Unknown error"
    if not errortext:
        errortext = "Unknown error"

    try:
        conn = psycopg2.connect(config())
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO errorlogs (errormessage, unixtimestamp) VALUES (%s, %s)",
                (errortext.replace("''", "'"), unixtimestamp)
            )
            conn.commit()
            logger.info(f"Logged error to database. errormsg: {errortext}")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f"Error while logging error to database. errormsg: {error}")
