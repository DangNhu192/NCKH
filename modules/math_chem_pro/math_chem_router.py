"""
math_chem_router.py
===================
FastAPI Router cho phân hệ Biên Tập Công Thức Toán - Hóa, Sơ Đồ Quy Trình & Biểu Đồ Khoa Học 300 DPI (Math-Chem-Chart Pro).
Hỗ trợ 3 chế độ nâng cấp:
1. 'math_chem_only': Chỉ fix & chuẩn hóa công thức Toán học và Hóa học.
2. 'images_only': Chỉ thêm / tạo và nhúng hình ảnh, biểu đồ, sơ đồ quy trình 300 DPI.
3. 'both': Thực hiện cả 2 chức năng đồng thời.
"""

import os
import sys
import uuid
import json
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Optional, List, Dict, Any

import io
import re
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from modules.shared.file_manager import file_mgr
from modules.shared.docx_styler import DocxStyler, sanitize_and_repair_docx
from modules.shared.docx_formula_engine import (
    latex_to_mathml, mathml_to_omml, latex_to_omml,
    add_latex_equation, format_inline_chemical_formulas,
    scan_and_enhance_document_formulas, format_chemical_text,
    UNICODE_CHEM_MAP
)
from modules.shared.scientific_chart_builder import (
    ScientificChartGenerator, FlowchartBuilder,
    download_and_optimize_image, ACADEMIC_COLORS
)
from modules.shared.gemini_service import gemini_service
from modules.shared.pubchem_service import pubchem_service

math_chem_router = APIRouter(prefix="/api/math-chem", tags=["Math-Chem-Chart Pro"])

WORKSPACE_DIR = file_mgr.workspace
FIGURES_DIR = WORKSPACE_DIR / "figures"
DOCS_DIR = file_mgr.drafts_dir
try:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
except OSError:
    pass
try:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
except OSError:
    pass


# --- REQUEST SCHEMAS ---

class EquationConvertRequest(BaseModel):
    latex: str
    equation_number: Optional[str] = "1.1"

class InterpretationRequest(BaseModel):
    latex: str
    equation_name: Optional[str] = ""
    domain: Optional[str] = ""

class ChartGenerateRequest(BaseModel):
    chart_type: str = "bar"
    title: str = "Biểu đồ khoa học"
    xlabel: str = "Chỉ số / Nhóm"
    ylabel: str = "Giá trị đo lường"
    categories: List[str] = []
    values: List[float] = []
    series_dict: Optional[Dict[str, List[float]]] = None

class FlowchartRequest(BaseModel):
    title: str = "Sơ đồ quy trình công nghệ"
    steps: List[Dict[str, str]] = []

class ImageSearchRequest(BaseModel):
    query: str
    limit: int = 8

class ImageDownloadRequest(BaseModel):
    url: str
    filename: Optional[str] = None


# --- API ENDPOINTS ---

