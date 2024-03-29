import re
import time
import psycopg2
from fastapi import HTTPException
import traceback

from ..meilisearch.MSIndex import IndexUser
from ..dbconfig import config
from ..log import logErrorToDB


async def makeUser(username, hashedpassword, email, ipaddress):

    try:
        conn = psycopg2.connect(config())

        # check if the email addr acc looks like an email
        # A regular expression to match email addresses
        email_regex = r"[^@]+@[^@]+\.[^@]+"

        # Use the regular expression to check if the string matches
        if re.match(email_regex, email):
            # it DOES look like an email
            with conn.cursor() as cur:
                # check if email is already in use.
                cur.execute(
                    "SELECT email FROM users WHERE email = %s",
                    (email,)
                )
                if cur.fetchone() is not None:  # if email already exists in the db
                    return HTTPException(
                        status_code=409,  # conflict http code
                        detail={
                            "error_code": "1",
                            "error": "Email already in use.",
                            "UIMessage": "This email is already in use.",
                        }
                    )

                # check if username already exists
                cur.execute(
                    "SELECT username FROM users WHERE username = %s",
                    (username,)
                )
                if cur.fetchone() is not None:  # if username alr exists in the db
                    return HTTPException(
                        status_code=409,  # conflict http code
                        detail={
                            "error_code": "1",
                            "error": "User already exists.",
                            "UIMessage": "Username is already in use."
                        }
                    )

                # get the highest user id
                cur.execute("SELECT MAX(userid) FROM users")
                highest_id = cur.fetchone()[0] or 0
                if highest_id <= 999:
                    highest_id = 1000
                userid = highest_id + 1
                usertimestamp = int(str(time.time()).split(".")[0])

                cur.execute(
                    "INSERT INTO users (userid, username, passwordhash, unixtimejoined, email, creationipaddress) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    (userid, username, hashedpassword, usertimestamp, email, ipaddress)
                )
                conn.commit()

                # let meilisearch index the user. most values are configured later though like if they're a mod,
                # their bio, etc.
                await IndexUser(userid, username, alias="", email=email, unixtimejoined=usertimestamp,
                                bio="", modnotes="", trusted=False, mod=False, badges=None, official=False)

                return {
                    "detail": {
                        "APImessage": "success",
                        "UIMessage": "You are now signed up. Welcome!",
                        "username": username,
                    },
                    "error_code": 0
                }
        else:
            return HTTPException(
                status_code=500,  # conflict http code
                detail={
                    "error_code": "1",
                    "error": "Email not valid.",
                    "UIMessage": "That doesn't look like an email..."
                }
            )

    except (Exception, psycopg2.DatabaseError):
        await logErrorToDB(str(traceback.format_exc()))
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "1",
                "http_code": "500",
                "error": "User signup error."
            }
        )
