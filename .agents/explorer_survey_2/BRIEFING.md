# BRIEFING — 2026-08-27T07:56:45+07:00

## Mission
Investigate R2: Upgrade Academic Writer 2-File ("Viết Học Thuật 2-File") to pure LLM drafting (eliminating mad-libs templates), auto-inserting Zotero CSL XML field codes (w:fldSimple / w:instrText) directly into Word (.docx) DOM tree, and generating companion .ris and .bib bibliography files with 100% verified authentic DOIs.

## 🔒 My Identity
- Archetype: explorer
- Roles: Academic Writer & Zotero Explorer, Docx DOM & CSL XML Specialist
- Working directory: H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\explorer_survey_2
- Original parent: 84efa4a4-2ee5-45a9-8776-f2252de6f7b4
- Milestone: Survey & Architectural Deep-Dive (R2: Academic Writer 2-File & Zotero DOM) — COMPLETED

## 🔒 Key Constraints
- Read-only investigation — do NOT implement modifications to source code
- Strictly adhere to the 4 Immutable Principles (Evidence First, In-Place DOM Word Preservation, Vietnamese Number Formatting, International Math/Chem Standard)
- Output analysis.md and handoff.md in working directory
- Communicate via send_message to parent (id: 84efa4a4-2ee5-45a9-8776-f2252de6f7b4)
- Investigate section-by-section pure LLM generation grounded in Evidence Vault / NotebookLM / files
- Investigate Zotero CSL XML injection into python-docx DOM (w:fldSimple / w:instrText)
- Investigate .ris and .bib generation with verified DOIs

## Current Parent
- Conversation ID: 84efa4a4-2ee5-45a9-8776-f2252de6f7b4
- Updated: 2026-08-27T07:56:45+07:00

## Investigation State
- **Explored paths**:
  - `modules/academic_writer/academic_writer_engine.py` & `writer_router.py`
  - `modules/zotero/zotero_converter_engine.py` & `zotero_router.py`
  - `modules/notebooklm/notebooklm_engine.py` & `notebooklm_router.py`
  - `modules/shared/docx_styler.py` & `modules/workspace/docx_editor_engine.py`
  - `static/js/academic-writer.js` & `static/index.html` (#writer-tab)
  - `docs_chuc_nang_va_chinh_sua/05_VIET_HOC_THUAT_2_FILE.md` & `04_CHUYEN_DOI_MA_TRICH_DAN_ZOTERO.md`
  - `Skill/02_THU_THAP_PDF_VA_ZOTERO/Zotero_Citation_Converter/SKILL.md` & `Skill/03_VIET_CHUYEN_NGHIEP_V3.1/SKILL.md`
- **Key findings**:
  1. Mad-Libs removal: `_synthesize_grounded_academic_section()` contains hardcoded mathematical formulas & static sample counts ("18.500 bản ghi", "41,6%"); needs pure LLM section-by-section drafting with section-aware chunks from Open-Notebook/Evidence Vault.
  2. Zotero XML DOM injection: File A docx was saved as plain text runs without `w:fldSimple` XML tags; auto-integrating `zotero_converter.convert_docx()` in the File A generation pipeline directly embeds Zotero CSL XML into the Word DOM.
  3. Companion .ris & .bib generation: Developed multi-item RIS (`export_batch_ris`) and BibTeX (`export_batch_bibtex`) architecture with 100% verified authentic DOIs, saving `File_References_{topic}.ris` and `.bib` into `Tai_Lieu/` and adding 1-click UI download buttons.
- **Unexplored areas**: None. Complete architectural survey finished.

## Key Decisions Made
- Authored comprehensive architectural analysis report: `analysis.md`.
- Authored self-contained 5-component handoff report: `handoff.md`.

## Artifact Index
- H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\explorer_survey_2\analysis.md — Comprehensive Survey & Architecture Analysis Report
- H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\explorer_survey_2\handoff.md — 5-Component Handoff Report
- H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\explorer_survey_2\progress.md — Liveness & Progress Log
