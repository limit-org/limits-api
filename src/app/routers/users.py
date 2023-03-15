from fastapi import APIRouter, Header, Form, Request
from pydantic import BaseModel
import bcrypt
import time

from functions.users.makeuser import makeUser
from functions.users.getpublicuserdetails import getpublicuserinfo
from functions.users.login import login
from functions.users.logout import logout
from functions.users.changepassword import changepwd
from functions.passwordstandards import CheckPassword
from functions.users.update import updateUsername
from functions.users.update import updateBio
from functions.users.update import updateEmailPublicity
from functions.users.update import updateUserAlias

router = APIRouter()


class User(BaseModel):
    username: str
    password: str
    email: str
    sessionkey: str


@router.post('/users/create/', tags=["user"], status_code=201)
async def create_user(request: Request, username: str = Form(), password: str = Form(), email: str = Form()):
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


@router.post('/users/login/', tags=["user"], status_code=200)
async def login_user(request: Request, username: str = Form(), password: str = Form()):
    # lowercase the username
    username = username.lower()

    client_host = request.client.host
    user_agent = Header(default=None)
    return await login(username, password, user_agent, client_host)


# return "public-safe" user details. that is stuff like user id, alias, username, email (if user chooses to share it)
@router.get('/users/get/{username}/', tags=["user"], status_code=200)
async def get_public_user_details(username):
    return await getpublicuserinfo(username.lower())


# let the user logout. (delete their session token)
@router.post('/users/logout/', tags=["user"], status_code=200)
async def logout_user(username: str = Form(), sessionkey: str = Form()):
    return await logout(username, sessionkey)


@router.put('/users/reset/password/', tags=["user"], status_code=200)
async def change_password(request: Request, username: str = Form(), password: str = Form(), newpass: str = Form()):
    client_host = request.client.host
    user_agent = Header(default=None)
    return await changepwd(username, password, newpass, client_host, user_agent)


@router.put('/users/update/username/', tags=["user"], status_code=200)
async def update_username(username: str = Form(), usersessionkey: str = Form(), newusername: str = Form()):
    return await updateUsername(username, usersessionkey, newusername)


@router.put('/users/update/bio/', tags=["user"], status_code=200)
async def update_bio(username: str = Form(), usersessionkey: str = Form(), newbio: str = Form()):
    return await updateBio(username, usersessionkey, newbio)


@router.put('/users/update/email/publicity/', tags=["user"], status_code=200)
async def update_email_publicity(username: str = Form(), usersessionkey: str = Form(), makeEmailPublic: bool = Form()):
    return await updateEmailPublicity(username, usersessionkey, makeEmailPublic)


@router.put('/users/update/alias/', tags=["user"], status_code=200)
async def update_email_publicity(username: str = Form(), usersessionkey: str = Form(), alias: str = Form()):
    return await updateUserAlias(username, usersessionkey, alias)
