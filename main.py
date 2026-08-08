from src.agent import run_agent


result = run_agent(
    question=(
        "Can you explain present continous?"
    ),
    level="A2",
)

print(result["answer"])
print()
print("Sources:", result["source_ids"])
print("Tool calls:", result["tool_calls"])
print("Trajectory:", result["tool_trajectory"])
print("Tokens:", result["total_tokens"])