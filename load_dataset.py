"""
load_dataset.py
---------------
Downloads 3 HuggingFace datasets relevant to breakup recovery and emotional
support, filters/formats them, and merges into knowledge.json for the Chroma
RAG vector store.

Datasets:
  1. Amod/mental_health_counseling_conversations  -- licensed counselor Q&A
  2. ShenLab/MentalChat16K                        -- depression / grief support
  3. facebook/empathetic_dialogues                -- empathetic conversations
"""

import json
import os
import sys

# Force UTF-8 output on Windows so emojis don't crash the terminal
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from datasets import load_dataset
from langchain_text_splitters import RecursiveCharacterTextSplitter

# -- Configuration -----------------------------------------------------------
OUTPUT_FILE   = "knowledge.json"
CHUNK_SIZE    = 600
CHUNK_OVERLAP = 80

# Keywords to filter broad datasets down to breakup/grief/relationship topics
RELATIONSHIP_KEYWORDS = [
    "breakup", "break up", "broke up", "relationship", "ex-partner",
    "ex-boyfriend", "ex-girlfriend", " ex ", "heartbreak", "heartbroken",
    "divorce", "dating", "lonely", "loneliness", "moving on", "move on",
    "grief", "attachment", "rejection", "dumped", "cheating", "cheated",
    "toxic relationship", "love", "missing him", "missing her", "miss my",
    "depression", "depressed", "hopeless", "hurt", "crying",
    "feel alone", "feel empty", "worthless", "self-worth",
    "heal", "healing", "coping", "recover", "recovery",
]

# Emotions in EmpatheticDialogues that map to post-breakup feelings
EMPATHY_EMOTIONS = {
    "heartbroken", "sad", "lonely", "devastated", "depressed",
    "disappointed", "grief", "betrayed", "hopeless", "jealous",
    "disgusted", "anxious", "terrified", "angry", "furious",
    "caring", "content", "hopeful", "nostalgic", "sentimental",
    "trusting", "faithful",
}

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
)


def has_keyword(text: str) -> bool:
    t = text.lower()
    return any(kw in t for kw in RELATIONSHIP_KEYWORDS)


def chunk_and_tag(text: str, category: str, source: str) -> list:
    chunks = splitter.split_text(text)
    return [
        {"text": c, "category": category, "source": source}
        for c in chunks
        if len(c.strip()) > 40
    ]


# ----------------------------------------------------------------------------
# Dataset 1 -- Amod/mental_health_counseling_conversations
# Schema: { Context: str, Response: str }
# ----------------------------------------------------------------------------
def load_amod() -> list:
    print("\n[1/3] Loading Amod/mental_health_counseling_conversations ...")
    ds = load_dataset("Amod/mental_health_counseling_conversations", split="train")
    results = []
    for row in ds:
        ctx  = row.get("Context", "")
        resp = row.get("Response", "")
        if has_keyword(ctx) or has_keyword(resp):
            text = f"Person: {ctx}\nCounselor: {resp}"
            results.extend(chunk_and_tag(
                text,
                "Professional Counseling",
                "Amod/mental_health_counseling_conversations (HuggingFace)"
            ))
    print(f"    OK: {len(results)} chunks extracted.")
    return results


# ----------------------------------------------------------------------------
# Dataset 2 -- ShenLab/MentalChat16K
# ----------------------------------------------------------------------------
def load_mentalchat() -> list:
    print("\n[2/3] Loading ShenLab/MentalChat16K ...")
    ds = load_dataset("ShenLab/MentalChat16K", split="train")
    results = []
    for row in ds:
        question = row.get("input") or row.get("instruction") or row.get("question") or ""
        answer   = row.get("output") or row.get("response") or row.get("answer") or ""
        if not question and not answer:
            continue
        text = f"Person: {question}\nSupport: {answer}"
        results.extend(chunk_and_tag(
            text,
            "Mental Health Support",
            "ShenLab/MentalChat16K (HuggingFace)"
        ))
    print(f"    OK: {len(results)} chunks extracted.")
    return results


# ----------------------------------------------------------------------------
# Dataset 3 -- facebook/empathetic_dialogues
# ----------------------------------------------------------------------------
def load_empathetic_dialogues() -> list:
    # facebook/empathetic_dialogues uses a deprecated loading script.
    # We use 'Esmat24/empathetic_dialogues' which is a Parquet-based mirror.
    print("\n[3/3] Loading Esmat24/empathetic_dialogues (Parquet mirror) ...")
    ds = load_dataset("Esmat24/empathetic_dialogues", split="train")

    convs = {}
    for row in ds:
        cid     = row["conv_id"]
        emotion = row.get("context", "").lower()
        if emotion not in EMPATHY_EMOTIONS:
            continue
        if cid not in convs:
            convs[cid] = {"emotion": emotion, "prompt": row.get("prompt", ""), "turns": []}
        convs[cid]["turns"].append(row.get("utterance", ""))

    results = []
    for cid, data in convs.items():
        if len(data["turns"]) < 2:
            continue
        dialogue = "\n".join(
            f"{'Friend' if i % 2 == 0 else 'Supporter'}: {t}"
            for i, t in enumerate(data["turns"])
        )
        full_text = (
            f"[Emotion: {data['emotion'].capitalize()}]\n"
            f"Situation: {data['prompt']}\n"
            f"{dialogue}"
        )
        results.extend(chunk_and_tag(
            full_text,
            "Empathetic Dialogue",
            "facebook/empathetic_dialogues (HuggingFace)"
        ))

    print(f"    OK: {len(results)} chunks extracted.")
    return results


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("  Breakup Bot -- HuggingFace RAG Dataset Builder")
    print("=" * 60)

    all_new_chunks = []

    try:
        all_new_chunks += load_amod()
    except Exception as e:
        print(f"    WARNING: Amod dataset failed: {e}")

    try:
        all_new_chunks += load_mentalchat()
    except Exception as e:
        print(f"    WARNING: MentalChat16K failed: {e}")

    try:
        all_new_chunks += load_empathetic_dialogues()
    except Exception as e:
        print(f"    WARNING: EmpatheticDialogues failed: {e}")

    # Load previously scraped chunks so we don't wipe them
    existing = []
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            try:
                existing = json.load(f)
            except json.JSONDecodeError:
                existing = []

    # De-duplicate on text content
    seen = {c["text"] for c in existing}
    deduped_new = [c for c in all_new_chunks if c["text"] not in seen]

    final = existing + deduped_new

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print(f"  Done!")
    print(f"  New chunks added   : {len(deduped_new)}")
    print(f"  Total in knowledge : {len(final)}")
    print(f"  Saved to           : {OUTPUT_FILE}")
    print("=" * 60)
    print("\n  Next step: run  python ingest_chroma.py  to rebuild the vector store.")


if __name__ == "__main__":
    main()
