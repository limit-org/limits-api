import time
import psycopg2
from fastapi import HTTPException
import traceback

from ..dbconfig import config
from ..log import logErrorToDB


async def logout(username, usersessionkey):
    try:
        conn = psycopg2.connect(config())
        with conn.cursor() as cur:
            # check if username already exists
            cur.execute(
                "SELECT (sessioncookie) FROM users WHERE username = %s",
                (username,)
            )

            # pull the password hash. if none, either no password (big issue) or user doesn't exist (probably this)
            sessionCookie = cur.fetchone()
            sessionCookie = sessionCookie[0]

            if sessionCookie is None:  # User doesnt exist or user never logged in lmao
                return {
                    "detail": {
                        "APImessage": "failure",
                        "UIMessage": "User does not exist or user never logged in.",
                        "username": username,
                        "attempt_time": int(str(time.time()).split(".")[0]),
                    },
                    "error_code": 0
                }

            else:  # user DOES exist.

                # is sessionkey correct?
                if usersessionkey == sessionCookie:  # it's correct, logout
                    cur.execute(
                        "UPDATE users SET sessioncookie=%s WHERE username=%s",
                        ("", username)
                    )
                    conn.commit()
                    return {
                        "detail": {
                            "APImessage": "success",
                            "UIMessage": "You are logged out.",
                            "username": username,
                            "time_logged_in": int(str(time.time()).split(".")[0]),
                        },
                        "error_code": 0
                    }
                else:
                    return {
                        "detail": {
                            "APImessage": "failure",
                            "UIMessage": "Couldn't logout due to an incorrect session key. It probably expired.",
                            "username": username,
                            "time_logged_in": int(str(time.time()).split(".")[0]),
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
                "error": "User signout error.",
            }
        )
