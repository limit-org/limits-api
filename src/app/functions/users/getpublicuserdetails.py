import csv
import traceback

import psycopg2
from fastapi import HTTPException

from ..dbconfig import config
from ..log import logErrorToDB


async def getpublicuserinfo(username):

    try:
        conn = psycopg2.connect(config())
        with conn.cursor() as cur:
            # check if username already exists
            cur.execute(
                "SELECT (userid, username, alias, unixtimejoined, bio, modnotes, trusted, moderator, badges, "
                "email, makeemailpublic, official) "
                "FROM users WHERE username = %s",
                (username,)
            )
            DBValue = cur.fetchone()

            if DBValue is not None:  # if username already exists in the db
                # parse values about user into variables
                reader = csv.reader(DBValue, delimiter=',', quotechar='"')
                fields = list(reader)[0]
                user_id, username, alias, unixjoin, bio, modnotes, is_trusted, is_mod, badges, email, is_email_public, \
                    is_official = fields

                # Remove the parentheses from the first and last values
                user_id = user_id[1:]
                is_official = is_official[:-1]

                if is_email_public == "f":
                    email = "[REDACTED DUE TO USERS PRIVACY CHOICES.]"

                return {
                    "detail": {
                        "UIContents": {
                            "userid": user_id,
                            "username": username,
                            "alias": alias,
                            "unixtimejoined": unixjoin,
                            "bio": bio,
                            "is_trusted": is_trusted,
                            "moderation_notes": modnotes,
                            "is_mod": is_mod,
                            "badges": badges,
                            "email": email,
                            "is_email_public": is_email_public,
                            "official": is_official
                        },
                    },
                    "error_code": 0
                }
            else:
                return {
                    "detail": {
                        "error_code": "1",
                        "error": "User does not exist.",
                        "UIMessage": "That user does not exist.",
                    }
                }

    except (Exception, psycopg2.DatabaseError):
        await logErrorToDB(str(traceback.format_exc()))
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "1",
                "http_code": "500",
                "error": "SQL query error.",
            }
        )
