"""All workshop content lives here. Pages in app_pages/ are generic renderers.

To build a new lab, edit EVENT, NAMES, DATA and SECTIONS; no page code changes needed.
"""

EVENT = {
    "title": "Alberta Energy Operations: Raw Data to AI Agent with AISQL",
    "subtitle": "Build an AI agent on raw energy operations documents, measure it, then make it faster, cheaper and more accurate by preprocessing with AISQL",
    "page_icon": ":material/oil_barrel:",
    "date": "Wednesday, November 25, 2026",
    "venue_name": "The Ampersand",
    "venue_address": "112 4 Ave SW",
    "venue_city": "Calgary, AB",
    "duration": "75 min hands-on",
    "event_link": "https://www.snowflake.com/event/calgary-coco-hands-on-lab-20261125/",
    "signup_link": "https://signup.snowflake.com/?t=762eba0e2cc36aa13cd1dfb526fa91d94d7ad354f9e8c2e2ac8348dff61e12e4&cloud=aws&region=us-east-2",
    "signup_short_link": "https://tinyurl.com/yyc-coco-hol",
    "recommended_region": "US East 2 (Ohio)",
    "scenario": """An Alberta energy operator runs five facilities: **Scotford Upgrader, Horizon Oil Sands, Kearl Lake Operations, Christina Lake SAGD and Keystone Terminal Calgary**, shipping product over 20 pipelines. Pipeline shipments are tracked in clean tables, but most operational knowledge is written by people: **incident reports** from field and control room staff, **Alberta Energy Regulator (AER) inspection notes**, and **shipper and refinery emails** in English and French.

Leadership wants an AI agent that can answer questions like *"How many hours of downtime did equipment failures cost us this year?"* The facts are all there, but they're buried in free text, with every facility and number written a different way.
""",
    "agenda": [
        ("9:00 – 9:15", "Welcome & Check-In", "Grab a coffee, connect to Wi-Fi, and start your Snowflake trial signup (see Getting Started)."),
        ("9:15 – 9:30", "Opening & Context Setting", "Why AI agents need good data, and where AISQL fits in the pipeline."),
        ("9:30 – 10:45", "Hands-On Lab", "Sections 1–5 in this guide."),
        ("10:45 – 11:00", "Wrap-Up & Next Steps", "Review the before/after results and how to apply this to your own data."),
        ("11:00 – 11:30", "Networking", ""),
    ],
}

NAMES = {
    "db": "ENERGY_YYC_AISQL",
    "schema": "ENERGY_OPS",
    "wh": "ENERGY_AISQL_WH",
    "stage": "DATA",
    "base_sv": "ENERGY_OPS_SV",
    "enriched_sv": "ENERGY_OPS_ENRICHED_SV",
    "search": "RAW_DOCS_SEARCH",
    "baseline_agent": "ENERGY_AGENT_BASELINE",
    "aisql_agent": "ENERGY_AGENT_AISQL",
    "eval_table": "ENERGY_EVAL_DATA",
}
N = NAMES
FQ = f"{N['db']}.{N['schema']}"

DATA = {
    "zip_name": "alberta_energy_data.zip",
    "zip_url": "https://github.com/sfc-gh-mkeith/coco-hol-aisql-calgary-nov-25/raw/main/workshop_guide/data/alberta_energy_data.zip",
    "tables": [
        ("FACILITIES", 5, "structured", "The five facilities: Scotford Upgrader, Horizon Oil Sands, Kearl Lake Operations, Christina Lake SAGD, Keystone Terminal Calgary"),
        ("PIPELINES", 20, "structured", "Pipelines, their operators and product types"),
        ("PIPELINE_SHIPMENTS", 400, "structured", "Each pipeline batch: facility, pipeline, destination, nominated vs delivered barrels"),
        ("INCIDENT_REPORTS_RAW", 300, "raw text", "Free-text incident reports. Facility, severity, downtime and cost are only in the text, written with inconsistent names and formats"),
        ("AER_INSPECTIONS_RAW", 120, "raw text", "Alberta Energy Regulator inspector notes. Outcome and penalty amount are only in the text"),
        ("SHIPPER_EMAILS_RAW", 150, "raw text", "Shipper and refinery emails in English and French. Topic and urgency are only in the text"),
        ("EVAL_QUESTIONS", 12, "evaluation", "12 test questions with known correct answers, used to score both agents"),
    ],
}
TABLE_LIST = ", ".join(t[0] for t in DATA["tables"])
NUM_TABLES = len(DATA["tables"])
TOTAL_ROWS = sum(t[1] for t in DATA["tables"])

