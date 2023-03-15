import re
import time
import psycopg2
from fastapi import HTTPException
import bcrypt
import traceback

from ..dbconfig import config
from ..log import logErrorToDB
from ..passwordstandards import CheckPassword


async def changepwd(username, password, newpass, clienthost, useragent):
    try:
        conn = psycopg2.connect(config())
        with conn.cursor() as cur:
            # check if username already exists
            cur.execute(
                "SELECT (passwordhash) FROM users WHERE username = %s",
                (username,)
            )

            # pull the password hash. if none, user doesn't exist
            pwdhash = cur.fetchone()

            if pwdhash is None:  # User doesnt exist.
                return {
                    "detail": {
                        "APImessage": "failure",
                        "UIMessage": "User does not exist.",
                        "username": username,
                        "attempt_time": int(str(time.time()).split(".")[0]),
                    },
                    "error_code": 0
                }

            else:  # user DOES exist.

                # verify is password is correct. if so, change. else: return to user its wrong
                # extract hash using regex
                match = re.match(r'^b"(.*)"$', pwdhash[0])
                pwdhash = match.group(1)

                if bcrypt.checkpw(password.encode('utf-8'), pwdhash.encode('utf-8')):  # password is right
                    lalVar = f"Successful password reset attempt., {clienthost}, {useragent}"
                    # log that someone logged into their account
                    cur.execute(  # modify the lastaccountlogin field to now.
                        "UPDATE users SET lastaccountlogin=%s WHERE username=%s",
                        (lalVar, username)
                    )

                    # does password conform to standards?
                    pwc = CheckPassword(plainTextPass=password, username=username)
                    if pwc != 0:
                        return {
                            "detail": {
                                "error_code": "1",
                                "error": str(pwc['err']),
                                "UIMessage": str(pwc['ui']),
                            }
                        }

                    # Generate a salt for the password
                    salt = bcrypt.gensalt()
                    # Hash the password using the salt
                    newpass = str(bcrypt.hashpw(str(newpass).encode('utf-8'), salt)).replace("'", "\"")

                    cur.execute(
                        "UPDATE users SET passwordhash=%s WHERE username=%s",
                        (newpass, username,)
                    )

                    cur.execute(
                        "UPDATE users SET sessioncookie=%s WHERE username=%s",
                        ("", username)
                    )
                    conn.commit()
                    return {
                        "detail": {
                            "APImessage": "success",
                            "UIMessage": "Your password has been changed!",
                            "username": username,
                            "reset_time": int(str(time.time()).split(".")[0]),
                        },
                        "error_code": 0
                    }

                else:  # password is wrong
                    lalVar = f"Failed password reset attempt: {clienthost}: {useragent}"
                    # modify the lastaccountlogin field now to show a failed attempt. this does not logout the user
                    cur.execute(
                        "UPDATE users SET lastaccountlogin=%s WHERE username=%s",
                        (lalVar, username)
                    )
                    conn.commit()

                    return {
                        "detail": {
                            "APImessage": "failure",
                            "UIMessage": "Incorrect password.",
                            "username": username,
                            "attempt_time": int(str(time.time()).split(".")[0]),
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
                "error": "Password reset error.",
            }
        )
