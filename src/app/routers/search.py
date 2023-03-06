from fastapi import APIRouter

from functions.meilisearch.MSSearch import MSSearchPosts
from functions.meilisearch.MSSearch import MSSearchUsers

router = APIRouter()


@router.get('/search/posts', tags=["search"], status_code=200)
def searchPosts(searchterm: str, page: int):
    return MSSearchPosts(searchterm, page)


@router.get('/search/users', tags=["search"], status_code=200)
def searchUsers(searchterm: str, page: int):
    return MSSearchUsers(searchterm, page)