@math_chem_router.post("/convert-equation")
def convert_equation(req: EquationConvertRequest):
    """Chuyển đổi công thức LaTeX sang MathML và OMML (<m:oMath>)."""
    try:
        mathml = latex_to_mathml(req.latex)
        omml = mathml_to_omml(mathml)
        return {
            "success": True,
            "latex": req.latex,
            "mathml": mathml,
            "omml": omml,
            "omml_xml": omml,
            "equation_number": req.equation_number
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lỗi chuyển đổi công thức: {str(e)}")


@math_chem_router.post("/generate-interpretation")
def generate_interpretation(req: InterpretationRequest):
    """AI tự động sinh đoạn văn diễn giải chi tiết 4 yếu tố theo Quy tắc Interpretation Rule."""
    try:
        prompt = f"""Bạn là Chuyên gia biên tập học thuật quốc tế (Scopus/Nature/Elsevier).
Hãy viết đoạn văn diễn giải chi tiết cho công thức/phương trình khoa học sau:
- Phương trình (LaTeX): $${req.latex}$$
- Tên gọi đề xuất: {req.equation_name or "Phương trình khoa học"}
- Lĩnh vực / Bối cảnh: {req.domain or "Khoa học Tự nhiên / Môi trường / Kỹ thuật"}

YÊU CẦU BẮT BUỘC ĐÁP ỨNG ĐẦY ĐỦ 4 YẾU TỐ:
1. Tên gọi và mục đích sử dụng cụ thể của phương trình.
2. Định nghĩa rõ ràng từng biến số, tham số và hằng số có mặt trong công thức.
3. Đơn vị đo lường chuẩn khoa học (ví dụ: mg/L, kg/ha/năm, %, ppm, cm/năm, t CO2eq/ha).
4. Ý nghĩa thực tiễn, liên hệ cơ chế khoa học / môi trường / kinh tế sinh thái.

Phong cách viết: Học thuật, chuẩn mực, khúc chiết, mạch lạc (khoảng 100 - 180 từ).
Chỉ trả về trực tiếp đoạn văn diễn giải tiếng Việt có dấu, không kèm lời chào hỏi hay tiêu đề phụ."""

        gemini_res = gemini_service.generate_content(prompt)
        interpretation_text = gemini_res.get("text", "").strip() if isinstance(gemini_res, dict) else str(gemini_res).strip()
        
        if not interpretation_text:
            interpretation_text = f"Phương trình mô tả động thái biến thiên và quan hệ hàm số giữa các thông số cốt lõi trong hệ thống. Các biến số được chuẩn hóa theo đơn vị đo lường tiêu chuẩn, phản ánh định lượng cơ chế tương tác và cung cấp cơ sở tin cậy cho việc mô hình hóa thực nghiệm."

        return {
            "success": True,
            "latex": req.latex,
            "interpretation": interpretation_text
        }
    except Exception as e:
        return {
            "success": True,
            "latex": req.latex,
            "interpretation": f"Phương trình biểu diễn mối tương quan định lượng giữa các biến số thành phần trong mô hình nghiên cứu, đóng vai trò then chốt trong việc đánh giá cơ chế lý hóa và lượng hóa các chỉ tiêu khoa học."
        }


@math_chem_router.post("/generate-chart")
def generate_chart(req: ChartGenerateRequest):
    """Tạo biểu đồ khoa học Tiếng Việt chất lượng cao 300 DPI."""
    try:
        gen = ScientificChartGenerator()
        chart_id = f"chart_{uuid.uuid4().hex[:8]}"
        out_path = FIGURES_DIR / f"{chart_id}.png"
        
        if req.chart_type == "line" and req.series_dict:
            gen.plot_line_chart(
                x_data=req.categories,
                series_dict=req.series_dict,
                title=req.title,
                xlabel=req.xlabel,
                ylabel=req.ylabel,
                output_path=str(out_path)
            )
        else:
            gen.plot_bar_chart(
                categories=req.categories if req.categories else ["Mẫu A", "Mẫu B", "Mẫu C"],
                values=req.values if req.values else [10.5, 25.3, 18.7],
                title=req.title,
                xlabel=req.xlabel,
                ylabel=req.ylabel,
                output_path=str(out_path)
            )
            
        return {
            "success": True,
            "chart_id": chart_id,
            "filename": f"{chart_id}.png",
            "file_url": f"/workspace/figures/{chart_id}.png",
            "title": req.title
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tạo biểu đồ: {str(e)}")


@math_chem_router.post("/generate-flowchart")
def generate_flowchart(req: FlowchartRequest):
    """Tạo sơ đồ quy trình công nghệ / lưu đồ khối 300 DPI."""
    try:
        builder = FlowchartBuilder()
        chart_id = f"flowchart_{uuid.uuid4().hex[:8]}"
        out_path = FIGURES_DIR / f"{chart_id}.png"
        
        steps = req.steps if req.steps else [
            {"title": "Thu Thập Mẫu", "desc": "Lấy mẫu thực địa"},
            {"title": "Xử Lý Lý Hóa", "desc": "Đo đạc thông số"},
            {"title": "Mô Hình Hóa", "desc": "Đánh giá kết quả"}
        ]
        
        builder.build_linear_process(
            steps=steps,
            title=req.title,
            output_path=str(out_path)
        )
        
        return {
            "success": True,
            "chart_id": chart_id,
            "filename": f"{chart_id}.png",
            "file_url": f"/workspace/figures/{chart_id}.png",
            "title": req.title
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tạo sơ đồ quy trình: {str(e)}")


@math_chem_router.post("/search-images")
def search_images(req: ImageSearchRequest):
    """Tìm kiếm ảnh khoa học mở chất lượng cao từ Wikimedia Commons API."""
    try:
        search_query = urllib.parse.quote(req.query)
        api_url = (
            f"https://commons.wikimedia.org/w/api.php?action=query&generator=search"
            f"&gsrnamespace=6&gsrsearch={search_query}&gsrlimit={req.limit}"
            f"&prop=imageinfo&iiprop=url|size|mime|extmetadata&format=json"
        )
        headers = {'User-Agent': 'AcademicResearchBot/2.0 (contact@research.edu.vn)'}
        req_obj = urllib.request.Request(api_url, headers=headers)
        
        with urllib.request.urlopen(req_obj, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            
        results = []
        pages = data.get("query", {}).get("pages", {})
        for page_id, page in pages.items():
            image_info = page.get("imageinfo", [{}])[0]
            url = image_info.get("url")
            thumb_url = image_info.get("thumburl", url)
            title = page.get("title", "").replace("File:", "")
            if url and ("jpg" in url.lower() or "png" in url.lower() or "jpeg" in url.lower()):
                results.append({
                    "title": title,
                    "url": url,
                    "thumb_url": thumb_url or url,
                    "width": image_info.get("width", 0),
                    "height": image_info.get("height", 0)
                })
                
        return {"success": True, "query": req.query, "results": results}
    except Exception as e:
        return {"success": True, "query": req.query, "results": []}


@math_chem_router.post("/download-image")
def download_image(req: ImageDownloadRequest):
    """Tải và chuẩn hóa ảnh 300 DPI từ URL."""
    try:
        img_id = f"img_{uuid.uuid4().hex[:8]}"
        out_name = f"{img_id}.png"
        out_path = FIGURES_DIR / out_name
        
        saved = download_and_optimize_image(req.url, str(out_path))
        if not saved:
            raise HTTPException(status_code=400, detail="Không thể tải ảnh từ URL cung cấp.")
            
        return {
            "success": True,
            "filename": out_name,
            "file_url": f"/workspace/figures/{out_name}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tải ảnh: {str(e)}")


@math_chem_router.get("/workspace-docx-files")
def get_workspace_docx_files():
    """Lấy danh sách các tệp .docx có sẵn trong Workspace phục vụ chọn nhanh để nâng cấp."""
    files = []
    for cat, dir_path in [
        ("Ban_Thao", file_mgr.drafts_dir),
        ("Tai_Lieu", file_mgr.docs_dir),
        ("Xuat_Ban", file_mgr.publish_dir),
        ("Zotero_Converted", file_mgr.zotero_dir)
    ]:
        if dir_path.exists():
            for p in dir_path.glob("*.docx"):
                try:
                    stat = p.stat()
                    files.append({
                        "name": p.name,
                        "rel_path": f"{cat}/{p.name}",
                        "category": cat,
                        "size": stat.st_size,
                        "mtime": stat.st_mtime
                    })
                except Exception:
                    pass
    files.sort(key=lambda x: x["mtime"], reverse=True)
    return {"success": True, "files": files}


@math_chem_router.post("/enhance-docx")
async def enhance_docx(
    file: Optional[UploadFile] = File(None),
    workspace_file_path: Optional[str] = Form(None),
    mode: str = Form("both"),  # 'math_chem_only', 'images_only', 'both'
    normalize_chem: bool = Form(True),
    normalize_decimals: bool = Form(True),
    convert_latex_blocks: bool = Form(True),
    add_equation_latex: Optional[str] = Form(None),
    equation_number: Optional[str] = Form(None),
    equation_interpretation: Optional[str] = Form(None),
    image_filename: Optional[str] = Form(None),
    image_caption: Optional[str] = Form(None)
):
    """
    Nâng cấp 1-Click tài liệu Word (.docx) toàn diện:
    - Sửa chữa và khử lỗi đóng gói word/media bằng sanitize_and_repair_docx.
    - Quét chuẩn hóa ký hiệu hóa học (FeS₂, H₂SO₄, NH₄⁺...) trong cả đoạn văn và bảng biểu.
    - Chuẩn hóa số thập phân tiếng Việt (1,5; 28,5%) và phân cách hàng nghìn (1.000; 50.000).
    - Tự động chuyển đổi các công thức LaTeX $$...$$ thành OMML Microsoft Word Equation.
    - Chèn công thức OMML mới và lời diễn giải 4 yếu tố.
    - Nhúng hình ảnh / sơ đồ 300 DPI kèm caption chuẩn APA.
    - Lưu kết quả vào workspace/Ban_Thao/ đồng bộ với Trình Biên Tập Số Liệu.
    """
    try:
        content_bytes = None
        orig_filename = "Document.docx"

        if file and file.filename:
            orig_filename = file.filename
            content_bytes = await file.read()
        elif workspace_file_path and workspace_file_path.strip():
            clean_ws = workspace_file_path.strip().replace("\\", "/").lstrip("/")
            ws_path = (file_mgr.workspace / clean_ws).resolve()
            if not ws_path.exists():
                raise HTTPException(status_code=404, detail=f"Không tìm thấy tệp trong Workspace: {clean_ws}")
            orig_filename = ws_path.name
            with open(ws_path, "rb") as f:
                content_bytes = f.read()
        else:
            raise HTTPException(status_code=400, detail="Vui lòng tải lên 1 tệp Word (.docx) hoặc chọn 1 tệp có sẵn trong Workspace.")

        if not content_bytes:
            raise HTTPException(status_code=400, detail="Nội dung tệp rỗng.")

        # 2. Khử lỗi đóng gói word/media và các định dạng bất thường
        repaired_bytes = sanitize_and_repair_docx(content_bytes)
        doc = Document(io.BytesIO(repaired_bytes))

        styler = DocxStyler()
        chem_count = 0
        eq_added = 0
        img_added = 0
        decimal_count = 0

        # --- MODE 1 & 3: XỬ LÝ TOÁN & HÓA HỌC & SỐ THẬP PHÂN ---
        doc_stats = {}
        if mode in ["math_chem_only", "both"]:
            doc_stats = scan_and_enhance_document_formulas(
                doc,
                normalize_chem=normalize_chem,
                normalize_decimals=normalize_decimals,
                convert_latex_blocks=convert_latex_blocks,
                convert_inline_math=True
            )
            chem_count = doc_stats.get("chem_fixes", 0)
            decimal_count = doc_stats.get("decimal_fixes", 0)
            eq_added = doc_stats.get("block_equations", 0) + doc_stats.get("inline_equations", 0)

            # Chèn thêm công thức OMML mới nếu người dùng yêu cầu
            if add_equation_latex and add_equation_latex.strip():
                p_eq = doc.add_paragraph()
                p_eq.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_eq.paragraph_format.space_before = Pt(6)
                p_eq.paragraph_format.space_after = Pt(6)
                add_latex_equation(p_eq, add_equation_latex.strip(), equation_number)
                eq_added += 1

                if equation_interpretation and equation_interpretation.strip():
                    p_interp = doc.add_paragraph()
                    p_interp.paragraph_format.first_line_indent = Inches(0.4)
                    p_interp.paragraph_format.line_spacing = 1.25
                    p_interp.paragraph_format.space_after = Pt(6)
                    run_i = p_interp.add_run(equation_interpretation.strip())
                    run_i.font.name = "Times New Roman"
                    run_i.font.size = Pt(11)
                    run_i.font.italic = True

        # --- MODE 2 & 3: XỬ LÝ HÌNH ẢNH / BIỂU ĐỒ 300 DPI ---
        if mode in ["images_only", "both"]:
            if image_filename and image_filename.strip():
                clean_img_name = Path(image_filename.strip()).name
                candidate_paths = [
                    FIGURES_DIR / clean_img_name,
                    file_mgr.workspace / "charts" / clean_img_name,
                    file_mgr.workspace / "figures" / clean_img_name,
                    file_mgr.workspace / "Tai_Lieu" / "PDFs" / clean_img_name,
                    file_mgr.workspace / clean_img_name
                ]
                resolved_img = None
                for c_path in candidate_paths:
                    if c_path.exists() and c_path.is_file():
                        resolved_img = c_path
                        break

                if resolved_img:
                    p_img = doc.add_paragraph()
                    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p_img.paragraph_format.space_before = Pt(12)
                    p_img.paragraph_format.space_after = Pt(4)
                    run_img = p_img.add_run()
                    run_img.add_picture(str(resolved_img), width=Inches(5.5))

                    cap_text = image_caption.strip() if image_caption else f"Hình: {clean_img_name}"
                    p_cap = doc.add_paragraph()
                    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p_cap.paragraph_format.space_before = Pt(2)
                    p_cap.paragraph_format.space_after = Pt(12)
                    run_cap = p_cap.add_run(cap_text)
                    run_cap.font.name = "Times New Roman"
                    run_cap.font.size = Pt(11)
                    run_cap.font.bold = True
                    run_cap.font.italic = True
                    run_cap.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
                    img_added += 1

        # Lưu file đã nâng cấp vào Ban_Thao trong Workspace
        clean_base = re.sub(r'^(?:Enhanced_[a-zA-Z_]+_)+', '', orig_filename)
        output_name = f"Enhanced_{mode}_{clean_base}"
        if not output_name.lower().endswith(".docx"):
            output_name += ".docx"

        rel_out = f"Ban_Thao/{output_name}"
        target_fpath = file_mgr.drafts_dir / output_name
        doc.save(str(target_fpath))

        stat = target_fpath.stat()
        return {
            "success": True,
            "mode": mode,
            "filename": output_name,
            "rel_path": rel_out,
            "abs_path": str(target_fpath).replace("/", "\\"),
            "file_url": f"/workspace/{rel_out}",
            "size": stat.st_size,
            "stats": {
                "chem_normalized": chem_count,
                "decimal_normalized": decimal_count,
                "equations_added": eq_added,
                "images_added": img_added,
                "tables_scanned": len(doc.tables),
                "paragraphs_count": len(doc.paragraphs)
            },
            "message": f"Đã nâng cấp file Word '{output_name}' thành công theo chế độ {mode.upper()}."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi nâng cấp file Word: {str(e)}")


# --- PUBCHEM CHEMICAL RESOLVER & PROPERTIES ---

@math_chem_router.post("/pubchem-resolve")
def resolve_chemical_substance(payload: dict):
    """
    Tra cứu và phân giải danh pháp, cấu trúc và thuộc tính hóa học từ NCBI PubChem REST API:
    - CID, SMILES, InChIKey, IUPAC Name, Khối lượng phân tử.
    - Cung cấp dữ liệu chuẩn hóa cho nghiên cứu thổ nhưỡng, hóa chất BVTV, nông nghiệp, môi trường.
    """
    name = payload.get("name", "")
    if not name or not name.strip():
        raise HTTPException(status_code=400, detail="Vui lòng cung cấp tên hoặc công thức hóa học cần tra cứu.")

    res = pubchem_service.resolve_compound(name.strip())
    return res


@math_chem_router.get("/pubchem-image/{cid}")
def get_chemical_structure_image(cid: int):
    """Lấy URL hình ảnh cấu trúc phân tử 2D độ nét cao từ PubChem."""
    if not cid:
        raise HTTPException(status_code=400, detail="CID không hợp lệ.")
    image_url = pubchem_service.get_structure_image_url(cid)
    return {
        "status": "success",
        "cid": cid,
        "image_url": image_url
    }
