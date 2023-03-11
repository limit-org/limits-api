from fastapi import APIRouter

from functions.meilisearch.MSSearch import MSSearchPosts
from functions.meilisearch.MSSearch import MSSearchUsers

router = APIRouter()


@router.get('/search/posts/', tags=["search"], status_code=200)
async def searchPosts(searchterm: str, page: int):
    return await MSSearchPosts(searchterm, page)


@router.get('/search/users/', tags=["search"], status_code=200)
async def searchUsers(searchterm: str, page: int):
    return await MSSearchUsers(searchterm, page)
