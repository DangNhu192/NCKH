# Project: WEB SUPER v3.2 / v2.0 — Comprehensive Platform Reform

## Architecture
Hệ thống nghiên cứu khoa học chuẩn quốc tế ISI/Scopus/Scimago, Tòa soạn báo AI 6 Ban GATE, và Kho tri thức học thuật Open-Notebook.

### Module Boundaries & Data Flow:
```
[User / Browser UI (static/)]
        │
        ▼ (REST API / SSE)
[FastAPI Application Server (server.py)]
        │
        ├── [7-Step Pipeline (modules/pipeline/)] ◄─── R1: Semantic PICO, Trends & Seamless Flow
        │       ├── Step 1: Semantic PICO & Multilingual AI Keywords (EuropePMC/OpenAlex/ArXiv)
        │       ├── Multi-format Document Ingestion (.md, .docx, workspace files)
        │       └── End-to-end 7-Step sequential execution & artifact publishing
        │
        ├── [Academic Writer 2-File (modules/academic_writer/)] ◄─── R2: True LLM Generation & Zotero XML
        │       ├── Pure LLM Drafting (no mad-libs template placeholders)
        │       ├── Zotero CSL XML field codes (w:fldSimple) DOM insertion into Word (.docx)
        │       └── 100% Real DOI .ris / .bib bibliography generation & export
        │
        ├── [AI Humanizer / Turnitin (modules/turnitin_humanizer/ & modules/workspace/)] ◄─── R3: LLM Restructure & DOM Preservation
        │       ├── Specialized LLM Perplexity & Burstiness restructuring
        │       └── In-Place Word (.docx) DOM preservation (Headings, 300 DPI images, tables, Zotero XML)
        │
        ├── [UI/UX & Route Integrity (static/ & routes/)] ◄─── R4: Button Audit & Xac_Nhan_Hoan_Hao Packaging
        │       ├── 100% responsive button handlers & clean browser console
        │       └── Snapshot packaging of verified modules into Xac_Nhan_Hoan_Hao/
        │
        ├── [Open-Notebook / Kho Tri Thức (modules/notebooklm/)] ◄─── SciBot IMRaD & BM25 Hybrid Search
        ├── [Harvester Pro & OCR (modules/harvester/, modules/shared/pdf_ocr_engine.py)]
        ├── [Editorial Office 6 GATEs (modules/editorial_office/)]
        └── [BigQuery AI Analytics (modules/bigquery/)]
```

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| F01 | Semantic PICO & Multilingual Keywords | AI Gemini semantic extraction + EuropePMC/OpenAlex/ArXiv trend analytics | M1 | ORIGINAL_REQUEST R1 |
| F02 | Multi-format Document Ingestion | Ingest .md, .docx, workspace files into Evidence Vault | M1 | ORIGINAL_REQUEST R1 |
| F03 | 7-Step Pipeline End-to-End Execution | Seamless 7-step execution with full artifact publishing | M1 | ORIGINAL_REQUEST R1 |
| F04 | Academic Writer True LLM Generation | Section-by-section pure LLM drafting without mad-libs / placeholder templates | M2 | ORIGINAL_REQUEST R2 |
| F05 | Zotero XML DOM Injection | In-place injection of `w:fldSimple` Zotero CSL field codes into Word (.docx) DOM | M2 | ORIGINAL_REQUEST R2 |
| F06 | Real DOI .ris / .bib Export | 100% authentic verified DOI bibliography export for 1-click Zotero import | M2 | ORIGINAL_REQUEST R2 |
| F07 | LLM AI Humanizer Restructuring | Burstiness & Perplexity adjustment with human-grade academic style | M3 | ORIGINAL_REQUEST R3 |
| F08 | Word In-Place DOM Preservation | 100% preservation of Word styles, XML structure, images, and tables during humanization | M3 | ORIGINAL_REQUEST R3 |
| F09 | UI/UX Button & Route Audit | Complete audit of static/index.html & JS files; fix all non-responsive buttons | M4 | ORIGINAL_REQUEST R4 |
| F10 | Perfect Snapshot Packaging | Packaging verified and tested modules into Xac_Nhan_Hoan_Hao/ | M4 | ORIGINAL_REQUEST R4 |
| F11 | 15 Docs 4-Layer Synchronization | Update and validate all 15 documentation files in docs_chuc_nang_va_chinh_sua/ | M5 | System Rules |
| F12 | Master E2E & Adversarial Hardening | Comprehensive automated test verification across Tiers 1-5 | M6 | Quality Gate |
| F13 | Zotero Web API Bidirectional Sync | Direct cloud sync, Vietnamese single-field name fixer, thematic subcollection classification | M2 | Academic Advancement |
| F14 | Zero-Risk Storage Optimization | Safe PDF storage cleanup with automatic ZIP backup, freeing 300MB Zotero Cloud quota | M2 | Storage Protocol |
| F15 | Interactive Word Hyperlinks Engine | Full `<w:hyperlink>` OpenXML DOM conversion with Ctrl+Click navigation & strict page budget | M3 | Publishing Standard |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | 7-Step Pipeline Reform | `modules/pipeline/`, `static/js/pipeline.js`, `routes/` | None | IN_PROGRESS |
| M2 | Academic Writer 2-File & Zotero Export | `modules/academic_writer/`, `modules/workspace/`, `static/js/academic-writer.js` | None | IN_PROGRESS |
| M3 | AI Humanizer & Word DOM Preservation | `modules/turnitin_humanizer/`, `modules/shared/docx_styler.py`, `modules/workspace/` | None | IN_PROGRESS |
| M4 | UI/UX Audit & Xac_Nhan_Hoan_Hao Packaging | `static/index.html`, `static/js/`, `Xac_Nhan_Hoan_Hao/` | None | IN_PROGRESS |
| M5 | 15 Documentation Files Synchronization | `docs_chuc_nang_va_chinh_sua/` (15 files) | M1, M2, M3, M4 | PLANNED |
| M6 | Master E2E Test Suite & Adversarial Hardening | `tests/` master suites, Tier 1-5 validation | M1, M2, M3, M4, M5 | PLANNED |

