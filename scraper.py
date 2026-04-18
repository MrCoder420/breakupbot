import os
import json
import time
import requests
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configuration
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
OUTPUT_FILE = 'knowledge.json'
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Target configuration structure: [url, source_name, category]
# We use some placeholder URLs targeting the requested domains.
# You can add or replace these URLs with specific articles as needed.
TARGETS = [
    # Stages of Grief
    {
        "url": "https://www.verywellmind.com/five-stages-of-grief-4175361",
        "source": "Verywell Mind",
        "category": "Stages of Grief"
    },
    # No Contact Logic
    {
        "url": "https://www.psychologytoday.com/us/blog/the-specular-image/202102/why-the-no-contact-rule-is-so-effective",
        "source": "Psychology Today",
        "category": "No Contact Rules"
    },
    {
        "url": "https://www.healthline.com/health/no-contact-rule",
        "source": "Healthline",
        "category": "No Contact Rules"
    },
    # CBT Tools
    {
        "url": "https://www.helpguide.org/articles/grief/coping-with-a-breakup-or-divorce.htm",
        "source": "HelpGuide.org",
        "category": "CBT Tools & Coping"
    },
    {
        "url": "https://www.psychologytoday.com/us/blog/the-mindful-self-express/201603/the-science-heartbreak", 
        "source": "Psychology Today",
        "category": "Biological Explanations"
    },
    # Moving On / Healing
    {
        "url": "https://www.healthline.com/health/how-to-get-over-a-breakup",
        "source": "Healthline",
        "category": "Moving On"
    },
    {
        "url": "https://www.verywellmind.com/how-to-cope-with-a-breakup-4174037",
        "source": "Verywell Mind",
        "category": "Moving On"
    },
    # Advanced CBT/DBT specific
    {
        "url": "https://www.psychologytoday.com/us/blog/fixing-families/202203/how-cognitive-behavioral-therapy-can-help-after-breakup",
        "source": "Psychology Today",
        "category": "Clinical CBT"
    },
    {
        "url": "https://cbtprofessionals.com.au/using-cbt-to-cope-with-a-relationship-break-up/",
        "source": "CBT Professionals",
        "category": "Clinical CBT"
    },
    # DBT/Distress Tolerance
    {
        "url": "https://medium.com/@drtaranixon/using-dbt-skills-to-survive-a-breakup-7764f699313a",
        "source": "Medium / Dr. Tara Nixon",
        "category": "Clinical DBT"
    },
    {
        "url": "https://www.choosingtherapy.com/dbt-for-breakups/",
        "source": "Choosing Therapy",
        "category": "Clinical DBT"
    }
]

def fetch_page_content(url):
    """Fetches the page and extracts text from <p> tags."""
    try:
        print(f"Fetching: {url}")
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'lxml')
        
        # Extract all paragraph tags to avoid headers and footer noise
        paragraphs = soup.find_all('p')
        texts = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
        
        # Join the texts with double newlines for clear separation before chunking
        full_text = "\n\n".join(texts)
        return full_text
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def process_and_save():
    # Initialize the LangChain text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False,
    )

    all_chunks = []

    for target in TARGETS:
        raw_text = fetch_page_content(target["url"])
        if not raw_text:
            print(f"-> Warning: Got no text for {target['url']}")
            continue
            
        print("-> Extracting chunks...")
        # Split the text into LangChain strings based on chunk settings
        chunks = text_splitter.split_text(raw_text)
        
        for chunk in chunks:
            # Check to avoid tiny or empty chunks
            if len(chunk) < 50:
                continue
                
            # Create our structured data object
            chunk_data = {
                "text": chunk,
                "category": target["category"],
                "source": target["source"]
            }
            all_chunks.append(chunk_data)
            
        # Be slightly polite to servers by adding a short delay
        time.sleep(1)

    # Output to JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=4, ensure_ascii=False)
        
    print(f"\n✅ Processing complete! Generated {len(all_chunks)} knowledge chunks.")
    print(f"✅ Data saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    print("Starting Breakup Bot knowledge extraction...")
    process_and_save()
