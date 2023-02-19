import time
import psycopg2
from fastapi import HTTPException

from ..dbconfig import config
from ..log import logErrorToDB


def logout(username, usersessionkey):
    # start timer
    task_start_time = time.time()

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
                # calculate time taken to do the thing
                time_task_took = time.time() - task_start_time

                return {
                    "detail": {
                        "APImessage": "failure",
                        "UIMessage": "User does not exist or user never logged in.",
                        "username": username,
                        "attempt_time": int(str(time.time()).split(".")[0]),
                    },
                    "time_took": time_task_took,
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
                    # calculate time taken to do the thing
                    time_task_took = time.time() - task_start_time
                    return {
                        "detail": {
                            "APImessage": "success",
                            "UIMessage": "You are logged out.",
                            "username": username,
                            "time_logged_in": int(str(time.time()).split(".")[0]),
                        },
                        "time_took": time_task_took,
                        "error_code": 0
                    }
                else:
                    time_task_took = time.time() - task_start_time
                    return {
                        "detail": {
                            "APImessage": "failure",
                            "UIMessage": "Couldn't logout due to an incorrect session key. It probably expired.",
                            "username": username,
                            "time_logged_in": int(str(time.time()).split(".")[0]),
                        },
                        "time_took": time_task_took,
                        "error_code": 0
                    }

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        error = str(error).replace("\'", "\"")
        logErrorToDB(errortext=error)
        time_task_took = time.time() - task_start_time
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "1",
                "http_code": "500",
                "error": "User signout error.",
                "time_took": time_task_took
            }
        )
