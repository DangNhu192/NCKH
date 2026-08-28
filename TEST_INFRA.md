# E2E Test Infra: WEB SUPER v3.2 / v2.0

## Test Philosophy
- Opaque-box, requirement-driven, continuous multi-tier verification.
- Enforces 4 Invariant Rules unconditionally (Zero Fabrication, Word DOM In-Place preservation, Vietnamese decimal comma, Math/Chem formatting).
- Methodology: Category-Partition + Boundary Value Analysis + Pairwise Combinatorial + Real-World Workload Testing + Adversarial Stress Testing.

## Feature Inventory & Test Coverage
| # | Feature | Source | Tier 1 (Feature) | Tier 2 (Boundary) | Tier 3 (Pairwise) | Tier 4 (Real-World) |
|---|---------|--------|:----------------:|:-----------------:|:-----------------:|:-------------------:|
| F01 | RhinoInsight Phase 1 Outline Tree | R1, Survey 1 | 5 cases | 5 cases | ✓ | ✓ |
| F02 | RhinoInsight Phase 2 Deep Investigation | R1, Survey 1 | 5 cases | 5 cases | ✓ | ✓ |
| F03 | Academic Writer Dual 2-Files Publishing | R1, Survey 1 | 5 cases | 5 cases | ✓ | ✓ |
| F04 | SciBot IMRaD Scientific Sectioner | R2, Survey 2 | 5 cases | 5 cases | ✓ | ✓ |
| F05 | SciBot Okapi BM25 + Hybrid Ranking | R2, Survey 2 | 5 cases | 5 cases | ✓ | ✓ |
| F06 | SciBot Grounded Chat & 7-Col Matrix | R2, Survey 2 | 5 cases | 5 cases | ✓ | ✓ |
| F07 | 6 GATE Editorial Office & Peer Review | R3, Survey 3 | 5 cases | 5 cases | ✓ | ✓ |
| F08 | 4 Invariant Rules Enforcement | R3, Survey 3 | 5 cases | 5 cases | ✓ | ✓ |
| F09 | 4-Layer Doc Synchronization | R4, Survey 3 | 5 cases | 5 cases | ✓ | ✓ |
| F10 | Comprehensive Automated E2E Test Suite | R4, Survey 3 | 5 cases | 5 cases | ✓ | ✓ |

## Test Architecture
- **Test Runner**: Python test runner via virtual environment (`uv run python <test_file>.py`).
- **Pass/Fail Semantics**: Exit code 0, 100% assertions passed, zero unhandled exceptions, zero fake data detected.
- **Test Directory & Suites Layout**:
  - `test_pdf_ocr_full_flow.py`: OCR Purpose-Built AI, 300 DPI image extraction, RAG chunk citations `[file, Trang X]`.
  - `test_open_notebook_full_flow.py`: Ingestion, SciBot sectioning, Okapi BM25, Grounded Chat, Literature Matrix.
  - `test_docx_editor_engine.py`: Word In-Place DOM preservation, Heading 1/2/3 styles, grid tables, run styles.
  - `test_server_load.py`: Concurrent API load, async pipeline resilience, server endpoints health.
  - `test_worker_m1_verification.py`: Academic Writer deep research flow, 2-files generation, PICO integration.
  - `test_m2_docx_math_chem.py`: Math formulas OMML/MathML, Chemistry subscript/superscript, decimal formatting.
  - `docs_chuc_nang_va_chinh_sua/tools_cross_validate_docs.py`: 4-Layer documentation validation (15/15 files).

## Real-World Application Scenarios (Tier 4)
| # | Scenario | Features Exercised | Complexity |
|---|----------|--------------------|------------|
| 1 | Full Academic Research Pipeline (PICO ➔ Evidence Harvest ➔ Outline Tree ➔ Deep Drafting ➔ 2 Files) | F01, F02, F03, F08 | High |
| 2 | SciBot Literature Ingestion & Grounded Evidence Discovery (PDF OCR ➔ Sectioning ➔ Okapi BM25 ➔ 7-Col Matrix) | F04, F05, F06 | High |
| 3 | Q1 ISI/Scopus Editorial Review & Rebuttal (Rubric Scoring ➔ Adversarial 2-Reviewers ➔ Revision Directives) | F07, F08 | High |
| 4 | Multimodal Word DOM & Math/Chem Publishing (Heading 1/2/3, 300 DPI figures, OMML Equations, Chem formulas) | F08 | High |
| 5 | Cross-System Master Validation (Docs Sync + All Test Suites Full Execution) | F09, F10 | High |

## Coverage Thresholds
- Tier 1: ≥5 test cases per feature (50 total)
- Tier 2: ≥5 boundary/edge test cases per feature (50 total)
- Tier 3: Pairwise coverage across major feature interactions (≥10 combination suites)
- Tier 4: ≥5 realistic application scenarios
- Tier 5: Adversarial stress testing & coverage hardening (Zero Cheating, Forensic Integrity Audit CLEAN)
