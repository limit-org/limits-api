from fastapi import APIRouter

from functions.meilisearch.search import MSSearchPosts

router = APIRouter()


@router.get('/search/posts', tags=["search"])
def searchPosts(searchterm):
    return MSSearchPosts(searchterm)
