import time

from fastapi import APIRouter
from fastapi import Form
from pydantic import BaseModel
import psycopg2

from functions.dbconfig import config
from functions.posting.create import makepost


class Post(BaseModel):
    username:      str
    sessionkey:    str
    posttitle:     str
    postcontent:   str
    attachedmedia: str
    posttopic:     str


router = APIRouter()


@router.post('/posts/create', tags=["posts"])
async def createpost(username: str = Form(), sessionkey: str = Form(),
                     posttitle: str = Form(), postcontent: str = Form(), attachedmedia: str = Form(),
                     posttopic: str = Form()):
    time_task_started = time.time()

    post_topics = [
        "meta/news",  # for everything related to news for this site
        "hacking/general", "hacking/osint", "hacking/digital", "hacking/physical",
        "hacking/pentesting",  # all things hacking
        "privacy/physical", "privacy/digital",
        "darkweb/tor", "darkweb/i2p", "darkweb/general",  # all things privacy related
        "tech/general", "tech/opensource", "tech/linux", "tech/microsoft", "tech/apple", "tech/servers", "tech/ai",
        "tech/databases", "tech/robotics", "tech/thefuture",
        "files/audio", "files/video", "files/documents",  # for discussion on... files?
        "programming/python", "programming/js", "programming/rust", "programming/go", "programming/java", 
        "programming/gaming", "programming/other",  # programming (duh)
        "gaming/cheats", "gaming/other",  # gaming
        "dev/testing"
    ]
    # ADD MORE

    if posttopic not in post_topics:
        time_task_took = time.time() - time_task_started
        return {
            "detail": {
                "APImessage": "failure",
                "error": "Invalid post topic.",
                "UIMessage": "Invalid post topic.",
                "username": username,
                "attempt_time": int(str(time.time()).split(".")[0]),
            },
            "time_took": time_task_took,
            "error_code": 0
        }
    if len(posttitle) > 70:
        time_task_took = time.time() - time_task_started
        return {
            "detail": {
                "APImessage": "failure",
                "error": "Post title too long.",
                "UIMessage": "Post title too long.",
                "username": username,
                "attempt_time": int(str(time.time()).split(".")[0]),
            },
            "time_took": time_task_took,
            "error_code": 0
        }
    return await makepost(posttitle, postcontent, attachedmedia, posttopic, username, sessionkey)
