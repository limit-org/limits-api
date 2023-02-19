from fastapi import APIRouter, Header, Form, Request
from pydantic import BaseModel
import bcrypt
import time

from functions.users.makeuser import makeUser
from functions.users.getpublicuserdetails import getpublicuserinfo
from functions.users.login import login
from functions.users.logout import logout

router = APIRouter()


class User(BaseModel):
    username:   str
    password:   str
    email:      str
    sessionkey: str


@router.post('/users/create/', tags=["user"])
async def createuser(request: Request, username: str = Form(), password: str = Form(), email: str = Form()):
    time_task_started = time.time()

    # lowercase the username
    username = username.lower()

    # check username/pwd length
    # check username
    if len(username) <= 2:  # equal to or less than 2 chars
        time_task_took = time.time() - time_task_started
        return {
            "detail": {
                "error_code": "1",
                "error": "Username not long enough.",
                "UIMessage": "Username needs to be at least 3 characters long.",
                "time_took": time_task_took
            }
        }
    if len(username) >= 26:
        time_task_took = time.time() - time_task_started
        return {
            "detail": {
                "error_code": "1",
                "error": "Username too long.",
                "UIMessage": "Usernames can only be 25 characters long.",
                "time_took": time_task_took
            }
        }

    if len(password) >= 257:
        time_task_took = time.time() - time_task_started
        return {
            "detail": {
                "error_code": "1",
                "error": "Password too long.",
                "UIMessage": "Stop being paranoid. Your password does not need to be over 256 characters long.",
                "time_took": time_task_took
            }
        }

    # check password
    if len(password) <= 7:  # equal to or less than 7 characters
        time_task_took = time.time() - time_task_started
        return {
            "detail": {
                "error_code": "1",
                "error": "Password not long enough.",
                "UIMessage": "Passwords need to be at least 8 characters long.",
                "time_took": time_task_took
            }
        }
    else:
        # Generate a salt for the password
        salt = bcrypt.gensalt()
        # Hash the password using the salt
        hashed_password = str(bcrypt.hashpw(str(password).encode('utf-8'), salt)).replace("'", "\"")

        ipaddress = request.client.host
        return makeUser(username, hashed_password, email, ipaddress)


@router.post('/users/login/', tags=["user"])
async def loginAsUser(request: Request, username: str = Form(), password: str = Form()):
    # lowercase the username
    username = username.lower()

    client_host = request.client.host
    user_agent = Header(default=None)
    return login(username, password, user_agent, client_host)


# return "public-safe" user details
@router.get('/users/get/{username}', tags=["user"])
async def getPublicUserDetails(username):
    return getpublicuserinfo(username.lower())


# let the user logout. (delete their session token)
@router.post('/users/logout/', tags=["user"])
async def logoutAsUser(username: str = Form(), sessionkey: str = Form()):
    return logout(username, sessionkey)
