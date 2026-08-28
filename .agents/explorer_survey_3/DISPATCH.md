# DISPATCH — Explorer 3 (Humanizer & UI Audit Explorer)

## Mission
Investigate R3 & R4: Upgrade AI Humanizer ("Khử Dấu Vết AI") and perform Full UI/UX button & route audit + snapshot packaging into `Xac_Nhan_Hoan_Hao/`.

## Requirements to Map
1. **AI Humanizer LLM Restructuring:** Replace regex-based word replacement with specialized LLM rewriting for natural Burstiness & Perplexity adjustment while preserving academic rigor (target Human Score >= 90%).
2. **In-Place Word DOM Preservation:** Preserve 100% of Word formatting (Heading 1/2/3 styles, tables, 300 DPI figures, OMML formulas, Zotero XML field codes).
3. **UI/UX Audit & Fixes:** Systematic audit of all buttons across `static/index.html` and JS modules (`pipeline.js`, `academic-writer.js`, `harvester.js`, `notebooklm.js`, `turnitin.js`, `workspace.js`, etc.) to identify broken/non-responsive buttons or missing API routes.
4. **Snapshot Packaging into Xac_Nhan_Hoan_Hao/:** Inventory and plan the packaging of verified modules into `Xac_Nhan_Hoan_Hao/`.

## Reference Files to Inspect
- `ORIGINAL_REQUEST.md`: `H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\ORIGINAL_REQUEST.md`
- `PROJECT.md`: `H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\PROJECT.md`
- `docs_chuc_nang_va_chinh_sua/07_KHU_AI_VA_CHONG_DAO_VAN_TURNITIN.md`
- `docs_chuc_nang_va_chinh_sua/00_CAU_TRUC_VA_GIAO_DIEN_WEB_SUPER.md`
- `modules/turnitin_humanizer/`
- `modules/shared/docx_styler.py`
- `static/index.html`
- `static/js/` (all JS files)

## Output Deliverable
Write `analysis.md` and `handoff.md` in your directory `.agents/explorer_survey_3/` detailing architecture findings, gap analysis, and implementation roadmap.
