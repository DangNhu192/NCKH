# BRIEFING — 2026-08-27T00:58:00Z

## Mission
Implement Requirement R3: AI Humanizer Chuyên Sâu (Multi-pass LLM Rewriting optimizing Burstiness sigma >= 8.0 & Perplexity, Fixing runtime crash bugs, and In-Place Word DOM Token Shielding preserving Zotero XML field codes, Headings, and 300 DPI images).

## 🔒 My Identity
- Archetype: worker
- Roles: implementer, qa, specialist
- Working directory: H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\worker_m3
- Original parent: 84efa4a4-2ee5-45a9-8776-f2252de6f7b4
- Milestone: M3 (AI Humanizer & Word In-Place DOM Preservation)

## 🔒 Key Constraints
- Owned files:
  - modules/humanizer/humanizer_engine.py
  - modules/humanizer/humanizer_router.py
  - modules/shared/docx_styler.py
  - static/js/humanizer.js
  - static/js/turnitin.js
- Zero Fabrication (100% evidence-first citations, valid DOI resolution, Word Zotero CSL XML)
- In-Place DOM Word (.docx) Preservation (Heading 1/2/3, 300 DPI images, #CBD5E1 grid tables, OMML, CSL fields `w:fldSimple` / `w:fldChar`)
- Vietnamese Decimal & Thousands formatting (1,5; 28,5%; 1.000; 50.000)
- Math & Chemistry formatting (UNICODE_CHEM_MAP compounds/ions, LaTeX/OMML integration)
- Multi-pass LLM rewriting with high burstiness (sigma >= 8.0) and high perplexity while preserving facts, numbers, citations.

## Current Parent
- Conversation ID: 84efa4a4-2ee5-45a9-8776-f2252de6f7b4
- Updated: 2026-08-27T00:58:00Z

## Task Summary
- **What to build**:
  1. Fix runtime crash bugs in `humanizer_paragraph_by_paragraph` in `modules/humanizer/humanizer_engine.py`.
  2. Implement specialized multi-pass LLM rewriting optimizing Burstiness ($\sigma \ge 8.0$) and Perplexity while preserving academic facts, numbers, and formulas.
  3. Implement In-Place Word DOM Token Shielding (`{{ZOTERO_REF_i}}`) in `humanize_docx_bytes` to 100% preserve `w:fldSimple` Zotero XML field codes, Headings, and 300 DPI images.
- **Success criteria**:
  - No runtime crashes.
  - LLM rewriting optimizes Burstiness ($\sigma \ge 8.0$) and removes clichés/tells while retaining facts.
  - `humanize_docx_bytes` shields Zotero citations `{{ZOTERO_REF_i}}`, preserves headings (English, Vietnamese, `w:outlineLvl`), and keeps images/tables intact.
  - Verification suite passes 100% using `.venv\Scripts\python.exe`.
  - Update `docs_chuc_nang_va_chinh_sua/07_KHU_AI_VA_CHONG_DAO_VAN_TURNITIN.md`.
  - Write `handoff.md`.
- **Interface contracts**: PROJECT.md, docs_chuc_nang_va_chinh_sua/07_KHU_AI_VA_CHONG_DAO_VAN_TURNITIN.md

## Key Decisions Made
- [TBD - analyzing codebase]

## Artifact Index
- handoff.md — Final Milestone M3 Handoff Report

