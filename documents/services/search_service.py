# documents/services/search_service.py
from functools import lru_cache

from django.conf import settings
from pymongo import MongoClient

from documents.models import Document

DEFAULT_LIMIT = 5


@lru_cache(maxsize=1)  # create the client once and reuse it
def _get_client():
    return MongoClient(settings.DATABASES["default"]["HOST"])


def _get_collection():
    db_name = settings.DATABASES["default"]["NAME"]
    return _get_client()[db_name][Document._meta.db_table]


def _get_index_name():
    index_name = settings.VECTOR_INDEX_NAME
    if not index_name:
        raise ValueError("VECTOR_INDEX_NAME is not set. Add it to your .env file.")
    return index_name


def semantic_search(question: str, limit: int = DEFAULT_LIMIT) -> list:
    """Search with a plain-text question.

    There is no query vector to pass in: MongoDB embeds the question
    with the index's model.
    """
    pipeline = [
        {
            "$vectorSearch": {
                "index": _get_index_name(),
                "path": "abstract",
                "query": question,
                "numCandidates": limit * 20,
                "limit": limit,
            }
        },
        {
            "$project": {
                "_id": 0,
                "document_number": 1,
                "title": 1,
                "abstract": 1,
                "source_url": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        },
    ]
    return list(_get_collection().aggregate(pipeline))