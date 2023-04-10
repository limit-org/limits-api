import psycopg2
import time
from ..dbconfig import config
import base64
from ..log import logErrorToDB
from fastapi import HTTPException
import traceback


# func for uploading media to limits
async def uploadMedia(file, username, sessionkey):
    try:
        conn = psycopg2.connect(config())

        with conn.cursor() as cur:
            cur.execute(
                "SELECT (sessioncookie) FROM users WHERE username = %s",
                (username,)
            )
            sessioncookie = cur.fetchone()

            if sessioncookie is None:  # if the user doesn't exist or never logged in
                return {
                    "detail": {
                        "APImessage": "failure",
                        "UIMessage": "That user does not exist.",
                        "username": username,
                    },
                    "error_code": 0
                }

            else:  # user exists
                # are they allowed to upload files?
                cur.execute("SELECT (allowedtoupload) FROM users WHERE username=%s",
                            (username,))
                if not cur.fetchone()[0]:
                    return {
                        "detail": {
                            "APImessage": "failure",
                            "error": "User not allowed to upload files.",
                            "UIMessage": "You're not allowed to upload files to Limits.",
                            "username": username,
                        },
                        "error_code": 0
                    }

                if sessioncookie[0] == sessionkey:  # correct sesh key
                    # check the file size.
                    fc = await file.read()
                    if len(fc) > 10485760:  # if greater than exactly 10 MB
                        return HTTPException(
                            status_code=400,  # bad request
                            detail={
                                "error_code": 1,
                                "error": "File too large.",
                                "UIMessage": "That file is too large. They can only be 10MB or less.",
                            }
                        )

                    # base64 media
                    mediabase64 = base64.b64encode(await file.read()).decode("utf-8")

                    # get user id
                    cur.execute(
                        "SELECT (userid) FROM users WHERE username=%s",
                        (username,)
                    )
                    userid = cur.fetchone()

                    # find the highest media id
                    cur.execute("SELECT MAX(contentid) FROM media")
                    highest_id = cur.fetchone()[0] or 0

                    # upload media to cock db
                    cur.execute(
                        "INSERT INTO media (base64, userid, unixtimestamp, deleted, filename, contentid, contenttype) "
                        "VALUES (%s, %s, %s, %s, %s, %s)",
                        (mediabase64, userid, time.time(), "false", file.filename, (int(highest_id) + 1),
                         str(file.content_type))
                    )
                    conn.commit()

                    return {
                        "detail": {
                            "APImessage": "success",
                            "UIMessage": "Media uploaded successfully.",
                            "contentid": str(int(highest_id) + 1),
                            "filename": file.filename,
                            "username": username,
                        },
                        "error_code": 0
                    }

                else:  # session is wrong
                    return {
                        "detail": {
                            "APImessage": "failure",
                            "error": "Invalid session key.",
                            "UIMessage": "Invalid session key.",
                            "username": username,
                        },
                        "error_code": 0
                    }

    except (Exception, psycopg2.DatabaseError):
        await logErrorToDB(str(traceback.format_exc()))
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "1",
                "http_code": "500",
                "error": "Media upload error.",
            }
        )
