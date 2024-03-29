import time

from fastapi import APIRouter
from fastapi import Form
from pydantic import BaseModel

from functions.posting.create import makepost
from functions.posting.update import updatepost
from functions.posting.delete import deletepost


class Post(BaseModel):
    username: str
    sessionkey: str
    posttitle: str
    postcontent: str
    attachedmedia: str
    posttopic: str


router = APIRouter()


@router.post('/posts/create/', tags=["posts"], status_code=201)
async def create_post(username: str = Form(), sessionkey: str = Form(),
                      posttitle: str = Form(), postcontent: str = Form(), attachedmedia: str = Form(),
                      posttopic: str = Form()):

    post_topics = [
        "meta/news",  # for everything related to news for this site
        "hacking/general", "hacking/osint", "hacking/digital", "hacking/physical", "hacking/pentesting",  # hacking

        "privacy/physical", "privacy/digital",  # anything privacy related

        "darkweb/tor", "darkweb/i2p", "darkweb/general",  # alternative internets.

        "tech/general", "tech/opensource", "tech/linux", "tech/microsoft", "tech/apple", "tech/servers", "tech/ai",
        "tech/databases", "tech/robotics", "tech/thefuture",  # main tech discussions

        "files/audio", "files/video", "files/documents",  # for discussion on... files?

        "programming/python", "programming/js", "programming/rust", "programming/go", "programming/java",
        "programming/other",  # programming (duh)

        "gaming/cheats", "gaming/other",  # gaming

        "dev/testing"  # developer testing for limits. anything to stay goes into any other topic.
    ]
    # ADD MORE

    if posttopic not in post_topics:
        return {
            "detail": {
                "APImessage": "failure",
                "error": "Invalid post topic.",
                "UIMessage": "Invalid post topic.",
                "username": username,
                "attempt_time": int(str(time.time()).split(".")[0]),
            },
            "error_code": 0
        }
    if len(posttitle) > 101:  # 100 or less
        return {
            "detail": {
                "APImessage": "failure",
                "error": "Post title too long.",
                "UIMessage": "Post title too long.",
                "username": username,
                "attempt_time": int(str(time.time()).split(".")[0]),
            },
            "error_code": 0
        }
    return await makepost(posttitle, postcontent, attachedmedia, posttopic, username, sessionkey)


@router.put('/posts/edit/', tags=["posts"], status_code=200)
async def update_post(username: str = Form(), sessionkey: str = Form(), postid: int = Form(), posttitle: str = Form(),
                      postcontent: str = Form(), attachedmedia: str = Form(), posttopic: str = Form()):
    return await updatepost(postid, posttitle, postcontent, attachedmedia, posttopic, username, sessionkey)


@router.delete('/posts/delete/', tags=["posts"], status_code=200)
async def delete_post(username: str = Form(), sessionkey: str = Form(), postid: int = Form()):
    return await deletepost(postid, username, sessionkey)

