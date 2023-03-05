import csv
import time
import psycopg2
from fastapi import HTTPException
import traceback

from ..dbconfig import config
from ..log import logErrorToDB
from ..meilisearch.MSIndex import IndexUser


async def updateUser(username, usersessionkey, newusername, newbio, emailispublic, newalias):
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

            else:  # user DOES exist
                if newusername in [username, "null"]:  # if username hasn't been updated, don't update
                    newusername = username

                if newalias == "null":
                    cur.execute(
                        "SELECT alias FROM users WHERE username=%s",
                        (username,)
                    )
                    newalias = cur.fetchone()

                if newbio == "null":  # use null if the bio isn't being updated.
                    cur.execute(
                        "SELECT bio FROM users WHERE username=%s",
                        (username,)
                    )
                    newbio = cur.fetchone()
                if newbio == "none":  # Use none to get rid of the bio
                    newbio = ""

                if emailispublic not in ["t", "f"]:
                    time_task_took = time.time() - task_start_time
                    return {
                        "detail": {
                            "APImessage": "failure",
                            "UIMessage": "Incorrect 'emailispublic' field. Should be 't' or 'f'.",
                            "username": username,
                            "attempt_time": int(str(time.time()).split(".")[0]),
                        },
                        "time_took": time_task_took,
                        "error_code": 0
                    }

                else:
                    if emailispublic == "t":
                        emailispublic = True
                    if emailispublic == "f":
                        emailispublic = False

                # is sessionkey correct?
                if usersessionkey == sessionCookie:  # it's correct, change users stuff
                    # newusername, newbio, emailispublic
                    cur.execute(  # modify the lastaccountlogin field to now.
                        "UPDATE users SET username=%s, alias=%s, bio=%s, makeemailpublic=%s WHERE username=%s",
                        (newusername, newalias, newbio, emailispublic, username)
                    )
                    conn.commit()

                    cur.execute(
                        "SELECT (userid, username, alias, unixtimejoined, bio, modnotes, trusted, moderator, awards, "
                        "email, makeemailpublic, official) "
                        "FROM users WHERE username = %s",
                        (username,)
                    )
                    DBValue = cur.fetchone()
                    # Parse the string using the csv module
                    reader = csv.reader(DBValue, delimiter=',', quotechar='"')
                    # Extract the fields and convert them to a list
                    fields = list(reader)[0]
                    # Extract the individual values from the list
                    user_id, username, alias, unixjoin, bio, modnotes, is_trusted, is_mod, awards, email, is_email_public, \
                        is_official = fields

                    # Remove the parentheses from the first and last values
                    user_id = user_id[1:]
                    is_official = is_official[:-1]

                    if is_email_public == "f":
                        email = "*******@provider.tld"

                    await IndexUser(user_id, username, alias, unixjoin, bio, modnotes, is_trusted, is_mod,
                                    awards, is_official)

                    time_task_took = time.time() - task_start_time
                    return {
                        "detail": {
                            "APImessage": "success",
                            "UIMessage": "Successfully modified your profile!",
                            "username": newusername,
                            "bio": newbio,
                            "publicemail": emailispublic,
                            "alias": newalias
                        },
                        "time_took": time_task_took,
                        "error_code": 0
                    }

                else:  # session key is wrong
                    time_task_took = time.time() - task_start_time
                    return {
                        "detail": {
                            "APImessage": "failure",
                            "UIMessage": "Couldn't change details due to an incorrect session key. "
                                         "It probably expired.",
                            "username": username,
                            "time_logged_in": int(str(time.time()).split(".")[0]),
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
                "error": "User signup error.",
                "time_took": time_task_took
            }
        )
