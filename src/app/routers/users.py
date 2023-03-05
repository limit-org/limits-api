from fastapi import APIRouter, Header, Form, Request
from pydantic import BaseModel
import bcrypt
import time

from functions.users.makeuser import makeUser
from functions.users.getpublicuserdetails import getpublicuserinfo
from functions.users.login import login
from functions.users.logout import logout
from functions.users.changepassword import changepwd
from functions.users.update import updateUser
from functions.passwordstandards import CheckPassword

router = APIRouter()


class User(BaseModel):
    username: str
    password: str
    email: str
    sessionkey: str


@router.post('/users/create/', tags=["user"])
async def createuser(request: Request, username: str = Form(), password: str = Form(), email: str = Form()):
    time_task_started = time.time()

    # lowercase the username
    username = username.lower()

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

    # does password conform to standards?
    pwc = CheckPassword(plainTextPass=password, username=username)
    if pwc != 0:
        time_task_took = time.time() - time_task_started
        return {
            "detail": {
                "error_code": "1",
                "error": str(pwc["err"]),
                "UIMessage": str(pwc["ui"]),
                "time_took": time_task_took
            }
        }

    # Generate a salt for the password
    salt = bcrypt.gensalt()
    # Hash the password using the salt
    hashed_password = str(bcrypt.hashpw(str(password).encode('utf-8'), salt)).replace("'", "\"")

    ipaddress = request.client.host
    return await makeUser(username, hashed_password, email, ipaddress, time_task_started)


@router.post('/users/login/', tags=["user"])
async def loginAsUser(request: Request, username: str = Form(), password: str = Form()):
    # lowercase the username
    username = username.lower()

    client_host = request.client.host
    user_agent = Header(default=None)
    return await login(username, password, user_agent, client_host)


# return "public-safe" user details. that is stuff like user id, username, email (if user chooses to share it)
@router.get('/users/get/{username}/', tags=["user"])
async def getPublicUserDetails(username):
    return await getpublicuserinfo(username.lower())


# let the user logout. (delete their session token)
@router.post('/users/logout/', tags=["user"])
async def logoutAsUser(username: str = Form(), sessionkey: str = Form()):
    return await logout(username, sessionkey)


@router.put('/users/resetpassword/', tags=["user"])
async def changepassword(request: Request, username: str = Form(), password: str = Form(), newpass: str = Form()):
    client_host = request.client.host
    user_agent = Header(default=None)
    return await changepwd(username, password, newpass, client_host, user_agent)


@router.put('/users/updateprofile/', tags=["user"])
async def updateprofile(username: str = Form(), usersessionkey: str = Form(), newusername: str = Form(),
                        newbio: str = Form(), emailispublic: str = Form(), newalias: str = Form()):
    return await updateUser(username, usersessionkey, newusername, newbio, emailispublic, newalias)
