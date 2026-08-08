import json
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


SEARCH_TOOL = {
    "type": "function",
    "name": "search_grammar_rules",
    "description": (
        "Search the English grammar knowledge base. "
        "Use this before explaining a grammar rule, "
        "correcting a learner sentence, or creating "
        "a rule-based practice question."
    ),
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "A concise search query describing "
                    "the grammar rule or learner mistake."
                ),
            }
        },
        "required": ["query"],
        "additionalProperties": False,
    },
}


AGENT_INSTRUCTIONS = """
You are an English grammar tutoring agent for adult learners.

You have a tool named search_grammar_rules.

Rules:

1. Search the knowledge base before explaining or correcting grammar.
2. You may search again using improved wording if the first results are poor.
3. Base grammar explanations only on tool results.
4. Use British English.
5. Keep explanations suitable for the learner's CEFR level.
6. When correcting a sentence:
   - show the correction
   - explain what changed
   - state the rule
   - provide one example
   - provide one short practice question
7. If the knowledge base does not contain the rule, say so.
8. Do not make more tool calls than necessary.
""".strip()

def run_agent(
    question,
    level="A1",
    model=DEFAULT_MODEL,
    max_steps=3,
):
    started_at = perf_counter()

    input_items = [
        {
            "role": "user",
            "content": (
                f"Learner level: {level}\n"
                f"Question: {question}"
            ),
        }
    ]

    total_input_tokens = 0
    total_output_tokens = 0

    tool_trajectory = []
    source_ids = set()

    for _ in range(max_steps):
        response = openai_client.responses.create(
            model=model,
            instructions=AGENT_INSTRUCTIONS,
            input=input_items,
            tools=[SEARCH_TOOL],
        )

        if response.usage:
            total_input_tokens += (
                response.usage.input_tokens
            )
            total_output_tokens += (
                response.usage.output_tokens
            )

        input_items.extend(response.output)

        function_calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]

        if not function_calls:
            response_time = (
                perf_counter() - started_at
            )

            return {
                "answer": response.output_text,
                "model_used": model,
                "response_time": response_time,
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
                "total_tokens": (
                    total_input_tokens
                    + total_output_tokens
                ),
                "source_ids": sorted(source_ids),
                "tool_calls": len(tool_trajectory),
                "tool_trajectory": tool_trajectory,
            }

        for function_call in function_calls:
            arguments = json.loads(
                function_call.arguments
            )

            search_query = arguments["query"]

            results = search_grammar_rules(
                query=search_query,
                level=level,
                num_results=5,
            )

            retrieved_ids = [
                document["id"]
                for document in results
            ]

            source_ids.update(retrieved_ids)

            tool_trajectory.append(
                {
                    "tool": "search_grammar_rules",
                    "query": search_query,
                    "result_ids": retrieved_ids,
                }
            )

            input_items.append(
                {
                    "type": "function_call_output",
                    "call_id": function_call.call_id,
                    "output": json.dumps(results),
                }
            )

    response_time = perf_counter() - started_at

    return {
        "answer": (
            "I could not complete the request "
            "within the allowed number of searches."
        ),
        "model_used": model,
        "response_time": response_time,
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "total_tokens": (
            total_input_tokens
            + total_output_tokens
        ),
        "source_ids": sorted(source_ids),
        "tool_calls": len(tool_trajectory),
        "tool_trajectory": tool_trajectory,
    }