## Interface Contracts

### Pipeline ↔ Evidence Ingestion & Trend Analysis
- `POST /api/pipeline/step1/pico-trends` -> Input: `{"topic": str, "field": str, "uploaded_docs": List[str]}` -> Output: `{"pico": dict, "keywords": list, "trends": list, "status": "success"}`
- `POST /api/pipeline/run-step` -> Input: `{"step": int, "context": dict}` -> Output: `{"step_result": dict, "next_step": int, "artifacts": list}`

### Academic Writer ↔ Zotero DOM & RIS/BIB Export
- `POST /api/writer/generate-2file` -> Input: `{"topic": str, "outline": dict, "evidence_vault_id": str}` -> Output: `{"file_a_docx": str, "file_b_docx": str, "ris_file": str, "bib_file": str}`

### AI Humanizer ↔ Word In-Place DOM
- `POST /api/humanizer/process-docx` -> Input: `{"docx_path": str, "mode": "academic_burstiness"}` -> Output: `{"humanized_docx_path": str, "human_score": float, "dom_intact": bool}`

## Code Layout
- `modules/pipeline/`: 7-Step Pipeline engine and route handlers
- `modules/academic_writer/`: Academic Writer 2-File engine, LLM drafter, bibliography generator
- `modules/turnitin_humanizer/`: AI Humanizer, perplexity/burstiness transformer
- `modules/workspace/`: Word .docx DOM manipulation engine, Zotero XML injector
- `modules/shared/`: docx styler, OCR engine, math/chem converters
- `static/`: Frontend HTML, CSS, JavaScript modules
- `docs_chuc_nang_va_chinh_sua/`: 15 functional documentation files
- `Xac_Nhan_Hoan_Hao/`: Packaging directory for verified perfect modules
- `tests/`: Automated test suite
