import csv
import time
import psycopg2
from fastapi import HTTPException, Response
from fastapi.responses import JSONResponse
import traceback


from ..dbconfig import config
from ..log import logErrorToDB
from ..meilisearch.MSIndex import IndexUser


# update the bio of the user who asks.
async def updateBio(username, userSessionKey, newBio):
    try:
        conn = psycopg2.connect(config())
        with conn.cursor() as cur:
            # check if user exists
            cur.execute(
                "SELECT (sessioncookie) FROM users WHERE username = %s",
                (username,)
            )

            # pull the session. if none, user doesn't exist
            sessionCookie = cur.fetchone()
            if sessionCookie is None:  # User doesnt exist
                return JSONResponse(status_code=400, content={
                    "detail": {
                        "error": "User does not exist.",
                        "username": username,
                    },
                    "error_code": 1  # unexpected but not an error.
                })

            sessionCookie = sessionCookie[0]  # wait to do this until now, otherwise fastapi errors

            # if user DOES exist
            if userSessionKey == sessionCookie:  # is the provided session correct? the same = correct.
                # it's correct, change users bio
                cur.execute(
                    "UPDATE users SET bio=%s WHERE username=%s",
                    (newBio, username)
                )
                conn.commit()  # commit to db

                cur.execute(
                    "SELECT (userid, username, alias, unixtimejoined, bio, modnotes, trusted, moderator, badges, "
                    "email, makeemailpublic, official) "
                    "FROM users WHERE username = %s",
                    (username,)
                )
                DBValue = cur.fetchone()  # fetch user details again.

                # Parse the returned stuff into variables.
                reader = csv.reader(DBValue, delimiter=',', quotechar='"')
                fields = list(reader)[0]
                user_id, username, alias, unixjoin, bio, modnotes, is_trusted, is_mod, badges, email, is_email_public, \
                    is_official = fields

                # Remove the parentheses from the first and last values
                user_id = user_id[1:]
                is_official = is_official[:-1]

                # if email isn't supposed to be shared, replace it before indexing.
                if is_email_public == "f":
                    email = "[REDACTED DUE TO USERS PRIVACY CHOICES.]"

                # meilisearch needs to index the user now.
                await IndexUser(user_id, username, alias, email, unixjoin, bio, modnotes, is_trusted, is_mod,
                                badges, is_official)

                # everything worked! yay. return to the user it did.
                return JSONResponse(status_code=200, content={
                    "detail": {
                        "response": "Bio successfully changed!.",
                        "username": username,
                        "bio": bio
                    },
                    "error_code": 0  # it's all fine.
                })

            else:  # session key is wrong / auth failure
                return JSONResponse(status_code=401, content={
                    "detail": {
                        "error": "Incorrect session key.",
                    },
                    "error_code": 2  # an error.
                })

    except (Exception, psycopg2.DatabaseError):
        await logErrorToDB(str(traceback.format_exc()), timetaken=0)  # log this error to the database.
        return JSONResponse(status_code=500, content={
            "detail": {
                "error": "Bio update error.",
            },
            "error_code": 2
        })


