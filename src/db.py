import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DB_PATH = Path(
    os.getenv(
        "APP_DB_PATH",
        PROJECT_ROOT / "runtime" / "app.db",
    )
)


def get_connection():
    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def init_db():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                question TEXT NOT NULL,
                learner_level TEXT NOT NULL,
                answer TEXT NOT NULL,
                model_used TEXT NOT NULL,
                response_time REAL NOT NULL,
                input_tokens INTEGER NOT NULL,
                output_tokens INTEGER NOT NULL,
                total_tokens INTEGER NOT NULL,
                source_ids TEXT NOT NULL,
                tool_calls INTEGER NOT NULL,
                timestamp TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback (
                conversation_id TEXT PRIMARY KEY,
                feedback INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (
                    conversation_id
                )
                REFERENCES conversations(id)
            )
            """
        )


def save_conversation(
    conversation_id,
    question,
    learner_level,
    result,
):
    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO conversations (
                id,
                question,
                learner_level,
                answer,
                model_used,
                response_time,
                input_tokens,
                output_tokens,
                total_tokens,
                source_ids,
                tool_calls,
                timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                conversation_id,
                question,
                learner_level,
                result["answer"],
                result["model_used"],
                result["response_time"],
                result["input_tokens"],
                result["output_tokens"],
                result["total_tokens"],
                json.dumps(
                    result["source_ids"]
                ),
                result["tool_calls"],
                timestamp,
            ),
        )


def save_feedback(
    conversation_id,
    feedback,
):
    if feedback not in [1, -1]:
        raise ValueError(
            "Feedback must be 1 or -1"
        )

    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO feedback (
                conversation_id,
                feedback,
                timestamp
            )
            VALUES (?, ?, ?)
            ON CONFLICT(conversation_id)
            DO UPDATE SET
                feedback = excluded.feedback,
                timestamp = excluded.timestamp
            """,
            (
                conversation_id,
                feedback,
                timestamp,
            ),
        )