# Alberta Energy Operations: Raw Data to AI Agent with AISQL

Hands-on lab guide for the **[Calgary CoCo Hands-On Lab](https://www.snowflake.com/event/calgary-coco-hands-on-lab-20261125/)**,
Wednesday November 25, 2026, 9:00 AM MT, at The Ampersand (112 4 Ave SW, Calgary, AB).
Attendees build a Cortex Agent on raw energy operations documents, score it with Cortex Agent Evaluations, then preprocess the documents with AISQL functions, build a second agent on the enriched data, and compare accuracy, latency and token cost.

## Lab flow (75 min hands-on)

| # | Section | What happens |
|---|---------|--------------|
| 1 | Setup & Data Load | Database, stage, warehouse; load 7 CSVs (structured tables + raw text tables + eval set) |
| 2 | Baseline Agent | Semantic view over structured tables, Cortex Search over raw documents, `ENERGY_AGENT_BASELINE` |
| 3 | Evaluate the Baseline | Eval dataset with ground truth, `EXECUTE_AI_EVALUATION` run, scorecard |
| 4 | AISQL Pipeline | AI_EXTRACT / AI_CLASSIFY / AI_FILTER / AI_TRANSLATE / AI_AGG into `*_ENRICHED` tables, pipeline cost |
| 5 | AISQL Agent & Compare | Enriched semantic view, `ENERGY_AGENT_AISQL`, second eval run, before/after comparison and break-even |

## Repo layout

```
scripts/generate_data.py        # synthetic data + eval answers (seeded, reproducible)
workshop_guide/
  streamlit_app.py              # entrypoint (Streamlit Community Cloud main file)
  lab_config.py                 # ALL lab content: event, object names, data, sections, prompts
  components.py                 # generic renderers
  app_pages/                    # home, getting started, agenda
  data/                         # generated CSVs + alberta_energy_data.zip
```

## Data design

The scenario reuses the Alberta energy domain from the earlier Calgary HOL: the same five facilities (Scotford Upgrader, Horizon Oil Sands, Kearl Lake Operations, Christina Lake SAGD, Keystone Terminal Calgary) and 20 pipelines.

Facts in `INCIDENT_REPORTS_RAW`, `AER_INSPECTIONS_RAW` and `SHIPPER_EMAILS_RAW` exist only inside free text, with facility aliases (`HRZN`, `CNRL Horizon`, `the Calgary terminal`), mixed units (`8h`, `approx. 660 minutes`, `713.4k CAD`) and ~20% French emails. AER inspections reference facilities only by AER licence number. The generator keeps the hidden ground truth and writes the correct answers into `EVAL_QUESTIONS.csv`, so both agents are scored against the same answer key.

Regenerate with:

```bash
python3 scripts/generate_data.py
```

## Run locally

```bash
cd workshop_guide
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Before the event

- [ ] Replace `EVENT["signup_link"]` / `signup_short_link` in `lab_config.py` with the Calgary trial signup links
- [ ] Push to GitHub as `sfc-gh-mkeith/coco-hol-aisql-calgary-nov-25` and check `DATA["zip_url"]` points at the pushed zip
- [ ] Deploy on share.streamlit.io with main file `workshop_guide/streamlit_app.py`
- [ ] Do a full dry run in a fresh trial account and note the baseline vs AISQL scores
