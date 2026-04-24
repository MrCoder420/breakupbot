"""
ingest_chroma.py
----------------
Reads knowledge.json, selects a balanced high-quality subset, and builds
the Chroma vector store in ./chroma_db.

Why subset? Chroma with all-MiniLM-L6-v2 on CPU processes ~100 docs/sec.
5,000 docs = ~50 seconds. 114,000 docs = ~20 minutes. The bot only retrieves
top-k=3 at a time, so 5k well-chosen chunks are just as effective.
"""

import json
import os
import sys
import random
import shutil

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Load HF_TOKEN from .env before importing anything that might call HF
from dotenv import load_dotenv
load_dotenv()

import os
os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HF_TOKEN", "")

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

KNOWLEDGE_FILE   = "knowledge.json"
CHROMA_DIR       = "./chroma_db"
MAX_CHUNKS       = 5000   # sweet spot: fast ingest + great retrieval quality
SEED             = 42


def balanced_sample(data: list, total: int, seed: int) -> list:
    """
    Sample `total` chunks, keeping proportional representation from each
    source/category so no single dataset drowns out the others.
    """
    from collections import defaultdict
    groups: dict[str, list] = defaultdict(list)
    for item in data:
        key = item.get("category", "unknown")
        groups[key].append(item)

    rng = random.Random(seed)
    result = []
    cats = list(groups.keys())
    per_cat = max(1, total // len(cats))

    for cat in cats:
        pool = groups[cat]
        rng.shuffle(pool)
        result.extend(pool[:per_cat])

    # Fill any remaining slots from the overall pool
    rng.shuffle(data)
    seen_texts = {c["text"] for c in result}
    for item in data:
        if len(result) >= total:
            break
        if item["text"] not in seen_texts:
            result.append(item)
            seen_texts.add(item["text"])

    rng.shuffle(result)
    return result[:total]


def main():
    print("=" * 60)
    print("  Breakup Bot -- Chroma Vector Store Ingest")
    print("=" * 60)

    if not os.path.exists(KNOWLEDGE_FILE):
        print(f"ERROR: {KNOWLEDGE_FILE} not found. Run load_dataset.py first.")
        return

    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"\nTotal chunks in knowledge.json : {len(data)}")

    # Select a fast, balanced subset
    subset = balanced_sample(data, MAX_CHUNKS, SEED)
    print(f"Selected balanced subset       : {len(subset)}")

    # Show category breakdown
    from collections import Counter
    cats = Counter(c.get("category", "unknown") for c in subset)
    for cat, cnt in cats.items():
        print(f"  {cat}: {cnt}")

    docs = [
        Document(
            page_content=item["text"],
            metadata={
                "source":   item.get("source",   "unknown"),
                "category": item.get("category", "unknown"),
            }
        )
        for item in subset
        if item.get("text", "").strip()
    ]

    from langchain_huggingface import HuggingFaceEndpointEmbeddings
    embeddings = HuggingFaceEndpointEmbeddings(
        huggingfacehub_api_token=os.getenv("HF_TOKEN"),
        model="BAAI/bge-small-en-v1.5"
    )

    # Wipe old DB
    if os.path.exists(CHROMA_DIR):
        print(f"Clearing old Chroma DB ...")
        shutil.rmtree(CHROMA_DIR)

    print(f"Ingesting {len(docs)} documents into Chroma (this takes ~1-2 min) ...")

    BATCH = 1000
    vectorstore = None
    for i in range(0, len(docs), BATCH):
        batch = docs[i : i + BATCH]
        batch_num  = i // BATCH + 1
        total_batches = (len(docs) - 1) // BATCH + 1
        print(f"  Batch {batch_num}/{total_batches}  ({i+1}-{min(i+BATCH, len(docs))} docs)")
        if vectorstore is None:
            vectorstore = Chroma.from_documents(
                documents=batch,
                embedding=embeddings,
                persist_directory=CHROMA_DIR,
            )
        else:
            vectorstore.add_documents(batch)

    count = vectorstore._collection.count()
    print(f"\nChroma DB built at   : {CHROMA_DIR}")
    print(f"Vectors stored       : {count}")
    print("=" * 60)
    print("  Done! Start the app with:  uvicorn app:app --reload")
    print("=" * 60)


if __name__ == "__main__":
    main()
