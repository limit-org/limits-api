import re
import time
import psycopg2
from fastapi import HTTPException
import bcrypt
import secrets
import traceback

from ..dbconfig import config
from ..log import logErrorToDB


async def login(username, password, user_agent, client_host):
    # start timer
    task_start_time = time.time()

    try:
        conn = psycopg2.connect(config())
        with conn.cursor() as cur:
            # check if username already exists
            cur.execute(
                "SELECT (passwordhash) FROM users WHERE username = %s",
                (username,)
            )

            # pull the password hash. if none, either no password (big issue) or user doesn't exist (probably this)
            pwdhash = cur.fetchone()

            if pwdhash is None:  # User doesnt exist.
                # calculate time taken to do the thing
                time_task_took = time.time() - task_start_time

                return {
                    "detail": {
                        "APImessage": "failure",
                        "UIMessage": "User does not exist.",
                        "username": username,
                        "attempt_time": int(str(time.time()).split(".")[0]),
                    },
                    "time_took": time_task_took,
                    "error_code": 0
                }

            else:  # user DOES exist.

                # verify is password is correct. if so, login. else: return to user its wrong
                # extract hash using regex
                match = re.match(r'^b"(.*)"$', pwdhash[0])
                pwdhash = match.group(1)

                if bcrypt.checkpw(password.encode('utf-8'), pwdhash.encode('utf-8')):
                    lalVar = f"Successful login attempt., {client_host}, {user_agent}"
                    # log that someone logged into their account
                    cur.execute(  # modify the lastaccountlogin field to now.
                        "UPDATE users SET lastaccountlogin=%s WHERE username=%s",
                        (lalVar, username)
                    )

                    # give user an auth token and save it to the database.
                    session_token = secrets.token_hex(64)  # generate 128-bit key
                    cur.execute(
                        "UPDATE users SET sessioncookie=%s WHERE username=%s",
                        (session_token, username)
                    )
                    conn.commit()
                    # calculate time taken to do the thing
                    time_task_took = time.time() - task_start_time
                    return {
                        "detail": {
                            "APImessage": "success",
                            "UIMessage": "You are now signed in.",
                            "username": username,
                            "time_logged_in": int(str(time.time()).split(".")[0]),
                            "session": session_token
                        },
                        "time_took": time_task_took,
                        "error_code": 0
                    }
                else:
                    print('Password is incorrect')
                    lalVar = f"Failed login attempt., {client_host}, {user_agent}"
                    # modify the lastaccountlogin field now to show a failed attempt. this does not logout the user
                    cur.execute(
                        "UPDATE users SET lastaccountlogin=%s WHERE username=%s",
                        (lalVar, username)
                    )
                    # calculate time taken to do the thing
                    time_task_took = time.time() - task_start_time

                    return {
                        "detail": {
                            "APImessage": "failure",
                            "UIMessage": "Incorrect password.",
                            "username": username,
                            "attempt_time": int(str(time.time()).split(".")[0]),
                        },
                        "time_took": time_task_took,
                        "error_code": 0
                    }

    except (Exception, psycopg2.DatabaseError) :
        time_task_took = time.time() - task_start_time
        await logErrorToDB(str(traceback.format_exc()), timetaken=time_task_took)
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "1",
                "http_code": "500",
                "error": "User signin error.",
                "time_took": time_task_took
            }
        )
