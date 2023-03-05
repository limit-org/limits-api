import meilisearch
from ..dbconfig import meilisearchConfig


# func for searching posts
def MSSearchPosts(searchterm: str, page: int):
    msdb = meilisearchConfig()[0]
    msdbkey = meilisearchConfig()[1]
    client = meilisearch.Client(msdb, msdbkey)

    index = client.index('posts')  # set index to posts
    result = index.search(searchterm, {
        'offset': page
    })  # search for {searchterm} on page {page}
    return result  # return search results


# func for searching for/about users
def MSSearchUsers(searchterm: str, page: int):
    msdb = meilisearchConfig()[0]
    msdbkey = meilisearchConfig()[1]
    client = meilisearch.Client(msdb, msdbkey)

    index = client.index('users')  # set index to users
    result = index.search(searchterm, {
        'offset': page
    })  # search for {searchterm} on page {page}
    return result  # return search results
