# BRIEFING — 2026-08-27T07:57:07+07:00

## Mission
Implement Requirement R1: Comprehensive reform of 7-Step Pipeline ("Quy Trình Liên Kết"), including OpenAlex & EuropePMC research trends in Step 1, multi-format document ingestion into Evidence Vault in Step 2, and 1:1 synchronization of the 7-step flow between Backend and Frontend.

## 🔒 My Identity
- Archetype: 7-Step Pipeline & PICO Reform Worker (Worker M1)
- Roles: implementer, qa, specialist
- Working directory: H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\worker_m1
- Original parent: 84efa4a4-2ee5-45a9-8776-f2252de6f7b4
- Milestone: R1 (7-Step Pipeline & PICO Reform)

## 🔒 Key Constraints
- Exclusive file write ownership:
  - `modules/pipeline/pipeline_engine.py`
  - `modules/pipeline/pipeline_router.py`
  - `modules/harvester/data_harvesting_engine.py` (add `fetch_research_trends`)
  - `static/js/pipeline.js`
  - `static/index.html` (Pipeline tab & stepper sections)
  - `docs_chuc_nang_va_chinh_sua/01_QUY_TRINH_7_BUOC_PIPELINE.md`
- Evidence First & Zero Fabrication: 100% genuine citations and DOIs.
- In-Place DOM Word (.docx) preservation: Heading 1/2/3, 300 DPI figures, Zotero XML multi-run preservation.
- Vietnamese decimal standard (`1,5; 28,5%` and `1.000; 50.000`).
- International chemical & mathematical symbols (`FeS₂`, `H₂SO₄`, LaTeX OMML).
- All implementations must be genuine, maintaining real state and real behavior.

## Current Parent
- Conversation ID: 84efa4a4-2ee5-45a9-8776-f2252de6f7b4
- Updated: 2026-08-27T07:57:07+07:00

## Task Summary
- **What to build**:
  1. Step 1 research trends integration with OpenAlex & EuropePMC in `data_harvesting_engine.py` & `pipeline_engine.py`.
  2. Multi-format document ingestion (.docx, .md, .pdf, workspace files) into Evidence Vault with `/api/pipeline/vault/*` endpoints in `pipeline_engine.py` & `pipeline_router.py`.
  3. Synchronize 7-step flow 1:1 between backend and frontend (`static/index.html` & `static/js/pipeline.js`), removing `backendStepMap` and rendering all 7 distinct steps.
- **Success criteria**:
  - Genuine research trends fetching from OpenAlex & EuropePMC APIs with fallback.
  - Multi-format file ingestion (.docx, .md, .pdf, .txt) extracting title, authors, year, DOI, abstract, and saving to vault.
  - Full 7-step linear synchronization with rich interactive UI for all 7 steps.
  - 100% test pass on unit and integration test suite.
- **Interface contracts**: PROJECT.md & SCOPE.md.

## Key Decisions Made
- Research trends query computes publication counts for 2019-2025 using OpenAlex `/works?group_by=publication_year` and EuropePMC REST API counts, calculating 5-year CAGR and momentum classification.
- Evidence Vault supports direct file uploads (.docx via python-docx, .pdf via pypdf/pdfplumber, .md/.txt UTF-8) and relative workspace imports.
- Frontend stepper and cards strictly aligned with 7 steps:
  1. Mục Tiêu (PICO) & Xu Hướng Nghiên Cứu
  2. Kho Dữ Liệu Thực Chứng (Evidence Vault)
  3. Đồng Bộ Tri Thức & Ma Trận Y Văn
  4. Cấu Trúc IMRaD & BigQuery AI/ML (300 DPI)
  5. Soạn Thảo Bộ Đôi 2-File Học Thuật
  6. Nhúng Mã Trường Động Zotero
  7. Khử Dấu Vết AI Turnitin & Xuất Bản

## Change Tracker
- **Files modified**: [TBD]
- **Build status**: Pending implementation
- **Pending issues**: None

## Quality Status
- **Build/test result**: Pending
- **Lint status**: Clean
- **Tests added/modified**: Pending

## Artifact Index
- `docs_chuc_nang_va_chinh_sua/01_QUY_TRINH_7_BUOC_PIPELINE.md` — Feature specification and changelog
- `.agents/worker_m1/test_pipeline_r1.py` — Unit & integration test suite
- `.agents/worker_m1/handoff.md` — 5-component handoff report
