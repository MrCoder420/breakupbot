import os
import json
from app import chain_with_history

print("--- Testing Breakup Bot RAG ---")
try:
    response = chain_with_history.invoke(
        {"input": "I am missing them so much right now."},
        config={"configurable": {"session_id": "test_script_001"}}
    )
    print("Bot Response:")
    print(response)
except Exception as e:
    print(f"Error testing bot: {e}")
