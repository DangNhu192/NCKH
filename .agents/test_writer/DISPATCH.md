# DISPATCH — Test Writer (E2E & Module Test Suite Architect)

## Mission
Design and implement comprehensive automated test suites (Tiers 1-4) verifying all requirements R1, R2, R3, R4 of the WEB SUPER reform.

## Reference & Specifications
- `ORIGINAL_REQUEST.md`: `H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\ORIGINAL_REQUEST.md`
- `PROJECT.md`: `H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\PROJECT.md`
- `TEST_INFRA.md` (if existing or to be updated)

## File Ownership
- `tests/test_reform_r1_pipeline.py`
- `tests/test_reform_r2_writer_zotero.py`
- `tests/test_reform_r3_humanizer_dom.py`
- `tests/test_reform_r4_ui_packaging.py`
- `tests/test_reform_master_e2e.py`
- `TEST_READY.md` (publish when test suite is complete)

## Test Tiers to Implement:
1. **Tier 1 (Feature Coverage):** PICO semantic parsing, trend fetching, multi-format doc vault ingestion, true LLM drafting, Zotero XML injection, RIS/BIB export, LLM Humanizer with Burstiness/Perplexity, UI route integrity, archive packaging.
2. **Tier 2 (Boundary & Corner Cases):** Empty inputs, large documents, malformed DOCX/MD, offline fallback without API keys, zero fabrication validation (100% real DOIs).
3. **Tier 3 (Cross-Feature Combinations):** Step 1 PICO -> Step 2 Vault -> Step 5 Drafting -> Step 6 Zotero DOM -> Step 7 Humanizer in-place DOM pipeline flow.
4. **Tier 4 (Real-World Application Scenarios):** Full end-to-end multi-disciplinary research scenarios (e.g. Smart Grid, Clinical Medicine, Agricultural Policy) producing valid File A (.docx with Zotero XML), File B, .ris, .bib, and humanized DOCX.

## Verification Requirements
Execute all test scripts using `.venv\Scripts\python.exe` and publish `TEST_READY.md` upon completion.
