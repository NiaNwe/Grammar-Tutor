import os

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

from src.knowledge_base import (
    build_text_index,
    build_vector_index,
    load_documents,
)


load_dotenv()

openai_client = OpenAI()

documents = load_documents()
text_index = build_text_index(documents)
vector_index = build_vector_index(documents)


BEST_BOOSTS = {
    "title": 2.0,
    "rule": 2.0,
    "explanation": 1.0,
    "keywords": 2.5,
    "incorrect_example": 3.0,
    "error_reason": 2.0,
}

DEFAULT_TOP_K = int(
    os.getenv("RETRIEVAL_TOP_K", "5")
)

RETRIEVAL_METHOD = os.getenv(
    "RETRIEVAL_METHOD",
    "hybrid",
)


def text_search(query, level=None, num_results=5):
    filter_dict = {}

    if level:
        filter_dict["level"] = level

    return text_index.search(
        query=query,
        filter_dict=filter_dict,
        boost_dict=BEST_BOOSTS,
        num_results=num_results,
    )


def embed_query(query):
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=query,
    )

    return np.array(
        response.data[0].embedding,
        dtype=np.float32,
    )


def vector_search(query, level=None, num_results=5):
    query_vector = embed_query(query)

    filter_dict = {}

    if level:
        filter_dict["level"] = level

    return vector_index.search(
        query_vector,
        filter_dict=filter_dict,
        num_results=num_results,
    )


def reciprocal_rank_fusion(
    result_lists,
    num_results=5,
    rrf_constant=60,
):
    scores = {}
    documents_by_id = {}

    for result_list in result_lists:
        for rank, document in enumerate(
            result_list,
            start=1,
        ):
            document_id = document["id"]

            documents_by_id[document_id] = document

            scores[document_id] = (
                scores.get(document_id, 0.0)
                + 1 / (rrf_constant + rank)
            )

    ranked_ids = sorted(
        scores,
        key=scores.get,
        reverse=True,
    )

    return [
        documents_by_id[document_id]
        for document_id in ranked_ids[:num_results]
    ]


def hybrid_search(query, level=None, num_results=5):
    text_results = text_search(
        query,
        level=level,
        num_results=10,
    )

    vector_results = vector_search(
        query,
        level=level,
        num_results=10,
    )

    return reciprocal_rank_fusion(
        [text_results, vector_results],
        num_results=num_results,
    )


def search_grammar_rules(
    query,
    level=None,
    num_results=DEFAULT_TOP_K,
):
    if RETRIEVAL_METHOD == "keyword":
        return text_search(
            query,
            level=level,
            num_results=num_results,
        )

    if RETRIEVAL_METHOD == "vector":
        return vector_search(
            query,
            level=level,
            num_results=num_results,
        )

    if RETRIEVAL_METHOD == "hybrid":
        return hybrid_search(
            query,
            level=level,
            num_results=num_results,
        )

    raise ValueError(
        f"Unknown retrieval method: "
        f"{RETRIEVAL_METHOD}"
    )