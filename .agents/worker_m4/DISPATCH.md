# DISPATCH — Worker M4 (UI/UX Route Fixes & Snapshot Packaging into Xac_Nhan_Hoan_Hao/)

## Mission
Implement Requirement R4: UI/UX Route Fixes and Packaging Verified Modules into `Xac_Nhan_Hoan_Hao/`.

## Reference & Specifications
- `ORIGINAL_REQUEST.md`: `H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\ORIGINAL_REQUEST.md`
- `PROJECT.md`: `H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\PROJECT.md`
- Explorer 3 Analysis: `H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\explorer_survey_3\analysis.md`
- Explorer 3 Handoff: `H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\explorer_survey_3\handoff.md`

## File Ownership
- `static/js/pdf-ocr-reader.js`
- `routes/notebooklm_router.py` (add alias route if needed)
- `Xac_Nhan_Hoan_Hao/`
- `Xac_Nhan_Hoan_Hao/archive_manager.py`

## Detailed Tasks
1. **Fix Broken Endpoint in Frontend:** Sửa route tại `static/js/pdf-ocr-reader.js:287` từ `/api/open-notebook/list` thành `/api/notebooklm/notebooks` (và thêm alias tại backend `notebooklm_router.py` để tương thích ngược).
2. **Execute Verified Module Snapshot Packaging:** Sử dụng `archive_manager.py` để đóng gói các module hoàn chỉnh (Harvester, Zotero Converter, Math-Chem Pro, BigQuery AI) vào `Xac_Nhan_Hoan_Hao/Modules_Source_Code/` và ghi nhận nhật ký xác nhận.

## Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Verification Requirements
Run your tests using `.venv\Scripts\python.exe` and document snapshot creation and route verification in `handoff.md`.
