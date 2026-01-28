BASE_PROMPT_V1 = """
You are an information extraction system for freight forwarding pricing enquiries.

Extract shipment details from the email below.

STRICT RULES:
- Return ONLY valid JSON
- Do NOT add explanations
- Missing or unknown values → null
- Default incoterm = FOB
- Incoterms must be one of:
  FOB, CIF, CFR, EXW, DDP, DAP, FCA, CPT, CIP, DPU
- Dangerous goods:
  true if mentions DG, dangerous, hazardous, IMO, IMDG
  false if mentions non-DG, non-hazardous, not dangerous
  false if not mentioned
- If multiple shipments are mentioned, extract ONLY the FIRST one
- Body content overrides subject if there is conflict

Email:
Subject: {subject}
Body: {body}

Return JSON in this exact schema:
{{
  "product_line": string or null,
  "origin_port_code": string or null,
  "destination_port_code": string or null,
  "incoterm": string or null,
  "cargo_weight_kg": number or null,
  "cargo_cbm": number or null,
  "is_dangerous": boolean
}}
"""

BASE_PROMPT_V2 = """
You are an information extraction system for freight forwarding pricing enquiries.

You MUST follow the business rules strictly.

--------------------
BUSINESS RULES
--------------------
- All shipments are SEA LCL
- If destination port is in India (UN/LOCODE starts with IN) → product_line = pl_sea_import_lcl
- If origin port is in India → product_line = pl_sea_export_lcl
- Use UN/LOCODE 5-letter port codes ONLY from this allowed list
- If a port is not in the list, return null
- If incoterm is missing or ambiguous → FOB
- Body overrides subject
- If multiple shipments exist → extract ONLY the FIRST
- Dangerous goods:
  true if mentions DG, dangerous, hazardous, IMO, IMDG
  false if mentions non-DG, non-hazardous, not dangerous
  false if not mentioned

--------------------
ALLOWED PORT CODES
--------------------
{port_codes}

--------------------
EMAIL
--------------------
Subject: {subject}
Body: {body}

--------------------
OUTPUT
--------------------
Return ONLY valid JSON:
{{
  "product_line": string or null,
  "origin_port_code": string or null,
  "destination_port_code": string or null,
  "incoterm": string or null,
  "cargo_weight_kg": number or null,
  "cargo_cbm": number or null,
  "is_dangerous": boolean
}}
"""

