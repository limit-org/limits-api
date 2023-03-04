import meilisearch

from ..dbconfig import meilisearchConfig


async def IndexPost(postid: int, authorid: int, authorusername: str, title: str, textcontent: str,
                    media: str, timestamp: int, topic: str):
    msdb = meilisearchConfig()[0]
    msdbkey = meilisearchConfig()[1]
    client = meilisearch.Client(msdb, msdbkey)

    client.index('posts').add_documents([{
        'id': int(postid),
        'authorid': str(authorid),
        'author': authorusername,
        'title': title,
        'content': textcontent,
        'media': media,
        'timestamp': str(timestamp),
        'topic': topic
    }],
        'id'  # primary key for MS posts.
        # this is so MS can understand how many posts there are and how to identify one from another.
    )
