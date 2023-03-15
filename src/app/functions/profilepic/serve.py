import io

import PIL.Image
import psycopg2
from ..dbconfig import config
import time
import base64
from functions.log import logErrorToDB
from fastapi import HTTPException, Response
import traceback


async def servepfp(username, size):
    # start timer
    task_start_time = time.time()

    if size not in [512, 256, 128, 64, 20]:
        time_task_took = time.time() - task_start_time
        return {
            "detail": {
                "APImessage": "failure",
                "UIMessage": "Incorrect profile picture size. Supported values are 512,256,128,64,20.",
                "attempt_time": int(str(time.time()).split(".")[0]),
            },
            "time_took": time_task_took,
            "error_code": 0
        }

    try:
        conn = psycopg2.connect(config())

        with conn.cursor() as cur:
            # get user id for username
            cur.execute(
                "SELECT (userid) FROM users WHERE username = %s",
                (username,)
            )
            userid = cur.fetchone()[0]

            cur.execute(
                "SELECT (base64, deleted, deletedreason) FROM profilepics WHERE userid = %s",
                (userid,)
            )
            pfp = cur.fetchone()

            if pfp is None:  # pfp doesn't exist
                time_task_took = time.time() - task_start_time
                return {
                    "detail": {
                        "APImessage": "failure",
                        "UIMessage": "This user hasn't setup a profile picture.",
                        "username": username,
                        "userid": userid,
                        "attempt_time": int(str(time.time()).split(".")[0]),
                    },
                    "time_took": time_task_took,
                    "error_code": 0
                }

            else:  # it exists
                # parse "media" into acc values
                string = pfp[0][1:-1]
                values = string.split(',')
                media64 = values[0]
                deleted = values[1]
                deletereason = values[2]

                if deleted == "t":  # if it exists/ed but is now deleted
                    time_task_took = time.time() - task_start_time
                    return {
                        "detail": {
                            "APImessage": "success",
                            "UIMessage": f"That profile picture was deleted. Reason: '{str(deletereason)}'.",
                            "deletereason": deletereason,
                            "username": username,
                            "userid": userid,
                            "attempt_time": int(str(time.time()).split(".")[0]),
                        },
                        "time_took": time_task_took,
                        "error_code": 0
                    }

                # de base64 media
                media64 = base64.b64decode(media64)

                if size == 512:
                    # Return the data without doing anything cus all pfps are already 512x512
                    response = Response(content=media64, media_type="image/png")
                    return response
                else:
                    # make smaller lmao
                    img = PIL.Image.open(io.BytesIO(media64)).convert("RGB")
                    im_thumb = img.resize((size, size), PIL.Image.LANCZOS)

                    # base64 media
                    buffered = io.BytesIO()
                    im_thumb.save(buffered, format="PNG")
                    response = Response(content=buffered.getvalue(), media_type="image/png")
                    return response

    except (Exception, psycopg2.DatabaseError):
        time_task_took = time.time() - task_start_time
        await logErrorToDB(str(traceback.format_exc()))
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "1",
                "http_code": "500",
                "error": "Profile picture server error.",
                "time_took": time_task_took
            }
        )
