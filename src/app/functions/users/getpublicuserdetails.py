import time
import csv
import psycopg2
from fastapi import HTTPException
import traceback

from ..dbconfig import config
from ..log import logErrorToDB


async def getpublicuserinfo(username):
    # start timer
    task_start_time = time.time()

    try:
        conn = psycopg2.connect(config())
        with conn.cursor() as cur:
            # check if username already exists
            cur.execute(
                "SELECT (userid, username, alias, unixtimejoined, bio, modnotes, trusted, moderator, badges, "
                "email, makeemailpublic, official) "
                "FROM users WHERE username = %s",
                (username,)
            )
            DBValue = cur.fetchone()

            if DBValue is not None:  # if username already exists in the db
                # calculate time taken to do the thing
                time_task_took = time.time() - task_start_time

                # Parse the string using the csv module
                reader = csv.reader(DBValue, delimiter=',', quotechar='"')
                # Extract the fields and convert them to a list
                fields = list(reader)[0]
                # Extract the individual values from the list
                user_id, username, alias, unixjoin, bio, modnotes, is_trusted, is_mod, badges, email, is_email_public, \
                    is_official = fields

                # Remove the parentheses from the first and last values
                user_id = user_id[1:]
                is_official = is_official[:-1]

                if is_email_public == "f":
                    email = "[REDACTED DUE TO USERS PRIVACY CHOICES.]"

                return {
                    "detail": {
                        "UIContents": {
                            "userid": user_id,
                            "username": username,
                            "alias": alias,
                            "unixtimejoined": unixjoin,
                            "bio": bio,
                            "is_trusted": is_trusted,
                            "moderation_notes": modnotes,
                            "is_mod": is_mod,
                            "badges": badges,
                            "email": email,
                            "is_email_public": is_email_public,
                            "official": is_official
                        },
                    },
                    "time_took": time_task_took,
                    "error_code": 0
                }
            else:
                time_task_took = time.time() - task_start_time
                return {
                    "detail": {
                        "error_code": "1",
                        "error": "User does not exist.",
                        "UIMessage": "That user does not exist.",
                        "time_took": time_task_took
                    }
                }

    except (Exception, psycopg2.DatabaseError):
        time_task_took = time.time() - task_start_time
        await logErrorToDB(str(traceback.format_exc()), timetaken=int(time_task_took))
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "1",
                "http_code": "500",
                "error": "SQL query error.",
                "time_took": time_task_took
            }
        )