EVAL_EXAMPLES = [
    "How many incidents were reported at Horizon Oil Sands?",
    "What is the total downtime in hours caused by equipment failures across all facilities?",
    "How many AER inspections resulted in a penalty, and what was the total penalty amount?",
    "Which facility was incident INC-0042 at, and what was its severity?",
]

FACILITY_NAMES = "Scotford Upgrader, Horizon Oil Sands, Kearl Lake Operations, Christina Lake SAGD, Keystone Terminal Calgary"
FACILITY_ALIASES = ("Scotford Upgrader (aliases: Scotford, SCTF, Shell Scotford, the Fort Saskatchewan upgrader), "
                    "Horizon Oil Sands (Horizon, HRZN, CNRL Horizon, the Horizon mine), "
                    "Kearl Lake Operations (Kearl, KRLK, Imperial Kearl, the Kearl site), "
                    "Christina Lake SAGD (Christina Lake, CHLK, Cenovus CL, the Christina SAGD plant), "
                    "Keystone Terminal Calgary (Keystone, KYST, TC Calgary terminal, the Calgary terminal)")

# --------------------------------------------------------------------------
# Sections. Each step is one of:
#   {"type": "prompt", "id", "title", "text", "explain"?}
#   {"type": "markdown", "body"}
#   {"type": "info", "body"} / {"type": "warning", "body"}
#   {"type": "copy_list", "title", "items"}  individually copyable questions
# --------------------------------------------------------------------------

