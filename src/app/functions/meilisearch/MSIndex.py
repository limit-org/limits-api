import meilisearch_python_async

from ..dbconfig import meilisearchConfig


async def IndexPost(postid: int, authorid: int, authorusername: str, title: str, textcontent: str,
                    media: str, timestamp: int, topic: str, edited: bool):
    msdb = meilisearchConfig()[0]
    msdbkey = meilisearchConfig()[1]
    async with meilisearch_python_async.Client(msdb, msdbkey) as client:
        await client.index('posts').update_documents([{
            'id': int(postid),
            'authorid': str(authorid),
            'author': authorusername,
            'title': title,
            'content': textcontent,
            'media': media,
            'timestamp': str(timestamp),
            'topic': topic,
            'edited': edited
        }],
            'id'  # primary key for MS posts.
            # this is so MS can understand how many posts there are and how to identify one from another.
        )


async def IndexUser(userid, username, alias, email, unixtimejoined, bio, modnotes, trusted, mod, badges, official):
    msdb = meilisearchConfig()[0]
    msdbkey = meilisearchConfig()[1]
    async with meilisearch_python_async.Client(msdb, msdbkey) as client:
        await client.index('users').update_documents([{
            'id': int(userid),  # a meilisearch user id is
            'username': str(username),
            'alias': str(alias),
            'email': str(email),
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
