# BRIEFING — 2026-08-27T00:59:00Z

## Mission
Design, implement, and verify comprehensive automated test suites (Tiers 1-4) covering all 4 Reform Requirements (R1, R2, R3, R4) and Master E2E workflows in Web Super.

## 🔒 My Identity
- Archetype: Test Writer & QA Architect
- Roles: specialist, qa
- Working directory: H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\test_writer
- Original parent: 84efa4a4-2ee5-45a9-8776-f2252de6f7b4
- Milestone: M6 (Master E2E & Comprehensive Reform Test Suite)

## 🔒 Key Constraints
- Test code only — never modify implementation code; escalate bugs.
- 4 Immutable Rules: Evidence First & Zero Fabrication (100% real DOIs), In-Place DOM Word (.docx) Preservation, Vietnamese decimal comma format, Chemistry & Math standardisation.
- Progressive testability & strict isolation.
- Execute with Python interpreter in `.venv` and publish `TEST_READY.md`.

## Current Parent
- Conversation ID: 84efa4a4-2ee5-45a9-8776-f2252de6f7b4
- Updated: 2026-08-27T00:59:00Z

## Task Summary
- **What to build**: Comprehensive automated test suites across 5 target test modules:
  1. `tests/test_reform_r1_pipeline.py` (PICO semantic extraction, trend analytics, multi-format doc vault ingestion, 7-step pipeline flow)
  2. `tests/test_reform_r2_writer_zotero.py` (Academic Writer true LLM drafting, Zotero CSL XML injection, 100% real DOI .ris/.bib bibliography)
  3. `tests/test_reform_r3_humanizer_dom.py` (AI Humanizer burstiness/perplexity restructure, in-place DOM preservation: headings, 300 DPI images, tables, Zotero XML)
  4. `tests/test_reform_r4_ui_packaging.py` (UI/UX button handlers, API route integrity, `Xac_Nhan_Hoan_Hao` snapshot verification)
  5. `tests/test_reform_master_e2e.py` (Master E2E pipeline connecting all modules across multiple multidisciplinary scenarios)
- **Success criteria**: 100% test pass rate across all suites, zero mock fabrication violations, full coverage of edge cases and integration scenarios.
- **Interface contracts**: PROJECT.md & module router schemas.
- **Code layout**: `tests/` directory at root of `Web Super`.

## Key Decisions Made
- Use pytest with standard unittest/FastAPI TestClient / httpx / python-docx / lxml.
- Tests will cover both unit logic, integration API endpoints, and direct file/DOM generation with validation of XML tags, styles, and bibliography validity.

## Artifact Index
- `tests/test_reform_r1_pipeline.py`
- `tests/test_reform_r2_writer_zotero.py`
- `tests/test_reform_r3_humanizer_dom.py`
- `tests/test_reform_r4_ui_packaging.py`
- `tests/test_reform_master_e2e.py`
- `TEST_READY.md`
- `handoff.md`

## Loaded Skills
- **Source**: antigravity testing guidelines
- **Core methodology**: Behavior-based verification, adversarial edge cases, in-place DOM inspection, schema validation.

## Quality Status
- **Build/test result**: Initializing test suite.
- **Lint status**: Clean.
- **Tests added/modified**: TBD.
