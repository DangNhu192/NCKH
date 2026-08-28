# DISPATCH — Worker M1 (7-Step Pipeline & PICO Reform)

## Mission
Implement Requirement R1: Comprehensive reform of 7-Step Pipeline ("Quy Trình Liên Kết").

## Reference & Specifications
- `ORIGINAL_REQUEST.md`: `H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\ORIGINAL_REQUEST.md`
- `PROJECT.md`: `H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\PROJECT.md`
- Explorer 1 Analysis: `H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\explorer_survey_1\analysis.md`
- Explorer 1 Handoff: `H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\explorer_survey_1\handoff.md`

## File Ownership
- `modules/pipeline/pipeline_engine.py`
- `modules/pipeline/pipeline_router.py`
- `modules/harvester/data_harvesting_engine.py` (add `fetch_research_trends`)
- `static/js/pipeline.js`
- `static/index.html` (Pipeline tab & stepper sections)

## Detailed Tasks
1. **Step 1 Trends Integration:** In `data_harvesting_engine.py` and `pipeline_engine.py`, implement `fetch_research_trends(topic, query)` querying OpenAlex (`group_by=publication_year`) and EuropePMC (`PUB_YEAR`) to compute publication frequencies by year (2019-2025) and CAGR growth rate.
2. **Multi-format Document Ingestion into Evidence Vault:** In `pipeline_engine.py` and `pipeline_router.py`, implement `ingest_document_to_vault` and `import_workspace_files_to_vault` supporting `.docx`, `.md`, `.pdf`, `.txt`, and open endpoints `/api/pipeline/vault/upload` and `/api/pipeline/vault/import-workspace`.
3. **Synchronize 7-Step Linear Flow:** Update `static/index.html` and `static/js/pipeline.js` to render full 7 distinct steps (Step 1: PICO & Trends, Step 2: Evidence Vault, Step 3: Knowledge Sync, Step 4: Structure & BigQuery, Step 5: Academic Drafting, Step 6: Zotero XML, Step 7: AI Humanizer & Publish). Remove `backendStepMap` mapping. Ensure sequential and auto-run execution work 100%.

## Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Verification Requirements
Run your unit/integration tests using `.venv\Scripts\python.exe` and record command lines, test outputs, and layout compliance in `handoff.md`.
