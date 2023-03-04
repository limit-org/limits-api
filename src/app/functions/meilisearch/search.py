import meilisearch
from ..dbconfig import meilisearchConfig


def MSSearchPosts(searchterm: str, page: int):
    msdb = meilisearchConfig()[0]
    msdbkey = meilisearchConfig()[1]
    client = meilisearch.Client(msdb, msdbkey)

    index = client.index('posts')
    result = index.search(searchterm, {
        'offset': page
    })
    return result


def MSSearchUsers(searchterm: str, page: int):
    msdb = meilisearchConfig()[0]
    msdbkey = meilisearchConfig()[1]
    client = meilisearch.Client(msdb, msdbkey)

    index = client.index('users')
    result = index.search(searchterm, {
        'offset': page
    })
    return result