# update the username of whoever asks.
async def updateUsername(currentUsername, userSessionKey, newUsername):
    # check if the new username is the same as the old one.
    if newUsername == currentUsername:  # if username hasn't been updated, don't persist on db, that's a waste.
        return JSONResponse(status_code=400, content={
            "detail": {
                "error": "Old username is same as new username.",
                "currentUsername": currentUsername,
                "newUsername": newUsername
            },
            "error_code": 1  # unexpected but not an error.
        })

    # they're not the same and we can continue.
    try:
        conn = psycopg2.connect(config())
        with conn.cursor() as cur:
            # check if username already exists
            cur.execute(
                "SELECT (sessioncookie) FROM users WHERE username = %s",
                (currentUsername,)
            )

            # pull the session.
            sessionCookie = cur.fetchone()
            if sessionCookie is None:  # User doesnt exist if equal
                return JSONResponse(status_code=400, content={
                    "detail": {
                        "error": "User does not exist.",
                        "username": currentUsername,
                    },
                    "error_code": 1  # unexpected but not an error.
                })

            sessionCookie = sessionCookie[0]  # wait to do this, otherwise fastapi errors lol

            # user DOES exist
            if userSessionKey == sessionCookie:  # is sessionkey correct?
                # it's correct, change users username
                cur.execute(
                    "UPDATE users SET username=%s WHERE username=%s",
                    (newUsername, currentUsername)
                )
                conn.commit()  # commit to db

                cur.execute(
                    "SELECT (userid, username, alias, unixtimejoined, bio, modnotes, trusted, moderator, badges, "
                    "email, makeemailpublic, official) "
                    "FROM users WHERE username = %s",
                    (newUsername,)
                )
                DBValue = cur.fetchone()

                # Parse the returned stuff into variables.
                reader = csv.reader(DBValue, delimiter=',', quotechar='"')
                fields = list(reader)[0]
                user_id, username, alias, unixjoin, bio, modnotes, is_trusted, is_mod, badges, email, is_email_public, \
                    is_official = fields

                # Remove the parentheses from the first and last values
                user_id = user_id[1:]
                is_official = is_official[:-1]

                # if email isn't supposed to be shared, replace it before indexing.
                if is_email_public == "f":
                    email = "[REDACTED DUE TO USERS PRIVACY CHOICES.]"

                # meilisearch needs to index the user now.
                await IndexUser(user_id, username, alias, email, unixjoin, bio, modnotes, is_trusted, is_mod,
                                badges, is_official)

                # everything worked! yay
                return JSONResponse(status_code=200, content={
                    "detail": {
                        "response": "Username successfully changed!.",
                        "newUsername": newUsername
                    },
                    "error_code": 0  # it's all fine.
                })

            else:  # session key is wrong
                return JSONResponse(status_code=401, content={
                    "detail": {
                        "error": "Incorrect session key.",
                    },
                    "error_code": 2  # an error.
                })

    except (Exception, psycopg2.DatabaseError):
        await logErrorToDB(str(traceback.format_exc()), timetaken=0)
        return JSONResponse(status_code=500, content={
            "detail": {
                "error": "User profile update error.",
            },
            "error_code": 2
        })


async def updateEmailPublicity(username, userSessionKey, emailIsPublic):
    try:
        conn = psycopg2.connect(config())
        with conn.cursor() as cur:
            # check if username exists
            cur.execute(
                "SELECT (sessioncookie) FROM users WHERE username = %s",
                (username,)
            )

            # pull the session cookie
            sessionCookie = cur.fetchone()
            if sessionCookie is None:  # User doesnt exist or user never logged in lmao
                return JSONResponse(status_code=400, content={
                    "detail": {
                        "error": "User does not exist.",
                        "username": username,
                    },
                    "error_code": 1  # unexpected but not an error.
                })

            sessionCookie = sessionCookie[0]  # wait to do this, otherwise fastapi errors lol. it parses the variable.

            # user DOES exist
            if userSessionKey == sessionCookie:  # is sessionKey correct?
                # it's correct, change users email preference
                if emailIsPublic in ["t", "True", True, "true"]:
                    emailIsPublic = True
                else:
                    emailIsPublic = False

                # send to db
                cur.execute(
                    "UPDATE users SET makeemailpublic=%s WHERE username=%s",
                    (emailIsPublic, username)
                )
                conn.commit()  # commit to db

                cur.execute(
                    "SELECT (userid, username, alias, unixtimejoined, bio, modnotes, trusted, moderator, badges, "
                    "email, makeemailpublic, official) "
                    "FROM users WHERE username = %s",
                    (username,)
                )
                DBValue = cur.fetchone()

                # Parse the returned stuff into variables.
                reader = csv.reader(DBValue, delimiter=',', quotechar='"')
                fields = list(reader)[0]
                user_id, username, alias, unixjoin, bio, modnotes, is_trusted, is_mod, badges, email, is_email_public, \
                    is_official = fields

                # Remove the parentheses from the first and last values
                user_id = user_id[1:]
                is_official = is_official[:-1]

                # don't index email if we shouldn't share it.
                if is_email_public == "f":
                    email = "[REDACTED DUE TO USERS PRIVACY CHOICES.]"

                # meilisearch needs to index the user now.
                await IndexUser(user_id, username, alias, email, unixjoin, bio, modnotes, is_trusted, is_mod,
                                badges, is_official)

                # everything worked! yay
                return JSONResponse(status_code=200, content={
                    "detail": {
                        "response": "Email publicity successfully changed!.",
                        "username": username,
                        "emailPublicity": str(is_email_public)
                    },
                    "error_code": 0  # it's all fine.
                })

            else:  # session key is wrong
                return JSONResponse(status_code=401, content={
                    "detail": {
                        "error": "Incorrect session key.",
                    },
                    "error_code": 2  # an error.
                })

    except (Exception, psycopg2.DatabaseError):
        await logErrorToDB(str(traceback.format_exc()), timetaken=0)
        return JSONResponse(status_code=500, content={
            "detail": {
                "error": "User profile update error.",
            },
            "error_code": 2
        })


