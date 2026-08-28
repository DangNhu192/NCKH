## 2026-08-26T09:42:25Z
You are worker_m1_2 (replacement worker for Academic Integrity & Skill System).

Working directory: H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\worker_m1_2
Original Request: H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\ORIGINAL_REQUEST.md
PROJECT document: H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\PROJECT.md
Survey Analysis: H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\explorer_survey_1\analysis.md
Survey Handoff: H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\explorer_survey_1\handoff.md
Root workspace: H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super
Parent Workspace: H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill

EXCLUSIVE FILE OWNERSHIP:
- `modules/academic/academic_writer_engine.py`
- `modules/humanizer/humanizer_engine.py`
- `modules/workspace/docx_converter.py`
- `modules/zotero/zotero_converter_engine.py`
- `H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\01_BO_NAO_AI_RESEARCHER\SKILL.md`

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

TASKS (Execute directly using file replacement and run tests):
1. In `modules/academic/academic_writer_engine.py`: Remove synthetic fallback DOIs/citations (around lines 567-588); ensure fallback queries genuine sources or provides a clear explicit non-fabricated notification. Enforce zero fabrication across all generated citations.
2. In `modules/humanizer/humanizer_engine.py`: Fix lines 304-305 where `val.startswith("10.")` suppresses decimal conversion for numbers 10.0-10.999. Use strict DOI pattern `re.match(r'^10\.\d{4,9}/', val)`.
3. In `modules/workspace/docx_converter.py` and `modules/zotero/zotero_converter_engine.py`: Ensure inserting `<w:fldSimple>` Zotero CSL XML preserves surrounding Run formatting in the paragraph.
4. In `H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\01_BO_NAO_AI_RESEARCHER\SKILL.md`: Update Tệp B specification to strictly define the 6-Column Evidence Audit Matrix (`STT`, `Luận điểm`, `Tác giả & Năm`, `Tệp Monograph Gốc`, `Trích đoạn nguyên văn`, `Bản dịch tiếng Việt`).
5. Run test verifications on modified modules using python in .venv (`& "H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\.venv\Scripts\python.exe"`).

OUTPUT REQUIREMENTS:
Write changes and test results to `H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\worker_m1_2\handoff.md`.
Maintain `progress.md`. When done, send a message to parent with summary and test results.
