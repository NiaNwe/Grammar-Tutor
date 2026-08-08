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


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant":
            source_ids = message.get(
                "source_ids",
                [],
            )

            if source_ids:
                with st.expander(
                    "Grammar cards used"
                ):
                    for source_id in source_ids:
                        st.code(source_id)


question = st.chat_input(
    "Ask a grammar question or enter "
    "a sentence to check"
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
                    "source_ids"
                ]:
                    st.code(source_id)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["answer"],
            "source_ids": result["source_ids"],
        }
    )