async def updateUserAlias(username, userSessionKey, alias):
    try:
        conn = psycopg2.connect(config())
        with conn.cursor() as cur:
            # check if username exists
            cur.execute(
                "SELECT (sessioncookie) FROM users WHERE username = %s",
                (username,)
            )

            # pull the session cookie
            sessionCookie = cur.fetchone()
            if sessionCookie is None:  # User doesnt exist or user never logged in lmao
                return JSONResponse(status_code=400, content={
                    "detail": {
                        "error": "User does not exist.",
                        "username": username,
                    },
                    "error_code": 1  # unexpected but not an error.
                })

            sessionCookie = sessionCookie[0]  # wait to do this, otherwise fastapi errors lol. it parses the variable.

            # user DOES exist
            if userSessionKey == sessionCookie:  # is sessionKey correct?
                # it's correct, change users alias
                # send to db
                cur.execute(
                    "UPDATE users SET alias=%s WHERE username=%s",
                    (alias, username)
                )
                conn.commit()  # commit to db

                cur.execute(
                    "SELECT (userid, username, alias, unixtimejoined, bio, modnotes, trusted, moderator, badges, "
                    "email, makeemailpublic, official) "
                    "FROM users WHERE username = %s",
                    (username,)
                )
                DBValue = cur.fetchone()

                # Parse the returned stuff into variables.
                reader = csv.reader(DBValue, delimiter=',', quotechar='"')
                fields = list(reader)[0]
                user_id, username, alias, unixjoin, bio, modnotes, is_trusted, is_mod, badges, email, is_email_public, \
                    is_official = fields

                # Remove the parentheses from the first and last values
                user_id = user_id[1:]
                is_official = is_official[:-1]

                # don't share if user doesn't want us to.
                if is_email_public == "f":
                    email = "[REDACTED DUE TO USERS PRIVACY CHOICES.]"

                # meilisearch needs to index the user now.
                await IndexUser(user_id, username, alias, email, unixjoin, bio, modnotes, is_trusted, is_mod,
                                badges, is_official)

                # everything worked! yay
                return JSONResponse(status_code=200, content={
                    "detail": {
                        "response": "Alias successfully changed!",
                        "username": username,
                        "alias": alias
                    },
                    "error_code": 0  # it's all fine.
                })

            else:  # session key is wrong
                return JSONResponse(status_code=401, content={
                    "detail": {
                        "error": "Incorrect session key.",
                    },
                    "error_code": 2  # an error.
                })

    except (Exception, psycopg2.DatabaseError):
        await logErrorToDB(str(traceback.format_exc()), timetaken=0)
        return JSONResponse(status_code=500, content={
            "detail": {
                "error": "User alias update error.",
            },
            "error_code": 2
        })
