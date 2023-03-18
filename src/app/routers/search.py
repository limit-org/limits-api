from fastapi import APIRouter

from functions.meilisearch.MSSearch import MSSearchPosts
from functions.meilisearch.MSSearch import MSSearchUsers

router = APIRouter()


@router.get('/search/posts/', tags=["search"], status_code=200)
async def search_posts(query: str, page: int):
    return await MSSearchPosts(query, page)


@router.get('/search/users/', tags=["search"], status_code=200)
async def search_users(query: str, page: int):
    return await MSSearchUsers(query, page)
