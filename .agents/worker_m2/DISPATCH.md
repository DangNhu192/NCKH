# DISPATCH — Worker M2 (Academic Writer & Zotero DOM / RIS-BIB Export)

## Mission
Implement Requirement R2: Academic Writer 2-File true LLM generation, Zotero XML DOM injection, and companion .ris / .bib export.

## Reference & Specifications
- `ORIGINAL_REQUEST.md`: `H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\ORIGINAL_REQUEST.md`
- `PROJECT.md`: `H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\PROJECT.md`
- Explorer 2 Analysis: `H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\explorer_survey_2\analysis.md`
- Explorer 2 Handoff: `H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\explorer_survey_2\handoff.md`

## File Ownership
- `modules/academic_writer/academic_writer_engine.py`
- `modules/academic_writer/writer_router.py`
- `modules/zotero/zotero_converter_engine.py` (add `export_batch_ris`, `export_batch_bibtex`)
- `static/js/academic-writer.js`

## Detailed Tasks
1. **Eliminate Mad-Libs / Placeholder Templates:** In `academic_writer_engine.py`, eliminate hardcoded synthetic numbers/formulas in `_synthesize_grounded_academic_section`. Implement true LLM section drafting with section-aware evidence retrieval from Evidence Vault / Open-Notebook and `[uncertain]` tagging for missing/conflicting data.
2. **Auto-Inject Zotero XML DOM into File A:** In `academic_writer_engine.py`, automatically invoke `zotero_converter.convert_docx()` on File A during publication so `w:fldSimple` Zotero CSL field codes are directly embedded in the Word (.docx) DOM tree.
3. **Companion .ris & .bib Bibliography Generation:** In `zotero_converter_engine.py` and `academic_writer_engine.py`, implement multi-record `.ris` and `.bib` bibliography generators with 100% verified real DOIs. Return file paths in `/api/writer/generate-2file` and add 1-click download buttons in `static/js/academic-writer.js`.

## Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Verification Requirements
Run your unit/integration tests using `.venv\Scripts\python.exe` and document passing results and XML validation in `handoff.md`.
