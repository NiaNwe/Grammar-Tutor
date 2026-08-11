from src.agent import run_agent


result = run_agent(
    question=(
        "Can you explain present continous?"
    ),
    level="A2",
)

save_conversation(
    conversation_id=conversation_id,
    question=question,
    learner_level=level,
    result=result,
)

print(result["answer"])
print()
print("Sources:", result["source_ids"])
print("Tool calls:", result["tool_calls"])
print("Trajectory:", result["tool_trajectory"])
print("Tokens:", result["total_tokens"])