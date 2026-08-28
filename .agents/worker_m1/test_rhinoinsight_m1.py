# .agents/worker_m1/test_rhinoinsight_m1.py
"""
Targeted Verification Test Suite for Milestone M1 (RhinoInsight 2-Phase Workflow):
1. Structured Outline Tree Generation (Phase 1)
2. Branch Expansion (Add Items / Sub-branches)
3. Dimension Addition (Add Dimensions / Fields)
4. Outline Locking & Approval Gate
5. Bidirectional Markdown <-> Outline Tree Conversion
6. Section Parser with Dict / JSON Support
7. FastAPI Router Endpoints for Writer Router
8. Generate 2-Files with Outline Tree & Uncertainty Tracking
"""

import sys
import os
import json
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

print("======================================================================")
print("   RHINOINSIGHT M1 (DEEP RESEARCH WORKFLOW) VERIFICATION SUITE       ")
print("======================================================================")

passed = 0
total = 0

def test(name, condition, details=""):
    global passed, total
    total += 1
    if condition:
        passed += 1
        print(f"  [PASS] {name}")
    else:
        print(f"  [FAIL] {name} - Details: {details}")
        assert False, f"Test failed: {name} - {details}"

from modules.academic_writer.academic_writer_engine import academic_writer, AcademicWriterEngine

# ── TEST 1: Structured Outline Generation ──────────────────────────────────────
print("\n--- 1. Kiểm thử Sinh Cây Đề Cương Có Cấu Trúc (Phase 1 Outline Tree) ---")
res_tree = academic_writer.propose_structured_outline(
    topic="Ứng dụng Học Sâu trong Tối ưu Năng lượng Lưới điện Thông minh",
    paper_type="Báo cáo khoa học",
    depth_level="comprehensive"
)

test("Trạng thái sinh đề cương thành công", res_tree.get("status") == "success")
tree = res_tree.get("outline_tree", {})
test("Cây đề cương chứa danh sách items (chương mục)", isinstance(tree.get("items"), list) and len(tree["items"]) >= 6)
test("Cây đề cương chứa 5 chiều phân tích (dimensions)", isinstance(tree.get("dimensions"), list) and len(tree["dimensions"]) >= 5)
test("Mục 1 chứa các tiểu mục (subsections)", len(tree["items"][0].get("subsections", [])) >= 3)
test("Cây đề cương sinh kèm Markdown outline tương thích", "## 1." in res_tree.get("markdown_outline", ""))

# ── TEST 2: Branch Expansion ──────────────────────────────────────────────────
print("\n--- 2. Kiểm thử Mở Rộng Nhánh Luận Điểm (Branch Expansion) ---")
res_expand_sub = academic_writer.expand_outline_branch(
    topic="Ứng dụng Học Sâu trong Tối ưu Năng lượng Lưới điện Thông minh",
    outline_tree=tree,
    target_node_id="sec_4",
    expansion_prompt="Đối sánh hiệu năng giữa mô hình PINN và DRL truyền thống"
)

test("Mở rộng nhánh tiểu mục thành công", res_expand_sub.get("status") == "success")
updated_tree = res_expand_sub.get("outline_tree", {})
sec_4 = next(it for it in updated_tree["items"] if it["id"] == "sec_4")
test("Mục 4 có thêm tiểu mục mới", len(sec_4["subsections"]) >= 4)
test("Tiểu mục mới chứa nội dung prompt", any("PINN" in s.get("title", "") or "PINN" in s.get("focus", "") for s in sec_4["subsections"]))

# Expand new section
res_expand_sec = academic_writer.expand_outline_branch(
    topic="Ứng dụng Học Sâu trong Tối ưu Năng lượng Lưới điện Thông minh",
    outline_tree=updated_tree,
    target_node_id="",
    expansion_prompt="Phân tích Rủi ro An ninh Mạng và Cơ chế Tự Phục Hồi"
)
test("Mở rộng thêm chương mục mới thành công", len(res_expand_sec["outline_tree"]["items"]) >= 7)

