# DISPATCH — Worker M3 (AI Humanizer & Word In-Place DOM Preservation)

## Mission
Implement Requirement R3: Upgrade AI Humanizer with specialized LLM restructuring (Burstiness & Perplexity adjustment) and 100% In-Place Word DOM Preservation.

## Reference & Specifications
- `ORIGINAL_REQUEST.md`: `H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\ORIGINAL_REQUEST.md`
- `PROJECT.md`: `H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\PROJECT.md`
- Explorer 3 Analysis: `H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\explorer_survey_3\analysis.md`
- Explorer 3 Handoff: `H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\explorer_survey_3\handoff.md`

## File Ownership
- `modules/humanizer/humanizer_engine.py`
- `modules/humanizer/humanizer_router.py`
- `modules/shared/docx_styler.py`
- `static/js/turnitin.js`

## Detailed Tasks
1. **Fix Runtime Bugs:** Fix missing methods `replace_cliches_deterministic` and `break_sentence_lengths` in `humanize_paragraph_by_paragraph`.
2. **Specialized LLM Restructuring:** Replace crude regex substitutions with LLM multi-pass humanization optimizing Burstiness ($\sigma \ge 8,0$) and Perplexity while preserving academic semantics, numbers, and formulas.
3. **In-Place Word DOM Token Shielding:** In `humanize_docx_bytes`, implement Token Shielding (`{{ZOTERO_REF_i}}`) to preserve `w:fldSimple` / `w:fldChar` Zotero citation XML nodes, Headings (including Vietnamese headings), and 300 DPI images (`<w:drawing>`).

## 2026-08-27T00:57:07Z

You are Worker M3 (AI Humanizer & Word In-Place DOM Implementer).
Your working directory is H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\worker_m3.
Read your DISPATCH.md at H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\worker_m3\DISPATCH.md and ORIGINAL_REQUEST.md at H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\ORIGINAL_REQUEST.md.
Implement R3:
1. Fix runtime crash bugs in humanizer_paragraph_by_paragraph in modules/humanizer/humanizer_engine.py.
2. Implement specialized multi-pass LLM rewriting optimizing Burstiness (sigma >= 8.0) and Perplexity while preserving academic facts, numbers, and formulas.
3. Implement In-Place Word DOM Token Shielding ({{ZOTERO_REF_i}}) in humanize_docx_bytes to 100% preserve w:fldSimple Zotero XML field codes, Headings, and 300 DPI images.
Test your changes using .venv\Scripts\python.exe, update docs_chuc_nang_va_chinh_sua/07_KHU_AI_VA_CHONG_DAO_VAN_TURNITIN.md, and write handoff.md. Report completion back when done.

