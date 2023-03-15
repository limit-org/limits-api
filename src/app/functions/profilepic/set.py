import io

import psycopg2
from PIL import Image
from ..dbconfig import config
import time
import base64
from functions.log import logErrorToDB
from fastapi import HTTPException
import traceback


async def setpfp(file, username, sessionkey):
    try:
        conn = psycopg2.connect(config())

        # check the file size.
        fc = await file.read()
        if len(fc) > 2097152:  # if greater than exactly 2 MB
            return HTTPException(
                status_code=500,  # conflict http code
                detail={
                    "error_code": "1",
                    "error": "File too large.",
                    "UIMessage": "That picture is too large. Profile pictures can only be less than 2MB.",
                }
            )

        with conn.cursor() as cur:
            cur.execute(
                "SELECT (sessioncookie) FROM users WHERE username = %s",
                (username,)
            )
            sessioncookie = cur.fetchone()

            if sessioncookie is None:
                return {
                    "detail": {
                        "APImessage": "failure",
                        "UIMessage": "That user does not exist.",
                        "username": username,
                        "attempt_time": int(str(time.time()).split(".")[0]),
                    },
                    "error_code": 0
                }

            else:  # user exists
                # are they allowed to upload files?
                cur.execute("SELECT (allowedtoupload) FROM users WHERE username=%s",
                            (username,))
                allowedtoupload = cur.fetchone()
                if not allowedtoupload[0]:
                    return {
                        "detail": {
                            "APImessage": "failure",
                            "error": "User not allowed to upload files.",
                            "UIMessage": "You're not allowed to upload files to Limits.",
                            "username": username,
                            "attempt_time": int(str(time.time()).split(".")[0]),
                        },
                        "error_code": 0
                    }

                # they're allowed to upload files. check if session is correct.
                if sessioncookie[0] == sessionkey:  # correct sesh key
                    # crop media to a 512x512 square.

                    img = Image.open(io.BytesIO(fc)).convert("RGB")
                    thumb_width = 512  # res to crop to

                    def crop_center(pil_img, crop_width, crop_height):
                        img_width, img_height = pil_img.size
                        return pil_img.crop(((img_width - crop_width) // 2,
                                             (img_height - crop_height) // 2,
                                             (img_width + crop_width) // 2,
                                             (img_height + crop_height) // 2))

                    def crop_max_square(im):
                        return crop_center(im, min(im.size), min(im.size))

                    im_thumb = crop_max_square(img).resize((thumb_width, thumb_width), Image.LANCZOS)

                    # base64 media
                    buffered = io.BytesIO()
                    im_thumb.save(buffered, format="PNG")
                    mediabase64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

                    # get user id
                    cur.execute(
                        "SELECT (userid) FROM users WHERE username=%s",
                        (username,)
                    )
                    userid = cur.fetchone()[0]

                    # see if a pfp already exists
                    cur.execute(
                        "SELECT (userid) FROM profilepics WHERE userid=%s",
                        (userid,)
                    )
                    pfp = cur.fetchone()

                    if pfp is None:  # if no profile pic
                        # upload media to cock db
                        cur.execute(
                            "INSERT INTO profilepics (base64, userid, unixtimestamp) "
                            "VALUES (%s, %s, %s)",
                            (mediabase64, userid, time.time())
                        )
                        conn.commit()

                        return {
                            "detail": {
                                "APImessage": "success",
                                "UIMessage": "Profile picture set successfully!",
                                "username": username,
                                "userid": userid
                            },
                            "error_code": 0
                        }

                    if pfp[0] == userid:  # if pfp already exists
                        # upload media to db
                        cur.execute(
                            "UPDATE profilepics SET base64=%s, unixtimestamp=%s "
                            "WHERE userid=%s",
                            (mediabase64, time.time(), userid)
                        )
                        conn.commit()
                        return {
                            "detail": {
                                "APImessage": "success",
                                "UIMessage": "Profile picture set successfully!",
                                "username": username,
                                "userid": userid
                            },
                            "error_code": 0
                        }

                else:  # session is wrong
                    return {
                        "detail": {
                            "APImessage": "failure",
                            "error": "Invalid session key.",
                            "UIMessage": "Invalid session key. It probably expired.",
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
                "error": "Media upload error.",
            }
        )


async def removepfp(username, sessionkey):
    try:
        conn = psycopg2.connect(config())

        with conn.cursor() as cur:
            cur.execute(
                "SELECT (sessioncookie) FROM users WHERE username = %s",
                (username,)
            )
            sessioncookie = cur.fetchone()

            if sessioncookie is None:
                return {
                    "detail": {
                        "APImessage": "failure",
                        "UIMessage": "That user does not exist.",
                        "username": username,
                        "attempt_time": int(str(time.time()).split(".")[0]),
                    },
                    "error_code": 0
                }

            else:  # user exists
                if sessioncookie[0] == sessionkey:  # correct sesh key
                    # get user id
                    cur.execute(
                        "SELECT (userid) FROM users WHERE username=%s",
                        (username,)
                    )
                    userid = cur.fetchone()[0]

                    # see if a pfp already exists
                    cur.execute(
                        "SELECT (userid) FROM profilepics WHERE userid=%s",
                        (userid,)
                    )
                    pfp = cur.fetchone()

                    if pfp is None:  # if no profile pic
                        return {
                            "detail": {
                                "APImessage": "success",
                                "UIMessage": "Profile picture removed.",
                                "username": username,
                                "userid": userid
                            },
                            "error_code": 0
                        }

                    if pfp[0] == userid:  # if pfp already exists
                        # delete pfp from db
                        cur.execute(
                            "DELETE FROM profilepics WHERE userid=%s",
                            (userid,)
                        )
                        conn.commit()
                        return {
                            "detail": {
                                "APImessage": "success",
                                "UIMessage": "Profile picture removed.",
                                "username": username,
                                "userid": userid
                            },
                            "error_code": 0
                        }

                else:  # session is wrong
                    return {
                        "detail": {
                            "APImessage": "failure",
                            "error": "Invalid session key.",
                            "UIMessage": "Invalid session key. It probably expired.",
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
                "error": "Media upload error.",
            }
        )
