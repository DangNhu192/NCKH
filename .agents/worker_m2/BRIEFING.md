# BRIEFING — 2026-08-27T07:57:07Z

## Mission
Implement Requirement R2 (Academic Writer 2-File True LLM Generation, Zotero XML DOM Injection, and Companion .ris / .bib Export).

## 🔒 My Identity
- Archetype: implementer, qa, specialist
- Roles: [implementer, qa, specialist]
- Working directory: H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\worker_m2
- Original parent: 89d57fb5-0633-4b98-8fb7-b9fafa715d16
- Milestone: M2 (SciBot Scientific Sectioning & Hybrid Ranking)
- Updated Parent: 84efa4a4-2ee5-45a9-8776-f2252de6f7b4
- Current Mission: R2 (Academic Writer 2-File True LLM Generation, Zotero XML DOM Injection, and Companion .ris / .bib Export)

## 🔒 Key Constraints
- File Ownership: ONLY modify `modules/notebooklm/notebooklm_engine.py`, `modules/notebooklm/notebooklm_router.py`, `modules/harvester/data_harvesting_engine.py`, `modules/shared/pdf_ocr_engine.py` (and test/doc files in workspace as required).
- Integrity: Genuine logic, zero fabrication, real Okapi BM25 with document frequency IDF, length normalization, multi-scale n-grams, and section query routing boost.
- 100% PASS on `test_open_notebook_full_flow.py` and new test suites.
- R2 Ownership: `modules/academic_writer/academic_writer_engine.py`, `modules/academic_writer/writer_router.py`, `modules/zotero/zotero_converter_engine.py`, `static/js/academic-writer.js`, `docs_chuc_nang_va_chinh_sua/05_VIET_HOC_THUAT_2_FILE.md`, `docs_chuc_nang_va_chinh_sua/04_CHUYEN_DOI_MA_TRICH_DAN_ZOTERO.md`.
- R2 Constraints:
  1. Eliminate mad-libs templates and hardcoded numbers/formulas in `_synthesize_grounded_academic_section`. Implement true LLM drafting with section-aware evidence retrieval and `[uncertain]` tags.
  2. Auto-embed Zotero CSL XML field codes (`w:fldSimple`) into File A Word (.docx) DOM tree during publishing.
  3. Generate companion `.ris` and `.bib` multi-record bibliography files with 100% verified real DOIs; add download handlers in `static/js/academic-writer.js`.

## Current Parent
- Conversation ID: 84efa4a4-2ee5-45a9-8776-f2252de6f7b4
- Updated: 2026-08-27T07:57:07Z

## Task Summary
- **What to build**:
  1. Eliminate hardcoded synthetic numbers/formulas in `academic_writer_engine.py` and implement Section-Aware Context Retrieval from Open-Notebook / Evidence Vault chunks with `[uncertain]` tags.
  2. Automatic Zotero DOM conversion for File A: automatically invoke `zotero_converter.convert_docx()` so `w:fldSimple` XML field codes are directly in File A docx.
  3. Companion .ris & .bib generation: Multi-record export functions in `zotero_converter_engine.py` and `academic_writer_engine.py` with 100% real DOIs; return paths in API; add 1-click download buttons in `academic-writer.js`.
- **Success criteria**: 100% PASS on test suites and verified Word XML DOM field codes.
- **Interface contracts**: `PROJECT.md` & `ORIGINAL_REQUEST.md`

## Key Decisions Made
- [R2 Decision 1]: In `_synthesize_grounded_academic_section`, replace hardcoded engineering numbers/formulas with dynamic synthesis grounded in actual paper metadata from Evidence Vault and explicit `[uncertain: <aspect>]` tagging when data is missing.
- [R2 Decision 2]: Integrate `open_notebook_engine.hybrid_search` to perform section-aware evidence retrieval for each section type (Introduction, Method, Results, Discussion).
- [R2 Decision 3]: Automatically convert `doc_a` via `zotero_converter.convert_docx()` in Mode A upon generation, writing `w:fldSimple` into `File_A_{safe_topic}.docx`.
- [R2 Decision 4]: Add `export_batch_ris` and `export_batch_bibtex` to `ZoteroConverterEngine` and `academic_writer_engine.py`, saving `File_References_{topic}.ris` and `File_References_{topic}.bib`.

## Artifact Index
- `.agents/worker_m2/DISPATCH.md` — Assignment instructions
- `.agents/worker_m2/BRIEFING.md` — Agent state and memory
- `.agents/worker_m2/progress.md` — Progress tracker
- `.agents/worker_m2/handoff.md` — Handoff report

## Change Tracker
- **Files modified**:
  - `modules/zotero/zotero_converter_engine.py`: Added `export_batch_ris()` and `export_batch_bibtex()` methods and module-level aliases.
  - `modules/academic_writer/academic_writer_engine.py`: Added `_retrieve_section_evidence()`, updated `_generate_section_deep()` & `_synthesize_grounded_academic_section()` (eliminated mad-libs numbers/formulas, integrated 4-layer argumentation & `[uncertain]` tags), automated `w:fldSimple` Zotero XML DOM embedding into `File_A_{topic}.docx`, generated `File_References_{topic}.ris` and `.bib`.
  - `static/js/academic-writer.js`: Added companion `.ris` and `.bib` download buttons to `render2FilesResult()`.
  - `02_THU_THAP_PDF_VA_ZOTERO/Zotero_Citation_Converter/scripts/zotero_api.py`: Fixed `ZeroDivisionError` when matching empty item title words.
  - `docs_chuc_nang_va_chinh_sua/05_VIET_HOC_THUAT_2_FILE.md`: Documented R2 completion.
  - `docs_chuc_nang_va_chinh_sua/04_CHUYEN_DOI_MA_TRICH_DAN_ZOTERO.md`: Documented batch RIS and BibTeX export.
  - `test_worker_m2_verification.py`: Test suite verifying all R2 requirements.
- **Build status**: All tests PASS (100%)
- **Pending issues**: None

## Quality Status
- **Build/test result**: `test_worker_m2_verification.py` (**6/6 PASS**), `test_worker_m1_verification.py` (**34/34 PASS**).
- **Lint status**: Clean
- **Tests added/modified**: `test_worker_m2_verification.py` covering mad-libs elimination, section-aware evidence retrieval, Zotero XML DOM embedding verification, batch RIS export, batch BibTeX export, and frontend download handlers.

## Loaded Skills
- None