SECTIONS = [
    {
        "num": 1,
        "group": "Part 1: The baseline",
        "nav": "Setup & Data Load",
        "icon": ":material/database:",
        "title": "Setup & Data Load",
        "time": "9:30 – 9:45",
        "duration": "15 min",
        "building": f"Database, warehouse and {NUM_TABLES} tables of energy operations data (structured + raw text)",
        "technologies": [
            {"name": "Database, Schema & Stage", "description": "Containers for your tables and an internal stage to hold uploaded files.", "icon": "database"},
            {"name": "INFER_SCHEMA + COPY INTO", "description": "Detect column types from CSV files and bulk-load them into tables.", "icon": "table_chart"},
            {"name": "Virtual Warehouse", "description": "The compute that runs your SQL, loads and AISQL functions.", "icon": "memory"},
        ],
        "steps": [
            {"type": "prompt", "id": "Prompt 1.1", "title": "Create Database, Schema, Stage & Warehouse", "text": f"""Create the following Snowflake objects for our Alberta Energy Operations AISQL workshop:

1. A database called {N['db']}
2. A schema called {N['schema']} inside that database
3. A stage called {N['stage']} in {FQ} with a directory table and server side encryption
4. A warehouse called {N['wh']} (size MEDIUM, auto-suspend after 60 seconds, auto-resume enabled)
5. Set the session context to use these objects

Execute all SQL and confirm each object was created.""",
             "explain": f"""
```sql
CREATE DATABASE {N['db']};
CREATE SCHEMA {FQ};
CREATE STAGE {FQ}.{N['stage']}
  DIRECTORY = (ENABLE = TRUE)
  ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE');
CREATE WAREHOUSE {N['wh']}
  WAREHOUSE_SIZE = 'MEDIUM' AUTO_SUSPEND = 60 AUTO_RESUME = TRUE;
```
"""},
            {"type": "markdown", "body": f"""
**Before running Prompt 1.2, download the CSV files and upload them to the `{N['stage']}` stage:**

1. Download the zip file: [{DATA['zip_name']}]({DATA['zip_url']})
2. Unzip it on your computer to get the {NUM_TABLES} CSV files.
3. In Snowsight, use the Horizon Catalog to browse to `{FQ}.{N['stage']}` and upload all CSV files.
4. Then copy the prompt below into Cortex Code and execute.
"""},
            {"type": "prompt", "id": "Prompt 1.2", "title": "Create and Load Tables from CSV", "text": f"""In {FQ}, the {NUM_TABLES} CSV files have been uploaded to an internal stage called {N['stage']}.

For all {NUM_TABLES} tables ({TABLE_LIST}):

1. Create a file format (CSV with PARSE_HEADER=TRUE, FIELD_OPTIONALLY_ENCLOSED_BY='"')
2. Create the tables with appropriate column types inferred from the data. Ensure to convert the column names to uppercase.
3. Load the data

Use CREATE TABLE with INFER_SCHEMA from a stage and then COPY INTO them. The key requirement is that all {NUM_TABLES} tables are created and populated.

Execute all SQL.""",
             "explain": "\n".join(f"- **{t[0]}** ({t[1]} rows, {t[2]}): {t[3]}" for t in DATA["tables"])},
            {"type": "prompt", "id": "Prompt 1.3", "title": "Look at the Raw Text", "text": f"""In {FQ}:

1. Show every table name and its row count, ordered by row count descending.
2. Show 5 sample rows from INCIDENT_REPORTS_RAW, AER_INSPECTIONS_RAW and SHIPPER_EMAILS_RAW.
3. In a short summary, point out what makes the raw text hard to analyze: how facilities are named, how downtime and costs are written, and which languages appear.""",
             "explain": f"""
You should see ~{TOTAL_ROWS:,} rows across {NUM_TABLES} tables. Notice that the same facility appears as *Horizon Oil Sands*, *HRZN*, *CNRL Horizon*, *the Horizon mine*; downtime appears as *8h*, *~4 hrs*, *approx. 660 minutes*; costs as *$130,700*, *713.4k CAD*, *roughly $113K*. Some shipper emails are in French. AER inspection notes reference facilities only by their AER licence number.

**This is the problem the rest of the lab is about.** None of these facts are columns yet, so no SQL can count or sum them.
"""},
        ],
        "concepts": [
            {"term": "Structured vs. raw data", "definition": "Structured data lives in typed columns that SQL can filter and aggregate. Raw data (reports, emails, notes) holds the same facts inside free text, where SQL can't reach them directly."},
            {"term": "INFER_SCHEMA", "definition": "A table function that detects column names and types from staged files."},
        ],
        "built": [f"{N['db']}.{N['schema']} with the {N['stage']} stage and {N['wh']} warehouse", f"{NUM_TABLES} tables loaded (~{TOTAL_ROWS:,} rows)"],
    },
    {
        "num": 2,
        "group": "Part 1: The baseline",
        "nav": "Baseline Agent",
        "icon": ":material/smart_toy:",
        "title": "Baseline Agent on Raw Data",
        "time": "9:45 – 10:00",
        "duration": "15 min",
        "building": "A semantic view, a search service over raw documents, and a first agent",
        "intro": "This is the most common way teams start: point an agent at the tables you have and a search index over your documents. It works for lookups, but watch what happens with questions that need counting or adding up facts buried in text.",
        "technologies": [
            {"name": "Semantic View", "description": "A business-friendly layer over tables that Cortex Analyst uses to turn questions into SQL.", "icon": "schema"},
            {"name": "Cortex Search", "description": "Hybrid vector + keyword search over text. Returns the most relevant chunks for a question.", "icon": "search"},
            {"name": "Cortex Agent", "description": "Plans, picks tools (Analyst, Search), runs them and writes the answer.", "icon": "smart_toy"},
        ],
        "steps": [
            {"type": "prompt", "id": "Prompt 2.1", "title": "Semantic View over the Structured Tables", "text": f"""/semantic_studio Create a semantic view called {N['base_sv']} in {FQ} over FACILITIES, PIPELINES and PIPELINE_SHIPMENTS.

- Add clear descriptions and synonyms for facilities (e.g. Horizon Oil Sands is also called HRZN or CNRL Horizon)
- Add a fact/metric for delivery shortfall barrels = NOMINATED_BARRELS - DELIVERED_BARRELS
- Relationships: PIPELINE_SHIPMENTS to FACILITIES on FACILITY_ID, PIPELINE_SHIPMENTS to PIPELINES on PIPELINE_ID
- When defining relationships, do not set join_type. The left_table must be the fact (many) side and the right_table the dimension (one) side, and the dimension tables must declare primary_key columns.

Use this format for relationships:
relationships:
  - name: shipments_to_facilities
    left_table: PIPELINE_SHIPMENTS
    right_table: FACILITIES
    relationship_columns:
      - left_column: FACILITY_ID
        right_column: FACILITY_ID

Deploy it and test it with: "What is the average delivery shortfall for shipments from Kearl Lake Operations?\"""",
             "explain": "The semantic view only covers the **structured** tables. The three `_RAW` tables can't go in a semantic view in a useful way: their facts aren't columns."},
            {"type": "prompt", "id": "Prompt 2.2", "title": "Cortex Search over the Raw Documents", "text": f"""In {FQ}:

1. Create a view RAW_DOCUMENTS that unions the three raw text tables into one shape: DOC_ID, DOC_TYPE ('incident_report', 'aer_inspection', 'shipper_email'), DOC_DATE, SOURCE (submitted_by / aer_licence / from_company) and DOC_TEXT (for emails, combine subject and body).
2. Create a Cortex Search service called {N['search']} on RAW_DOCUMENTS, searching DOC_TEXT, with DOC_ID, DOC_TYPE, DOC_DATE and SOURCE as attributes. Use warehouse {N['wh']}, TARGET_LAG = '1 hour' and embedding model snowflake-arctic-embed-l-v2.0.
3. Test it with SEARCH_PREVIEW for "H2S alarm at Christina Lake".""",
             "explain": "Search is great at *finding* relevant documents, but it returns a limited number of top results. It cannot read all 300 incident reports and add up their downtime."},
            {"type": "prompt", "id": "Prompt 2.3", "title": "Create the Baseline Agent", "text": f"""In {FQ}, create a Cortex Agent called {N['baseline_agent']}:

- Orchestration model: auto
- Tools: Cortex Analyst on the {N['base_sv']} semantic view (facilities, pipelines, shipment barrels) and Cortex Search on {N['search']} (incident reports, AER inspections, shipper emails)
- Instructions: You are an Alberta energy operations analyst. Use the semantic view for facility, pipeline and shipment volume questions. Use search for incidents, AER inspections and shipper emails. Always give a direct numeric answer when asked for counts or totals.
- Add sample questions: "Which pipeline operator had the most shipments?", "{EVAL_EXAMPLES[0]}"

Then ask the agent these two questions and show its answers and which tools it used:
1. "Which pipeline operator had the most shipments this year?"
2. "{EVAL_EXAMPLES[0]}\"""",
             "explain": "The first question goes to Cortex Analyst and is exact. For the second, the agent can only count the incidents that search returned, so the number is usually wrong, and the agent may not tell you."},
            {"type": "info", "body": f"You can also chat with the agent in Snowsight: **AI & ML → Agents → {N['baseline_agent']}**. Open the response details to see which tools it called and how long each step took."},
        ],
        "concepts": [
            {"term": "Top-k retrieval", "definition": "Search returns the k most relevant chunks, not every matching document. It's fine for 'find me the report about X', but questions like 'how many' or 'total cost' would need every document read."},
            {"term": "Tool routing", "definition": "The agent decides which tool to call from the tool descriptions and its instructions."},
        ],
        "built": [f"{N['base_sv']} semantic view (structured tables)", f"{N['search']} Cortex Search service over 570 raw documents", f"{N['baseline_agent']}, the baseline agent"],
    },
    {
        "num": 3,
        "group": "Part 1: The baseline",
        "nav": "Evaluate the Baseline",
        "icon": ":material/fact_check:",
        "title": "Evaluate the Baseline",
        "time": "10:00 – 10:10",
        "duration": "10 min",
        "building": "An evaluation dataset and a scored baseline run (accuracy, latency, tokens)",
        "intro": "To prove the AISQL version is better, you first need numbers for the baseline. Cortex Agent Evaluations run every test question through the agent and use an LLM judge to score each answer against the known correct answer. Each run also records duration and token usage.",
        "technologies": [
            {"name": "Cortex Agent Evaluations", "description": "Batch-run an agent over a dataset and score it with system metrics like answer correctness.", "icon": "fact_check"},
            {"name": "LLM-as-judge", "description": "A judge model compares each agent answer to the ground truth and scores it.", "icon": "gavel"},
            {"name": "AI Observability", "description": "Traces for every run: tool calls, duration and token counts, queryable with SQL.", "icon": "monitoring"},
        ],
        "steps": [
            {"type": "prompt", "id": "Prompt 3.1", "title": "Build the Evaluation Dataset", "text": f"""In {FQ}, create a table {N['eval_table']} (INPUT_QUERY VARCHAR, GROUND_TRUTH VARIANT) from EVAL_QUESTIONS.

- INPUT_QUERY = QUESTION
- GROUND_TRUTH = PARSE_JSON of an object with one key "ground_truth_output". Its value is a plain-language rubric: "The correct answer is <EXPECTED_ANSWER>. Numbers within ±5% are acceptable. An answer that gives a different number, or says it cannot determine the answer, is incorrect."

Use PARSE_JSON (not OBJECT_CONSTRUCT) so the column is a VARIANT. Show all 12 rows.""",
             "explain": "The judge only sees what you put in `ground_truth_output`, so it's written as a short rubric with the literal expected value and a tolerance, as the evaluation docs recommend."},
            {"type": "prompt", "id": "Prompt 3.2", "title": "Run the Baseline Evaluation", "text": f"""Run a Cortex Agent evaluation of {FQ}.{N['baseline_agent']}:

- First run USE SCHEMA {FQ} (evaluations run in the session's schema)
- Dataset: create an evaluation dataset called ENERGY_EVAL_DS from {FQ}.{N['eval_table']} (query column INPUT_QUERY, ground truth column GROUND_TRUTH)
- Run name: baseline-run-1
- Metrics: answer_correctness and logical_consistency, both pinned to version v3
- Create a file format EVAL_YAML_FORMAT (TYPE=CSV, FIELD_DELIMITER=NONE, RECORD_DELIMITER='\\n', SKIP_HEADER=0, FIELD_OPTIONALLY_ENCLOSED_BY=NONE, ESCAPE_UNENCLOSED_FIELD=NONE) and a stage EVAL_CONFIG that uses it
- We cannot upload local files, so write the YAML to @EVAL_CONFIG/eval_baseline.yaml with COPY INTO @EVAL_CONFIG/eval_baseline.yaml FROM (SELECT $$<yaml>$$) using SINGLE=TRUE, HEADER=FALSE, OVERWRITE=TRUE and an uncompressed CSV file format with FIELD_DELIMITER=NONE
- Start the run with EXECUTE_AI_EVALUATION('START', ...)

Then check STATUS every 30 seconds until it is COMPLETED.""",
             "explain": "The run takes a few minutes (12 questions, each answered by the agent and then judged). While it runs, read ahead to Section 4."},
            {"type": "info", "body": f"**No-code alternative:** In Snowsight go to **AI & ML → Agents → {N['baseline_agent']} → Evaluations → Create evaluation run → Run an evaluation manually**. Choose `{N['eval_table']}` as the source table, `INPUT_QUERY` as input, and turn on *Answer correctness* with `GROUND_TRUTH`."},
            {"type": "prompt", "id": "Prompt 3.3", "title": "Read the Baseline Scorecard", "text": f"""Using SNOWFLAKE.LOCAL.GET_AI_EVALUATION_DATA('{N['db']}', '{N['schema']}', '{N['baseline_agent']}', 'CORTEX AGENT', 'baseline-run-1'):

1. For each question show: INPUT, a 150-character preview of OUTPUT, answer_correctness score, DURATION_MS, TOTAL_INPUT_TOKENS + TOTAL_OUTPUT_TOKENS.
2. Join to {FQ}.EVAL_QUESTIONS on question text to add QUESTION_TYPE and EXPECTED_ANSWER.
3. Summarize by QUESTION_TYPE: average correctness, average seconds per answer, average tokens per answer.
4. Save the per-question results to a table EVAL_RESULTS_BASELINE.""",
             "explain": "Expect the **structured** and **lookup** questions to score well. The **aggregate_text** questions (counts and totals over raw documents) usually score low, and they tend to be the slowest and most token-hungry, because the agent searches repeatedly and reasons over long text chunks."},
        ],
        "concepts": [
            {"term": "Answer correctness", "definition": "How closely the agent's final answer matches the ground truth, scored by an LLM judge."},
            {"term": "Metric version", "definition": "Pins the judge model and rubric so scores are comparable across runs. This lab uses v3 for both agents."},
            {"term": "Run-to-run variance", "definition": "Agents are non-deterministic, so the same dataset can score slightly differently on each run. Large gaps are signal; small ones may be noise."},
        ],
        "built": [f"{N['eval_table']} evaluation table and ENERGY_EVAL_DS dataset", "baseline-run-1 with correctness, latency and token metrics", "EVAL_RESULTS_BASELINE scorecard"],
    },
    {
        "num": 4,
        "group": "Part 2: Optimize with AISQL",
        "nav": "AISQL Pipeline",
        "icon": ":material/auto_awesome:",
        "title": "Preprocess with AISQL",
        "time": "10:10 – 10:30",
        "duration": "20 min",
        "building": "Enriched tables where every fact from the raw text is a typed, queryable column",
        "intro": "Instead of making the agent read raw text at question time, read it **once** in the pipeline. AISQL functions run inside SQL over every row, turning text into structured columns. After that, a count or total is plain SQL.",
        "technologies": [
            {"name": "AI_EXTRACT", "description": "Pull specific fields (facility, downtime, cost, penalty) out of text into a structured response.", "icon": "data_object"},
            {"name": "AI_CLASSIFY", "description": "Assign each row to one of a fixed set of categories (incident type, severity, email topic).", "icon": "category"},
            {"name": "AI_FILTER / AI_TRANSLATE / AI_AGG", "description": "Yes/no checks in natural language, translation, and summaries across many rows.", "icon": "translate"},
        ],
        "steps": [
            {"type": "prompt", "id": "Prompt 4.1", "title": "Try the AISQL Functions on a Few Rows", "text": f"""In {FQ}, on 5 rows of INCIDENT_REPORTS_RAW, show side by side:

1. AI_EXTRACT on REPORT_TEXT returning:
   - facility: "The facility where the incident happened (not a pipeline name). Answer exactly one of: {FACILITY_ALIASES}"
   - downtime_hours: downtime in hours as a number (convert minutes to hours)
   - cost_cad: estimated cost in CAD as a plain number (expand k/K to thousands)

2. AI_CLASSIFY on REPORT_TEXT into category. Pass each label as an object with 'label' and 'description', and set task_description to "Classify the root cause of this energy facility incident report":
   - equipment_failure: mechanical or electrical breakdown, trip, seal/bearing failure, controller error of plant equipment
   - weather: caused by weather or natural events: cold snap, blizzard, chinook wind, freezing rain, flooding, wildfire smoke
   - safety_injury: a worker or contractor was injured: slip, fall, twisted ankle
   - environmental: a spill, leak or release of a substance (bitumen, diesel, glycol, dilbit, produced water) to the environment
   - h2s_release: H2S alarm or H2S gas reading
   - pipeline_integrity: pipeline inspection anomaly, wall loss, pressure drop on a pipeline, dig verification

3. AI_CLASSIFY on REPORT_TEXT into severity, with label descriptions and task_description "Classify the severity the report author assigned, based on the severity wording in the text":
   - low: minor, low impact, Sev: Low, no real impact to production, low severity
   - medium: moderate impact, Sev: Medium, medium severity, noticeable curtailment
   - high: serious, Sev: High, high severity, significant production loss, major curtailment
   - critical: CRITICAL, Sev: Critical, critical severity, full facility shut-in, emergency response plan activated

Show the original text next to the extracted values so we can check them.""",
             "explain": f"""Example shape of the SQL:
```sql
SELECT report_id, report_text,
  AI_EXTRACT(
    text => report_text,
    responseFormat => {{
      'facility': 'Which facility? One of {FACILITY_NAMES}',
      'downtime_hours': 'Downtime in hours as a number',
      'cost_cad': 'Estimated cost in CAD as a number'
    }}
  ):response AS extracted,
  AI_CLASSIFY(report_text, ['low','medium','high','critical']):labels[0]::STRING AS severity
FROM {FQ}.INCIDENT_REPORTS_RAW
LIMIT 5;
```
"""},
            {"type": "prompt", "id": "Prompt 4.2", "title": "Build INCIDENTS_ENRICHED", "text": f"""In {FQ}, create a table INCIDENTS_ENRICHED from all rows of INCIDENT_REPORTS_RAW using exactly the same AI_EXTRACT and AI_CLASSIFY calls from the previous step (same facility alias list and the same label descriptions; do not simplify them).

Columns: REPORT_ID, SUBMITTED_AT, SUBMITTED_BY, FACILITY_ID (join the extracted facility name to FACILITIES.FACILITY_NAME), FACILITY_NAME, CATEGORY, SEVERITY, DOWNTIME_HOURS (FLOAT), COST_CAD (FLOAT), REPORT_TEXT. Strip any non-numeric characters before casting DOWNTIME_HOURS and COST_CAD.

Then show: row count, number of rows where FACILITY_ID, DOWNTIME_HOURS or COST_CAD is NULL, incidents per facility, and incidents per category and severity.""",
             "explain": "This is the one-time cost: the LLM reads each of the 300 reports once. Every question after this is a cheap SQL query instead of an LLM reading text."},
            {"type": "prompt", "id": "Prompt 4.3", "title": "Enrich Inspections and Emails", "text": f"""In {FQ}, create two more enriched tables:

1. INSPECTIONS_ENRICHED from AER_INSPECTIONS_RAW: INSPECTION_ID, AER_LICENCE, INSPECTED_AT, FACILITY_ID (via FACILITIES on AER_LICENCE), FOCUS_AREA and PENALTY_CAD (AI_EXTRACT, 0 if no penalty), OUTCOME (AI_CLASSIFY: compliant, penalty, suspension, corrective_action), INSPECTOR_NOTES.

2. EMAILS_ENRICHED from SHIPPER_EMAILS_RAW:
   - EMAIL_ID, RECEIVED_AT, FROM_COMPANY, BODY
   - LANGUAGE: AI_CLASSIFY on BODY into 'en' or 'fr'
   - BODY_EN: AI_TRANSLATE BODY from 'fr' to 'en' when LANGUAGE = 'fr', otherwise keep BODY
   - TOPIC: AI_CLASSIFY on BODY_EN with label descriptions and task_description "Classify what this shipper email is about":
     - delay: a shipment or batch is late, held, apportioned or missed its cycle
     - quality: product off-spec, BS&W, water or sediment, quality complaint
     - billing: invoice, tariff, fees or charges problem
     - documentation: missing or requested paperwork: lot tickets, custody transfer confirmation, certificates
     - compliment: praise or thanks
   - IS_URGENT: AI_FILTER(PROMPT('Does the sender explicitly say this is urgent or that they need an answer today? Requests like "please advise when you can" are not urgent. Email: {{0}}', BODY_EN))
   - FACILITY_ID: AI_EXTRACT the facility the email is about, using the same facility alias list as INCIDENTS_ENRICHED, then join to FACILITIES.FACILITY_NAME

Show row counts, NULL FACILITY_ID counts, and a sample of 5 rows from each.""",
             "explain": "AI_TRANSLATE normalizes French emails to English before classification, so one set of labels works for both languages. AI_FILTER returns a real BOOLEAN you can filter on."},
            {"type": "prompt", "id": "Prompt 4.4", "title": "What Did the Pipeline Cost?", "text": f"""In {FQ}:

1. Query SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AISQL_USAGE_HISTORY for today, grouped by FUNCTION_NAME and MODEL_NAME, showing total TOKENS and TOKEN_CREDITS. This is the actual billed cost of the pipeline. If it returns no rows yet, say that ACCOUNT_USAGE views can lag and use the estimate from step 2.
2. As a rough lower-bound estimate, use AI_COUNT_TOKENS('ai_complete', 'llama3.1-70b', <text>) to count the tokens in REPORT_TEXT (x3 functions), INSPECTOR_NOTES (x2) and email BODY (x4). AI_COUNT_TOKENS does not support ai_extract or ai_filter, so this is a proxy that leaves out each function's built-in system prompt. Compare it with step 1 and explain the gap.
3. Use AI_AGG over INCIDENTS_ENRICHED.REPORT_TEXT where SEVERITY = 'critical' to write a 3-bullet summary of the main causes of critical incidents.""",
             "explain": "Keep this number: it's the **one-time** cost of preprocessing. In Section 5 you'll compare it with the **per-question** savings of the AISQL agent."},
            {"type": "info", "body": "**In production** you wouldn't rebuild these tables by hand. Wrap the same SELECTs in Dynamic Tables with incremental refresh (or a stream + task), so only new reports go through the LLM as they arrive."},
        ],
        "concepts": [
            {"term": "Shift-left AI", "definition": "Run the LLM once per document at ingest time, instead of once per question at query time. Repeated questions get faster and cheaper, and aggregates become exact."},
            {"term": "Normalization", "definition": "Mapping HRZN, CNRL Horizon and the Horizon mine to FACILITY_ID F002 means every join and GROUP BY is reliable."},
        ],
        "built": ["INCIDENTS_ENRICHED (300 rows)", "INSPECTIONS_ENRICHED (120 rows)", "EMAILS_ENRICHED (150 rows, translated, classified, urgency-flagged)", "A one-time cost estimate for the pipeline"],
    },
    {
        "num": 5,
        "group": "Part 2: Optimize with AISQL",
        "nav": "AISQL Agent & Compare",
        "icon": ":material/compare_arrows:",
        "title": "AISQL Agent & the Before/After",
        "time": "10:30 – 10:45",
        "duration": "15 min",
        "building": "A second agent over the enriched data, a second evaluation run, and the cost/speed comparison",
        "technologies": [
            {"name": "Semantic View (enriched)", "description": "The enriched tables become first-class facts and dimensions with relationships to facilities.", "icon": "schema"},
            {"name": "Cortex Agent", "description": "Same instructions and tools, but now aggregate questions resolve to a single SQL query.", "icon": "smart_toy"},
            {"name": "Evaluation Compare", "description": "Snowsight shows runs side by side, per question, with score and duration changes.", "icon": "compare_arrows"},
        ],
        "steps": [
            {"type": "prompt", "id": "Prompt 5.1", "title": "Enriched Semantic View", "text": f"""/semantic_studio Create a semantic view called {N['enriched_sv']} in {FQ} that includes everything in {N['base_sv']} plus INCIDENTS_ENRICHED, INSPECTIONS_ENRICHED and EMAILS_ENRICHED.

- Metrics: incident count, total and average DOWNTIME_HOURS, total COST_CAD, inspection count, total PENALTY_CAD, email count, urgent email count
- Dimensions: CATEGORY, SEVERITY, OUTCOME, FOCUS_AREA, TOPIC, LANGUAGE, IS_URGENT, month of SUBMITTED_AT
- Relationships from each enriched table to FACILITIES on FACILITY_ID
- Same relationship rules as before: no join_type, left_table = fact (many) side, right_table = dimension (one) side, primary_key on dimension tables

Deploy it and test with: "{EVAL_EXAMPLES[1]}\""""},
            {"type": "prompt", "id": "Prompt 5.2", "title": "Create the AISQL Agent", "text": f"""In {FQ}, create a Cortex Agent called {N['aisql_agent']} with orchestration model auto.

Instructions: "You are an Alberta energy operations analyst. Use the enriched analyst tool for every count, total, average or ranking, including facilities, pipelines, shipments, incidents, AER inspections and shipper emails. Use search only when the user asks what a specific report, inspection note or email says. Always give a direct numeric answer when asked for counts or totals."

Tools:
- Cortex Analyst on {N['enriched_sv']} (warehouse {N['wh']}), with a description that lists the incident, inspection and email metrics
- Cortex Search on {N['search']} (id and title column DOC_ID), described as "only for reading specific documents"

Ask it "{EVAL_EXAMPLES[0]}" and "{EVAL_EXAMPLES[2]}" and show which tools it used."""},
            {"type": "prompt", "id": "Prompt 5.3", "title": "Evaluate the AISQL Agent", "text": f"""Run a Cortex Agent evaluation of {FQ}.{N['aisql_agent']} with exactly the same setup as baseline-run-1:

- Same existing dataset ENERGY_EVAL_DS (do not recreate it; remove the dataset: block from the YAML)
- Run name: aisql-run-1
- Metrics: answer_correctness and logical_consistency, version v3

Start it and poll STATUS until COMPLETED. Then save the per-question results to EVAL_RESULTS_AISQL in the same shape as EVAL_RESULTS_BASELINE."""},
            {"type": "prompt", "id": "Prompt 5.4", "title": "The Before/After Comparison", "text": f"""In {FQ}, compare EVAL_RESULTS_BASELINE and EVAL_RESULTS_AISQL:

1. A per-question table: question, question type, expected answer, baseline vs AISQL correctness, baseline vs AISQL seconds, baseline vs AISQL tokens.
2. A summary row for each agent: average correctness, average seconds, average tokens, plus the % change from baseline to AISQL. Also break it down by QUESTION_TYPE.
3. Explain what happened to tokens per answer. If they did not go down, explain why (fixed overhead from instructions, tool descriptions and the semantic view on every call) and what actually improved.
4. Using the one-time pipeline credits from Prompt 4.4, explain the cost trade-off: a one-time cost per document in exchange for exact aggregate answers at lower latency.
5. Write 3 bullet points I could share with my leadership, focused on accuracy and speed.""",
             "explain": "You can also open **AI & ML → Agents → (either agent) → Evaluations**, select both runs and click **Compare** to see the same before/after per question in the UI."},
            {"type": "copy_list", "title": "Bonus: ask both agents and feel the difference", "items": [
                "Which facility had the most high or critical severity incidents?",
                "What is the total estimated cost of environmental incidents?",
                "How many urgent shipper emails were about shipment delays?",
                "Summarize the French-language shipper complaints by topic and facility.",
            ]},
        ],
        "concepts": [
            {"term": "Why accuracy goes up", "definition": "Counts and totals come from SQL over every row, not from whichever chunks search happened to return."},
            {"term": "Why it gets faster and cheaper", "definition": "The agent makes one Analyst call that returns a few rows, instead of several searches that return long text chunks for the LLM to read. Fewer tokens per answer, fewer LLM calls."},
            {"term": "Break-even", "definition": "Preprocessing is paid once per document. Every question asked after that saves tokens, so the more the agent is used, the bigger the saving."},
        ],
        "built": [f"{N['enriched_sv']} over structured + AISQL-enriched tables", f"{N['aisql_agent']}, the optimized agent", "aisql-run-1 evaluation", "A before/after scorecard on accuracy, latency and cost"],
    },
]
