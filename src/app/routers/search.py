from fastapi import APIRouter
from fastapi import Form
from pydantic import BaseModel

from functions.meilisearch.search import MSSearchPosts
from functions.dbconfig import config


router = APIRouter()


@router.get('/search/posts', tags=["search"])
def searchPosts(searchterm):
    return MSSearchPosts(searchterm)
