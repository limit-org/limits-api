import psycopg2
from ..dbconfig import config
import time
from functions.log import logErrorToDB
from fastapi import HTTPException
import traceback
from ..istrustedormod import checkTORM
from ..meilisearch.MSIndex import IndexPost


async def makepost(posttitle, textcontent, attachedmedia, posttopic, username, sessionkey):
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

                    # is user allowed to post?
                    cur.execute(
                        "SELECT (allowedtopost) FROM users WHERE username=%s",
                        (username,)
                    )
                    allowedtopost = cur.fetchone()

                    if not allowedtopost[0]:
                        time_task_took = time.time() - task_start_time
                        return {
                            "detail": {
                                "APImessage": "failure",
                                "error": "User not allowed to post.",
                                "UIMessage": "You're not allowed to post on limits.",
                                "username": username,
                                "attempt_time": int(str(time.time()).split(".")[0]),
                            },
                            "time_took": time_task_took,
                            "error_code": 0
                        }

                    # if the user is trying to post in the meta/news topic, check that they're allowed to
                    if posttopic == "meta/news":
                        TORM = checkTORM(username)
                        if TORM == 1:  # not trusted or a mod
                            return {
                                "detail": {
                                    "APImessage": "failure",
                                    "error": "Invalid post topic.",
                                    "UIMessage": "You're not allowed to post in this topic.",
                                    "username": username,
                                    "attempt_time": int(str(time.time()).split(".")[0]),
                                },
                                "time_took": time_task_took,
                                "error_code": 0
                            }

                    # if continuing, they are allowed to post here.
                    # get user id
                    cur.execute(
                        "SELECT (userid) FROM users WHERE username=%s",
                        (username,)
                    )
                    userid = cur.fetchone()

                    # find the highest post id
                    cur.execute("SELECT MAX(id) FROM posts")
                    highest_id = cur.fetchone()[0] or 0

                    # get timestamp
                    uploadtimestamp = int(str(time.time()).split(".")[0])

                    # upload to cock db
                    cur.execute(
                        "INSERT INTO posts (id, authorid, textcontent, attachedmedia, unixtimestamp, topic, posttitle) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        ((highest_id + 1), userid, textcontent, attachedmedia,
                         uploadtimestamp, posttopic, posttitle)
                    )
                    conn.commit()

                    # upload to meilisearch
                    await IndexPost((highest_id + 1), userid, username, posttitle, textcontent, attachedmedia,
                                    uploadtimestamp, posttopic, edited=False)

                    return {
                        "detail": {
                            "APImessage": "success",
                            "UIMessage": "Post uploaded!",
                            "postid": (highest_id + 1),
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
        await logErrorToDB(str(traceback.format_exc()))
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "1",
                "http_code": "500",
                "error": "Post creation error.",
                "time_took": time_task_took
            }
        )
