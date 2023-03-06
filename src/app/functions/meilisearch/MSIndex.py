import meilisearch

from ..dbconfig import meilisearchConfig


async def IndexPost(postid: int, authorid: int, authorusername: str, title: str, textcontent: str,
                    media: str, timestamp: int, topic: str):
    msdb = meilisearchConfig()[0]
    msdbkey = meilisearchConfig()[1]
    client = meilisearch.Client(msdb, msdbkey)

    client.index('posts').update_documents([{
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


async def IndexUser(userid, username, alias, unixtimejoined, bio, modnotes, trusted, mod, badges, official):
    msdb = meilisearchConfig()[0]
    msdbkey = meilisearchConfig()[1]
    client = meilisearch.Client(msdb, msdbkey)

    client.index('users').update_documents([{
        'id': int(userid),  # a meilisearch user id is
        'username': str(username),
        'alias': str(alias),
        'unixtime_joined': unixtimejoined,
        'bio': bio,
        'modnotes': modnotes,
        'is_trusted': trusted,
        'is_moderator': mod,
        'badges': badges,
        'is_official': official
    }],
        'id'  # primary key for MS users.
        # this is so MS can understand how many users there are and how to identify one from another.
    )
