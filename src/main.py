from src.rag import rag


result = rag(
    query="Why is 'she go to school' incorrect?",
    level="A1",
)

print(result["answer"])
print()
print("Sources:", result["source_ids"])
print("Tokens:", result["total_tokens"])
print("Time:", result["response_time"])