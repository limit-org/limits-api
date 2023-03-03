import random

import meilisearch
import json

from ..dbconfig import meilisearchConfig


async def IndexPost(postid, authorid, authorusername, title, textcontent, media, timestamp, topic):
    msdb = meilisearchConfig()[0]
    msdbkey = meilisearchConfig()[1]
    client = meilisearch.Client(msdb, msdbkey)

    index = client.index('posts')

    document = [
        {'id': postid, 'author_id': authorid, 'author_username': authorusername, 'post_title': title,
         'text_content': textcontent, 'media_ids': media, 'upload_timestamp': timestamp, 'topic': topic,
         },
    ]

    index.add_documents(document)
