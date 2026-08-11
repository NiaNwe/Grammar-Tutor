import uuid

from src.db import (
    init_db,
    save_conversation,
    save_feedback,
)
init_db()

conversation_id = str(uuid.uuid4())


import streamlit as st

from src.agent import run_agent


st.set_page_config(
    page_title="Grammar Coach",
    page_icon="📘",
    layout="centered",
)

st.title("Grammar Coach")
st.caption(
    "An A1 to B1 English grammar tutor "
    "grounded in a curated knowledge base."
)


level = st.sidebar.selectbox(
    "Learner level",
    options=["A1", "A2", "B1"],
)


if "messages" not in st.session_state:
    st.session_state.messages = []

for i, message in enumerate(st.session_state.messages):
    print(
        i,
        message.get("role"),
        message.get("conversation_id"),
    )


for message_index, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant":
            source_ids = message.get(
                "source_ids",
                [],
            )

            if source_ids:
                with st.expander("Grammar cards used"):
                    for source_id in source_ids:
                        st.code(source_id)

            message_conversation_id = message.get(
                "conversation_id"
            )

            if message_conversation_id:
                feedback_columns = st.columns(2)

                with feedback_columns[0]:
                    if st.button(
                        "Helpful",
                        key=f"helpful-{message_conversation_id}-{message_index}",
                    ):
                        save_feedback(
                            message_conversation_id,
                            1,
                        )
                        st.success("Feedback saved")

                with feedback_columns[1]:
                    if st.button(
                        "Not helpful",
                        key=f"not-helpful-{message_conversation_id}-{message_index}",
                    ):
                        save_feedback(
                            message_conversation_id,
                            -1,
                        )
                        st.success("Feedback saved")

question = st.chat_input(
    "Ask a grammar question or enter a sentence to check"
)
if question:
                
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    new_conversation_id = str(uuid.uuid4())

    with st.chat_message("assistant"):
        with st.spinner(
                "Searching the grammar knowledge base..."
            ):
            result = run_agent(
                    question=question,
                    level=level,
                    )

    st.markdown(result["answer"])

    if result["source_ids"]:
        with st.expander(
                "Grammar cards used"
             ):
                for source_id in result[
                    "source_ids"]:
                    st.code(source_id)
                
    save_conversation(
        conversation_id=conversation_id,
        question=question,
        learner_level=level,
        result=result,)
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["answer"],
            "source_ids": result["source_ids"],
            "conversation_id": conversation_id,
        }
    )

    st.rerun()