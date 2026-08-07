import os
from pathlib import Path

import numpy as np
import pandas as pd
from minsearch import Index, VectorSearch


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = Path(
    os.getenv(
        "GRAMMAR_DATA_PATH",
        PROJECT_ROOT / "data" / "grammar_rules.csv",
    )
)

EMBEDDING_PATH = Path(
    os.getenv(
        "GRAMMAR_EMBEDDING_PATH",
        PROJECT_ROOT
        / "data"
        / "grammar-document-embeddings.npy",
    )
)


TEXT_FIELDS = [
    "title",
    "rule",
    "explanation",
    "correct_example_1",
    "correct_example_2",
    "incorrect_example",
    "corrected_example",
    "error_reason",
    "keywords",
]

KEYWORD_FIELDS = [
    "id",
    "level",
    "category",
    "topic",
]


def load_documents():
    dataframe = pd.read_csv(DATA_PATH)
    dataframe = dataframe.fillna("")

    return dataframe.to_dict(orient="records")


def build_text_index(documents):
    search_index = Index(
        text_fields=TEXT_FIELDS,
        keyword_fields=KEYWORD_FIELDS,
    )

    search_index.fit(documents)

    return search_index


def build_vector_index(documents):
    if not EMBEDDING_PATH.exists():
        raise FileNotFoundError(
            "Document embeddings are missing. "
            "Run the embedding notebook first."
        )

    vectors = np.load(EMBEDDING_PATH)

    search_index = VectorSearch(
        keyword_fields=[
            "level",
            "category",
            "topic",
        ]
    )

    search_index.fit(vectors, documents)

    return search_index