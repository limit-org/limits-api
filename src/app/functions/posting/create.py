import psycopg2
from ..dbconfig import config
import time
from functions.log import logErrorToDB
from fastapi import HTTPException
import traceback


async def makepost(textcontent, attachedmedia, posttopic, username, sessionkey):
    # start timer
    task_start_time = time.time()

    try:
        conn = psycopg2.connect(config())

        with conn.cursor() as cur:
            cur.execute(
                "SELECT (sessioncookie) FROM users WHERE username = %s",
                (username,)
            )
            sessioncookie = cur.fetchone()

            if sessioncookie is None:
                time_task_took = time.time() - task_start_time
                return {
                    "detail": {
                        "APImessage": "failure",
                        "UIMessage": "That user does not exist.",
                        "username": username,
                        "attempt_time": int(str(time.time()).split(".")[0]),
                    },
                    "time_took": time_task_took,
                    "error_code": 0
                }

            else:  # user exists

                if sessioncookie[0] == sessionkey:  # correct sesh key
                    time_task_took = time.time() - task_start_time

                    # get user id
                    cur.execute(
                        "SELECT (userid) FROM users WHERE username=%s",
                        (username,)
                    )
                    userid = cur.fetchone()

                    # find the highest post id
                    cur.execute("SELECT MAX(id) FROM posts")
                    highest_id = cur.fetchone()[0] or 0

                    # upload media to cock db
                    cur.execute(
                        "INSERT INTO posts (id, authorid, textcontent, attachedmedia, unixtimestamp, topic) "
                        "VALUES (%s, %s, %s, %s, %s, %s)",
                        ((highest_id + 1), userid, textcontent, attachedmedia,
                         int(str(time.time()).split(".")[0]), posttopic)
                    )
                    conn.commit()

                    return {
                        "detail": {
                            "APImessage": "success",
                            "UIMessage": "Post uploaded!",
                            "username": username,
                            "attempt_time": int(str(time.time()).split(".")[0]),
                        },
                        "time_took": time_task_took,
                        "error_code": 0
                    }

                else:  # session is wrong
                    time_task_took = time.time() - task_start_time
                    return {
                        "detail": {
                            "APImessage": "failure",
                            "error": "Invalid session key.",
                            "UIMessage": "Invalid session key.",
                            "username": username,
                            "attempt_time": int(str(time.time()).split(".")[0]),
                        },
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
                "error": "Post creation error.",
                "time_took": time_task_took
            }
        )
