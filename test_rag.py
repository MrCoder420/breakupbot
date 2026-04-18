import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings

from personality import get_chat_prompt

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

print("Initializing Langchain RAG Test (Skipping MongoDB to verify core logic)...")

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

vectorstore = Chroma(embedding_function=embeddings, persist_directory="./chroma_db")
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

def get_context(query: str) -> str:
    docs = retriever.invoke(query)
    return "\n\n".join([doc.page_content for doc in docs])

prompt = get_chat_prompt()
llm = ChatGroq(model="llama3-8b-8192", temperature=0.4, api_key=GROQ_API_KEY)

chain = (
    {
        "context": lambda x: get_context(x["input"]),
        "chat_history": lambda x: [],
        "input": lambda x: x["input"]
    }
    | prompt
    | llm
    | StrOutputParser()
)

test_msg = "I feel so empty without them. What are the stages of grief?"
print(f"Sending message: '{test_msg}'")
response = chain.invoke({"input": test_msg})
print("\n=== Bot Response ===")
print(response)
print("====================")
