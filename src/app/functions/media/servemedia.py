import psycopg2
from ..dbconfig import config
import time
import base64
from functions.log import logErrorToDB
from fastapi import HTTPException, Response
import traceback


async def servemedia(contentid):
    # start timer
    task_start_time = time.time()

    try:
        conn = psycopg2.connect(config())

        with conn.cursor() as cur:
            cur.execute(
                "SELECT (base64, deleted, reasonfordeletion) FROM media WHERE contentid = %s",
                (contentid,)
            )
            media = cur.fetchone()

            if media is None:  # it doesn't exist
                time_task_took = time.time() - task_start_time
                return {
                    "detail": {
                        "APImessage": "failure",
                        "UIMessage": "That media file doesn't exist.",
                        "contentid": contentid,
                        "attempt_time": int(str(time.time()).split(".")[0]),
                    },
                    "time_took": time_task_took,
                    "error_code": 0
                }

            else:  # it exists
                # parse "media" into acc values
                string = media[0][1:-1]
                values = string.split(',')
                media64 = values[0]
                deleted = values[1]
                deletereason = values[2]

                if deleted == "t":  # if it exists/ed but is now deleted
                    time_task_took = time.time() - task_start_time
                    return {
                        "detail": {
                            "APImessage": "success",
                            "UIMessage": f"That media file was deleted. Reason: '{str(deletereason)}'.",
                            "deletereason": deletereason,
                            "contentid": contentid,
                            "attempt_time": int(str(time.time()).split(".")[0]),
                        },
                        "time_took": time_task_took,
                        "error_code": 0
                    }

                # not needed for me, might be for others so we will leave this here.
                # # get content type
                # bytesData = io.BytesIO()
                # bytesData.write(base64.b64decode(media64))
                # bytesData.seek(0)  # Jump to the beginning of the file-like interface to read all content!

                # de base64 media
                media64 = base64.b64decode(media64)

                # Return the data
                response = Response(content=media64)  # , media_type=mediatype)
                return response

    except (Exception, psycopg2.DatabaseError):
        time_task_took = time.time() - task_start_time
        print(str(traceback.format_exc()))
        await logErrorToDB(str(traceback.format_exc()), timetaken=time_task_took)
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "1",
                "http_code": "500",
                "error": "Media server error.",
                "time_took": time_task_took
            }
        )
