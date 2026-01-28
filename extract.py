import json
import os
import time
from dotenv import load_dotenv
from groq import Groq
from tqdm import tqdm

from schemas import ShipmentExtraction
from prompts import BASE_PROMPT_V1, BASE_PROMPT_V2

# ------------------ SETUP ------------------
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ------------------ LOAD FILES ------------------
with open("emails_input.json") as f:
    emails = json.load(f)

with open("port_codes_reference.json") as f:
    ports = json.load(f)

# Build lookup tables
CODE_TO_NAME = {p["code"]: p["name"] for p in ports}

import re

def clean_llm_json(raw: str) -> str:
    if not raw:
        return ""

    # Extract JSON inside ``` ``` if present
    match = re.search(r"\{[\s\S]*\}", raw)
    if match:
        return match.group(0).strip()

    return raw.strip()

# ------------------ LLM CALL WITH RETRY ------------------
def call_llm(prompt, retries=3):
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Retry {attempt + 1} failed: {e}")
            time.sleep(2 ** attempt)
    return None


# ------------------ EXTRACTION LOOP ------------------
results = []
PORT_CODE_LIST = ", ".join(sorted(CODE_TO_NAME.keys()))


for email in tqdm(emails, desc="Extracting emails"):
    prompt = BASE_PROMPT_V2.format(
        subject=email["subject"],
        body=email["body"],
        port_codes=PORT_CODE_LIST
    )

    raw = call_llm(prompt)
    if email["id"] == "EMAIL_001":
        print(f"\n=== EMAIL_001 LLM Response ===\n{raw}\n")

    if raw is None:
        print(f"⚠️ {email['id']}: LLM returned None (API failure)")

    if raw is None:
        # Hard failure → null everything
        results.append(
            ShipmentExtraction(
                id=email["id"],
                product_line=None,
                origin_port_code=None,
                origin_port_name=None,
                destination_port_code=None,
                destination_port_name=None,
                incoterm=None,
                cargo_weight_kg=None,
                cargo_cbm=None,
                is_dangerous=False
            ).model_dump()
        )
        continue

    try:
        cleaned = clean_llm_json(raw)
        data = json.loads(cleaned)
    except Exception as e:
        print(f"JSON parse failed for {email['id']}: {e}")
        data = {}


    # ------------------ POST-PROCESSING ------------------
    origin_code = data.get("origin_port_code")
    dest_code = data.get("destination_port_code")

    extraction = ShipmentExtraction(
        id=email["id"],
        product_line=data.get("product_line"),
        origin_port_code=origin_code,
        origin_port_name=CODE_TO_NAME.get(origin_code),
        destination_port_code=dest_code,
        destination_port_name=CODE_TO_NAME.get(dest_code),
        incoterm=data.get("incoterm"),
        cargo_weight_kg=round(data["cargo_weight_kg"], 2) if isinstance(data.get("cargo_weight_kg"), (int, float)) else None,
        cargo_cbm=round(data["cargo_cbm"], 2) if isinstance(data.get("cargo_cbm"), (int, float)) else None,
        is_dangerous=data.get("is_dangerous", False),
    )

    results.append(extraction.model_dump())

# ------------------ SAVE OUTPUT ------------------
with open("output.json", "w") as f:
    json.dump(results, f, indent=2)

print("Extraction completed. Output written to output.json")