# ── TEST 3: Add Dimension ─────────────────────────────────────────────────────
print("\n--- 3. Kiểm thử Bổ Sung Chiều Phân Tích (Add Dimension / Fields) ---")
res_dim = academic_writer.add_outline_dimension(
    topic="Ứng dụng Học Sâu trong Tối ưu Năng lượng Lưới điện Thông minh",
    outline_tree=res_expand_sec["outline_tree"],
    dimension_name="Chỉ số Chi phí Năng lượng Quy dẫn (LCOE)",
    dimension_description="Đánh giá tính khả thi kinh tế - tài chính"
)
test("Thêm dimension thành công", res_dim.get("status") == "success")
test("Danh sách dimensions chứa chỉ số mới", "Chỉ số Chi phí Năng lượng Quy dẫn (LCOE)" in res_dim.get("dimensions", []))

# ── TEST 4: Lock Outline Structure (Approval Gate) ────────────────────────────
print("\n--- 4. Kiểm thử Cổng Phê Duyệt & Khóa Đề Cương (Approval Gate) ---")
res_lock = academic_writer.lock_structured_outline(
    topic="Ứng dụng Học Sâu trong Tối ưu Năng lượng Lưới điện Thông minh",
    outline_tree=res_dim["outline_tree"]
)
test("Khóa đề cương thành công", res_lock.get("is_locked") is True)
test("Cây đề cương ghi nhận thời gian khóa", bool(res_lock["outline_tree"].get("locked_at")))
test("Báo cáo tổng kết đếm đúng số chương mục", res_lock["summary"]["total_sections"] >= 7)

# ── TEST 5: Bidirectional Markdown <-> Outline Tree Conversion ────────────────
print("\n--- 5. Kiểm thử Chuyển Đổi Hai Chiều Markdown <-> Outline Tree ---")
md_str = academic_writer.outline_tree_to_markdown(res_lock["outline_tree"])
test("Chuyển đổi Outline Tree sang Markdown đầy đủ", "# CẤU TRÚC ĐỀ CƯƠNG" in md_str and "## 1." in md_str)

converted_tree = academic_writer.markdown_to_outline_tree(md_str, topic="Chuyển đổi năng lượng", paper_type="Báo cáo khoa học")
test("Chuyển đổi Markdown sang Outline Tree thành công", len(converted_tree.get("items", [])) >= 6)
test("Chương 1 sau khi parse có danh sách subsections", len(converted_tree["items"][0].get("subsections", [])) >= 1)

# ── TEST 6: Section Parser with Dict / JSON Support ───────────────────────────
print("\n--- 6. Kiểm thử Section Parser hỗ trợ Dict và JSON Tree ---")
sec_plan_dict = academic_writer.parse_outline_into_sections(converted_tree)
test("Parser bóc tách mượt mà từ Dictionary", len(sec_plan_dict) >= 6)

json_tree_str = json.dumps(converted_tree, ensure_ascii=False)
sec_plan_json = academic_writer.parse_outline_into_sections(json_tree_str)
test("Parser bóc tách mượt mà từ JSON string", len(sec_plan_json) >= 6)

# ── TEST 7: Writer Router Endpoints ───────────────────────────────────────────
print("\n--- 7. Kiểm thử FastAPI Endpoints trong writer_router.py ---")
from modules.academic_writer.writer_router import writer_router

routes = [r.path for r in writer_router.routes]
test("Endpoint /api/writer/outline tồn tại", "/api/writer/outline" in routes)
test("Endpoint /api/writer/outline/structured tồn tại", "/api/writer/outline/structured" in routes)
test("Endpoint /api/writer/outline/expand-branch tồn tại", "/api/writer/outline/expand-branch" in routes)
test("Endpoint /api/writer/outline/add-dimension tồn tại", "/api/writer/outline/add-dimension" in routes)
test("Endpoint /api/writer/outline/lock tồn tại", "/api/writer/outline/lock" in routes)
test("Endpoint /api/writer/generate-2file tồn tại", "/api/writer/generate-2file" in routes)

# ── TEST 8: Backward Compatibility with Propose Structure ─────────────────────
print("\n--- 8. Kiểm thử Tương thích ngược propose_structure ---")
res_legacy = academic_writer.propose_structure(topic="Tối ưu năng lượng")
test("propose_structure trả về status success", res_legacy.get("status") == "success")
test("propose_structure trả về chuỗi outline", isinstance(res_legacy.get("outline"), str) and len(res_legacy["outline"]) > 50)
test("propose_structure trả về outline_tree đồng thời", isinstance(res_legacy.get("outline_tree"), dict))

print(f"\n======================================================================")
print(f"   KẾT QUẢ KIỂM THỬ M1: {passed}/{total} TESTS PASS (100% THÀNH CÔNG) ")
print(f"======================================================================")
