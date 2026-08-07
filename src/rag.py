import os
from time import perf_counter

from dotenv import load_dotenv
from openai import OpenAI

from src.retrieval import search_grammar_rules


load_dotenv()

openai_client = OpenAI()

DEFAULT_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.4-mini",
)


PROMPT_TEMPLATE = """
You are a patient English grammar tutor for adult learners.

Answer using only the CONTEXT.

When correcting a sentence:

1. Show the corrected sentence.
2. Explain what changed.
3. State the relevant rule simply.
4. Give one additional example.
5. Give one short practice question.

Do not invent rules that are absent from the context.
Use British English.
Use language suitable for level {level}.

QUESTION:
{question}

CONTEXT:
{context}
""".strip()


ENTRY_TEMPLATE = """
Rule ID: {id}
Level: {level}
Category: {category}
Topic: {topic}
Title: {title}
Rule: {rule}
Explanation: {explanation}
Correct example 1: {correct_example_1}
Correct example 2: {correct_example_2}
Incorrect example: {incorrect_example}
Corrected example: {corrected_example}
Error reason: {error_reason}
""".strip()


def build_prompt(query, search_results, level):
    context = "\n\n".join(
        ENTRY_TEMPLATE.format(**document)
        for document in search_results
    )

    return PROMPT_TEMPLATE.format(
        question=query,
        level=level,
        context=context,
    )


def call_llm(prompt, model=DEFAULT_MODEL):
    response = openai_client.responses.create(
        model=model,
        input=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    usage = response.usage

    return {
        "answer": response.output_text,
        "input_tokens": usage.input_tokens,
        "output_tokens": usage.output_tokens,
        "total_tokens": usage.total_tokens,
    }


def rag(query, level="A1", model=DEFAULT_MODEL):
    started_at = perf_counter()

    search_results = search_grammar_rules(
        query=query,
        level=level,
    )

    prompt = build_prompt(
        query=query,
        search_results=search_results,
        level=level,
    )

    llm_result = call_llm(
        prompt=prompt,
        model=model,
    )

    response_time = perf_counter() - started_at

    return {
        **llm_result,
        "model_used": model,
        "response_time": response_time,
        "source_ids": [
            document["id"]
            for document in search_results
        ],
    }