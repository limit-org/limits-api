import meilisearch
from ..dbconfig import meilisearchConfig
from fastapi import HTTPException
import traceback

from .functions.log import logErrorToDB


# func for searching posts
async def MSSearchPosts(searchterm: str, page: int):
    try:
        msdb = meilisearchConfig()[0]
        msdbkey = meilisearchConfig()[1]
        client = meilisearch.Client(msdb, msdbkey)

        index = client.index('posts')  # set index to posts
        result = index.search(searchterm, {
            'offset': page
        })  # search for {searchterm} on page {page}
        return result  # return search results
    except (Exception, meilisearch.client.MeiliSearchError):
        await logErrorToDB(str(traceback.format_exc()))
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "1",
                "http_code": "500",
                "error": "Meilisearch post searching error.",
                "time_took": 0
            }
        )


# func for searching for/about users
async def MSSearchUsers(searchterm: str, page: int):
    try:
        msdb = meilisearchConfig()[0]
        msdbkey = meilisearchConfig()[1]
        client = meilisearch.Client(msdb, msdbkey)

        index = client.index('users')  # set index to users
        result = index.search(searchterm, {
            'offset': page
        })  # search for {searchterm} on page {page}
        return result  # return search results
    except (Exception, meilisearch.client.MeiliSearchError):
        await logErrorToDB(str(traceback.format_exc()))
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "1",
                "http_code": "500",
                "error": "Meilisearch user searching error.",
                "time_took": 0
            }
        )
