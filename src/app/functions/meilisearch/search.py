import meilisearch
from ..dbconfig import meilisearchConfig


def MSSearchPosts(searchterm):
    msdb = meilisearchConfig()[0]
    msdbkey = meilisearchConfig()[1]
    client = meilisearch.Client(msdb, msdbkey)

    index = client.index('posts')
    result = index.search(searchterm)
    return result
