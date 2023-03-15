import psycopg2
from ..dbconfig import config
import time
from functions.log import logErrorToDB
from fastapi import HTTPException
import traceback
from ..meilisearch.MSIndex import IndexPost


async def deletepost(postid, username, sessionkey):
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
                    # get user id
                    cur.execute(
                        "SELECT (userid) FROM users WHERE username=%s",
                        (username,)
                    )
                    userid = cur.fetchone()

                    # check if this post actually exists
                    cur.execute(
                        "SELECT (unixtimestamp, ) FROM posts WHERE id=%s",
                        (postid,)
                    )
                    if cur.fetchone() is not None:  # post exists
                        # get timestamp
                        deletedattimestamp = int(str(time.time()).split(".")[0])

                        redactedText = "[REDACTED DUE TO DELETION]"
                        # upload to cock db
                        cur.execute(
                            "UPDATE posts SET textcontent=%s, votes=%s, deleted=true, deletereason=%s, "
                            "attachedmedia=NULL, popularity=%s, topic=deleted, posttitle=%s, updatedat=%s, "
                            "deletedat=%s WHERE id=%s",
                            (redactedText, 0, "Post deletion requested by user.", 0, redactedText, deletedattimestamp,
                             deletedattimestamp, postid)
                        )
                        conn.commit()

                        # upload to meilisearch
                        await IndexPost(postid, userid, username, title=redactedText,
                                        textcontent=redactedText, media=redactedText,
                                        timestamp=deletedattimestamp, topic="deleted", edited=True)

                        return {
                            "detail": {
                                "APImessage": "success",
                                "UIMessage": "Post uploaded!",
                                "postid": postid,
                                "username": username,
                                "attempt_time": int(str(time.time()).split(".")[0]),
                            },
                            "error_code": 0
                        }
                    return {
                        "detail": {
                            "APImessage": "failure",
                            "error": "Post does not exist.",
                            "UIMessage": "Post does not exist.",
                            "username": username,
                            "attempt_time": int(str(time.time()).split(".")[0]),
                        },
                        "error_code": 1
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
                "error": "Post deletion error.",
                "time_took": time_task_took
            }
        )
