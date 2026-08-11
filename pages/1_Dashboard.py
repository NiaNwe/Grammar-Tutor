import sqlite3

import pandas as pd
import streamlit as st

from src.db import DB_PATH, init_db


st.set_page_config(
    page_title="Grammar Coach Dashboard",
    layout="wide",
)

st.title("Grammar Coach Monitoring")

init_db()

connection = sqlite3.connect(DB_PATH)

conversations = pd.read_sql_query(
    """
    SELECT *
    FROM conversations
    ORDER BY timestamp
    """,
    connection,
)

feedback = pd.read_sql_query(
    """
    SELECT *
    FROM feedback
    ORDER BY timestamp
    """,
    connection,
)

connection.close()


if conversations.empty:
    st.info(
        "No conversations have been recorded yet."
    )
    st.stop()


conversations["timestamp"] = pd.to_datetime(
    conversations["timestamp"]
)

conversations["date"] = (
    conversations["timestamp"].dt.date
)


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total questions",
    len(conversations),
)

col2.metric(
    "Average response time",
    f"{conversations['response_time'].mean():.2f}s",
)

col3.metric(
    "Total tokens",
    int(conversations["total_tokens"].sum()),
)

positive_feedback = (
    feedback["feedback"].eq(1).sum()
    if not feedback.empty
    else 0
)

col4.metric(
    "Helpful ratings",
    int(positive_feedback),
)


st.subheader("1. Questions per day")

questions_per_day = (
    conversations
    .groupby("date")
    .size()
    .rename("questions")
)

st.line_chart(questions_per_day)


st.subheader("2. Average response time")

response_time_by_day = (
    conversations
    .groupby("date")["response_time"]
    .mean()
)

st.line_chart(response_time_by_day)


st.subheader("3. Tokens used per day")

tokens_by_day = (
    conversations
    .groupby("date")["total_tokens"]
    .sum()
)

st.bar_chart(tokens_by_day)


st.subheader("4. Questions by learner level")

questions_by_level = (
    conversations["learner_level"]
    .value_counts()
)

st.bar_chart(questions_by_level)


st.subheader("5. Tool calls per conversation")

tool_call_counts = (
    conversations["tool_calls"]
    .value_counts()
    .sort_index()
)

st.bar_chart(tool_call_counts)


st.subheader("6. User feedback")

if feedback.empty:
    st.info("No feedback received yet.")
else:
    feedback_counts = (
        feedback["feedback"]
        .map(
            {
                1: "Helpful",
                -1: "Not helpful",
            }
        )
        .value_counts()
    )

    st.bar_chart(feedback_counts)