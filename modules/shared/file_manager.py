import os
import re
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

SKILL_ROOT = Path(__file__).resolve().parent.parent.parent.parent
WEB_SUPER_DIR = Path(__file__).resolve().parent.parent.parent

import tempfile

def safe_mkdir(p: Path):
    try:
        p.mkdir(parents=True, exist_ok=True)
    except (OSError, FileNotFoundError):
        pass

IS_VERCEL = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))
if IS_VERCEL:
    WORKSPACE_DIR = Path(tempfile.gettempdir()) / "workspace"
else:
    WORKSPACE_DIR = WEB_SUPER_DIR / "workspace"

safe_mkdir(WORKSPACE_DIR)

DOCS_DIR = WORKSPACE_DIR / "Tai_Lieu"
safe_mkdir(DOCS_DIR)

DRAFTS_DIR = WORKSPACE_DIR / "Ban_Thao"
safe_mkdir(DRAFTS_DIR)

PUBLISH_DIR = WORKSPACE_DIR / "Xuat_Ban"
safe_mkdir(PUBLISH_DIR)

LOGS_DIR = WORKSPACE_DIR / "Logs"
safe_mkdir(LOGS_DIR)

ZOTERO_DIR = WORKSPACE_DIR / "Zotero_Converted"
safe_mkdir(ZOTERO_DIR)

# Regex to detect chemical formula indices: e.g. CO2 -> CO + sub(2), H2SO4 -> H + sub(2) + SO + sub(4)
CHEM_SUBSCRIPTS = ["CO2", "CH4", "N2O", "FeS2", "H2SO4", "SO4", "Al3+", "Fe2+", "NH4+", "NO3-", "NO2-", "BOD5", "COD", "DO", "NaCl"]

class FileManager:
    def __init__(self):
        self.workspace = WORKSPACE_DIR
        self.docs_dir = DOCS_DIR
        self.drafts_dir = DRAFTS_DIR
        self.publish_dir = PUBLISH_DIR
        self.logs_dir = LOGS_DIR
        self.zotero_dir = ZOTERO_DIR

    def create_styled_document(self, title: str = "", author: str = "") -> docx.Document:
        """Creates a standardized academic Word document with A4 margins, Times New Roman, and headers"""
        doc = docx.Document()
        for section in doc.sections:
            section.top_margin = Inches(0.98)     # 2.5 cm
            section.bottom_margin = Inches(0.79)  # 2.0 cm
            section.left_margin = Inches(1.18)    # 3.0 cm
            section.right_margin = Inches(0.79)   # 2.0 cm
            section.header_distance = Inches(0.5)
            section.footer_distance = Inches(0.5)
            
            if title:
                hdr = section.header
                p_hdr = hdr.paragraphs[0]
                p_hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                r_hdr = p_hdr.add_run(title[:70])
                r_hdr.font.name = "Times New Roman"
                r_hdr.font.size = Pt(8.5)
                r_hdr.font.italic = True
                r_hdr.font.color.rgb = RGBColor(100, 116, 139)
        return doc

    def list_files(self, category=None):
        target = self.workspace
        if category == "docs":
            target = self.docs_dir
        elif category == "drafts":
            target = self.drafts_dir
        elif category == "publish":
            target = self.publish_dir
        elif category == "zotero":
            target = self.zotero_dir

        files = []
        for root, _, filenames in os.walk(target):
            for fname in filenames:
                fpath = Path(root) / fname
                try:
                    rel_path = fpath.relative_to(self.workspace)
                    abs_path_str = str(fpath.resolve()).replace("/", "\\")
                    file_url = f"file:///{fpath.resolve().as_posix()}"
                    stat = fpath.stat()
                    files.append({
                        "name": fname,
                        "rel_path": str(rel_path).replace("\\", "/"),
                        "abs_path": abs_path_str,
                        "file_url": file_url,
                        "size": stat.st_size,
                        "mtime": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                        "extension": fpath.suffix.lower()
                    })
                except Exception:
                    pass
        return sorted(files, key=lambda x: x["mtime"], reverse=True)

    def read_file(self, rel_path):
        fpath = (self.workspace / rel_path).resolve()
        if not str(fpath).startswith(str(self.workspace.resolve())):
            raise PermissionError("Truy cập bên ngoài Workspace bị từ chối.")
        
        if not fpath.exists():
            raise FileNotFoundError(f"Không tìm thấy file: {rel_path}")

        ext = fpath.suffix.lower()
        abs_path_str = str(fpath).replace("/", "\\")
        file_url = f"file:///{fpath.as_posix()}"

        if ext == ".docx":
            doc = docx.Document(fpath)
            paragraphs = []
            for p in doc.paragraphs:
                paragraphs.append(p.text)
            # Also extract tables if present
            table_texts = []
            for t_idx, table in enumerate(doc.tables, 1):
                rows_text = []
                for row in table.rows:
                    rows_text.append(" | ".join([cell.text.strip().replace("\n", " ") for cell in row.cells]))
                if rows_text:
                    table_texts.append(f"\n[BẢNG {t_idx}]\n" + "\n".join(rows_text))
            
            full_text = "\n".join(paragraphs)
            if table_texts:
                full_text += "\n\n" + "\n\n".join(table_texts)
            return {"content": full_text, "type": "docx", "abs_path": abs_path_str, "file_url": file_url}
        elif ext == ".pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(fpath)
                text = ""
                for page in reader.pages[:10]: # Read first 10 pages for preview
                    text += (page.extract_text() or "") + "\n--- HẾT TRANG ---\n"
                return {"content": text, "type": "pdf", "abs_path": abs_path_str, "file_url": file_url}
            except Exception as e:
                return {"content": f"Không thể trích xuất PDF: {e}", "type": "pdf", "abs_path": abs_path_str, "file_url": file_url}
        else:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            return {"content": content, "type": ext.lstrip("."), "abs_path": abs_path_str, "file_url": file_url}

    def _format_academic_run(self, run, text, is_bold=False, is_italic=False, is_heading=False, font_size=14):
        run.font.name = "Times New Roman"
        run.font.size = Pt(font_size)
        run.bold = is_bold
        run.italic = is_italic
        run.font.color.rgb = RGBColor(0, 0, 0)

    def _apply_vietnamese_decimal_and_subscripts(self, paragraph, raw_text, is_bold=False, is_italic=False, font_size=14):
        """Processes section dots retention (e.g. 1.1.) vs decimal comma (e.g. 1,5), and chemical formulas without modifying URLs or DOIs"""
        # 0. Bảo vệ tuyệt đối các định danh học thuật: URL (http/https), mã DOI (10.xxxx/...), tên tệp, email
        protected_tokens = []
        def save_protected(m):
            idx = len(protected_tokens)
            protected_tokens.append(m.group(0))
            return f"__SAFE_ACADEMIC_TOKEN_{idx}__"

        protect_regex = re.compile(
            r'(https?://[^\s<>"]+|doi\.org/[^\s<>"]+|10\.\d{4,9}/[^\s<>"\)]+|doi:\s*10\.\d{4,9}/[^\s<>"\)]+|[\w\.\-]+\.(?:docx|pdf|ris|py|json|html|xml|txt|png|jpg)|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            re.IGNORECASE
        )
        safe_text = protect_regex.sub(save_protected, raw_text)

        # 1. Bảo vệ đánh số mục đầu dòng (ví dụ 1.1., 2.3.4.)
        section_prefix = ""
        body_text = safe_text
        match_section = re.match(r'^(\d+(?:\.\d+)+\.?\s*)(.*)', safe_text)
        if match_section:
            section_prefix = match_section.group(1)
            body_text = match_section.group(2)
            run_sec = paragraph.add_run(section_prefix)
            self._format_academic_run(run_sec, section_prefix, is_bold=True, is_italic=is_italic, font_size=font_size)

        # 2. Chuyển dấu chấm thành dấu phẩy CHỈ CHO SỐ THẬP PHÂN ĐỨNG ĐỘC LẬP trong văn bản (ví dụ: 15.5% -> 15,5%)
        body_text = re.sub(r'(^|[\s\(])(\d+)\.(\d+)(?=[\s%\),;.]|$)', r'\1\2,\3', body_text)

        # 3. Phục hồi nguyên trạng 100% các token DOI, URL, tên tệp với dấu chấm chính xác
        for idx, orig_val in enumerate(protected_tokens):
            body_text = body_text.replace(f"__SAFE_ACADEMIC_TOKEN_{idx}__", orig_val)

        # 4. Xử lý định dạng chỉ số dưới (Subscript) cho các công thức hóa học (ví dụ: CO2, CH4, H2SO4)
        tokens = re.split(r'(\b[A-Z][a-z]?\d+(?:[A-Z][a-z]?\d*)*\b)', body_text)
        for token in tokens:
            if not token:
                continue
            if re.match(r'^[A-Za-z]+\d+[A-Za-z0-9]*$', token) and not token.startswith("http") and not token.startswith("10.") and not "doi" in token.lower():
                sub_parts = re.split(r'(\d+)', token)
                for sp in sub_parts:
                    if not sp:
                        continue
                    run = paragraph.add_run(sp)
                    self._format_academic_run(run, sp, is_bold=is_bold, is_italic=is_italic, font_size=font_size)
                    if sp.isdigit():
                        run.font.subscript = True
            else:
                run = paragraph.add_run(token)
                self._format_academic_run(run, token, is_bold=is_bold, is_italic=is_italic, font_size=font_size)

    def build_academic_docx(self, fpath: Path, title: str, content: str, references: list = None, charts: list = None):
        """Builds a strictly compliant Vietnamese Academic & Professional DOCX file (viet-chuyen-nghiep-v3.1 & APA 7th)"""
        doc = docx.Document()
        from modules.shared.docx_styler import DocxStyler
        DocxStyler.render_markdown_to_docx(doc, content, title=title, charts=charts)

        fpath.parent.mkdir(parents=True, exist_ok=True)
        try:
            doc.save(fpath)
            return fpath
        except PermissionError:
            alt_fpath = fpath.parent / f"{fpath.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{fpath.suffix}"
            doc.save(alt_fpath)
            return alt_fpath

    def build_traceability_matrix_docx(self, fpath: Path, topic: str, matrix_data: list):
        """Builds File B: 6-Column Traceability Matrix per SKILL_scientific-academic-writing.md"""
        try:
            from modules.shared.skill_prompts import MATRIX_HEADERS_6COL, MATRIX_COLUMN_WIDTHS_CM
        except ImportError:
            MATRIX_HEADERS_6COL = [
                "STT",
                "Du Lieu / So Lieu Trong Bao Cao",
                "Tac Gia & Nam (APA)",
                "Ten Tep PDF Goc",
                "Trich Doan Goc (Ngon Ngu Goc)",
                "Ban Dich Tieng Viet + Trang"
            ]
            MATRIX_COLUMN_WIDTHS_CM = [1.2, 5.5, 4.0, 3.5, 5.5, 5.5]

        doc = docx.Document()

        # Page layout: landscape-friendly margins
        for section in doc.sections:
            section.top_margin = Inches(0.8)
            section.bottom_margin = Inches(0.8)
            section.left_margin = Inches(0.6)
            section.right_margin = Inches(0.6)

        # Title block
        p_title = doc.add_paragraph()
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_title.paragraph_format.space_before = Pt(6)
        p_title.paragraph_format.space_after = Pt(4)
        r_title = p_title.add_run(
            "BANG MA TRAN TRUY XUAT NGUON GOC TAI LIEU\n"
            "(TRACEABILITY MATRIX — 6 COT CHUAN MUC)\n"
            f"De tai: {topic.upper()}"
        )
        self._format_academic_run(r_title, r_title.text, is_bold=True, font_size=13)

        # Skill requirement note
        p_note = doc.add_paragraph()
        p_note.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r_note = p_note.add_run(
            "Luu y: Cot 'Trich Doan Goc' phai copy-paste CHINH XAC tu PDF goc "
            "(khong tom tat, khong sua chua). "
            "PDF goc luu tai: workspace/Tai_Lieu_Goc/[YYYY]_[TacGia]_[TuKhoa].pdf"
        )
        r_note.font.size = Pt(9)
        r_note.font.italic = True

        doc.add_paragraph()

        # Create 6-column table
        table = doc.add_table(rows=1, cols=6)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER

        # Style header row
        hdr_cells = table.rows[0].cells
        for i, header_text in enumerate(MATRIX_HEADERS_6COL):
            hdr_cells[i].text = header_text
            p = hdr_cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                self._format_academic_run(run, run.text, is_bold=True, font_size=9.5)
            shading_elm = parse_xml(r'<w:shd {} w:fill="1F4E79"/>'.format(nsdecls('w')))
            hdr_cells[i]._tc.get_or_add_tcPr().append(shading_elm)
            # White text for dark header
            for run in p.runs:
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

        # Column widths (cm converted to Inches)
        col_widths_inches = [Inches(w / 2.54) for w in MATRIX_COLUMN_WIDTHS_CM]

        # Populate data rows (6-column standard)
        for row_idx, row_data in enumerate(matrix_data, start=1):
            row_cells = table.add_row().cells

            # Col 0: STT (sequential number)
            row_cells[0].text = str(row_idx)

            # Col 1: Du Lieu / So Lieu Trong Bao Cao
            row_cells[1].text = str(row_data.get("claim_in_report", "[Can dien so lieu trich dan trong bao cao]"))

            # Col 2: Tac Gia & Nam (APA 7th)
            author_year = row_data.get("author_year_apa") or row_data.get("author_year", "")
            row_cells[2].text = str(author_year)

            # Col 3: Ten Tep PDF Goc
            pdf_file = row_data.get("original_pdf_file", "[YYYY_TacGia_TuKhoa.pdf]")
            row_cells[3].text = str(pdf_file)

            # Col 4: Trich Doan Goc (Ngon Ngu Goc)
            excerpt = row_data.get("original_excerpt", "[Copy-paste chinh xac tu PDF goc]")
            row_cells[4].text = str(excerpt)

            # Col 5: Ban Dich Tieng Viet + Trang
            translation = row_data.get("vietnamese_translation", "[Dich tieng Viet + ghi so trang chinh xac]")
            row_cells[5].text = str(translation)

            # Format data rows
            shade = "F5F5F5" if row_idx % 2 == 0 else "FFFFFF"
            for col_i, cell in enumerate(row_cells):
                p = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER if col_i == 0 else WD_ALIGN_PARAGRAPH.LEFT
                for run in p.runs:
                    self._format_academic_run(run, run.text, font_size=9)
                shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{shade}"/>')
                cell._tc.get_or_add_tcPr().append(shading_elm)

        # Apply column widths
        for row in table.rows:
            for i, w in enumerate(col_widths_inches):
                if i < len(row.cells):
                    row.cells[i].width = w

        # Footer note
        doc.add_paragraph()
        p_footer = doc.add_paragraph()
        r_footer = p_footer.add_run(
            "Quy tac bat buoc (SKILL_scientific-academic-writing.md v2.0): "
            "Khong duoc de trong bat ky o nao. "
            "Trich doan goc = text chinh xac copy-paste tu PDF, khong sua chua. "
            "Ban dich = dich can than, giu nguyen y nghia, kem so trang chinh xac."
        )
        r_footer.font.size = Pt(8)
        r_footer.font.italic = True

        fpath.parent.mkdir(parents=True, exist_ok=True)
        try:
            doc.save(fpath)
            return fpath
        except PermissionError:
            alt_fpath = fpath.parent / f"{fpath.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{fpath.suffix}"
            doc.save(alt_fpath)
            return alt_fpath

    def save_bytes(self, rel_path: str, data: bytes) -> Dict[str, Any]:
        """Safely saves raw bytes. If target file is locked by MS Word or another process, appends timestamp."""
        clean_rel = rel_path.lstrip("/\\")
        target_path = self.workspace / clean_rel
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        final_path = target_path
        try:
            with open(target_path, "wb") as f:
                f.write(data)
        except PermissionError:
            # File locked by Word/Windows -> write with timestamp suffix
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_path = target_path.parent / f"{target_path.stem}_{timestamp}{target_path.suffix}"
            with open(final_path, "wb") as f:
                f.write(data)
        
        final_rel = str(final_path.relative_to(self.workspace)).replace("\\", "/")
        return {
            "abs_path": str(final_path),
            "rel_path": final_rel,
            "filename": final_path.name,
            "file_url": f"file:///{final_path.as_posix()}"
        }

    def get_custom_storage_dir(self, custom_path: Optional[str] = None) -> Path:
        """Trả về thư mục lưu trữ bài báo do người dùng chỉ định hoặc thư mục cấu hình cá nhân"""
        if custom_path and str(custom_path).strip():
            clean = str(custom_path).strip().replace('"', '').replace("'", "")
            if clean.replace("\\", "/").startswith("workspace/"):
                clean = clean.replace("\\", "/")[len("workspace/"):]
            p = Path(clean)
            if not p.is_absolute():
                p = (self.workspace / clean).resolve()
            p.mkdir(parents=True, exist_ok=True)
            return p

        # Check config.json for global/user custom_storage_dir
        cfg_file = WEB_SUPER_DIR / "config.json"
        if cfg_file.exists():
            try:
                with open(cfg_file, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    c_dir = cfg.get("custom_storage_dir", "").strip()
                    if c_dir:
                        p = Path(c_dir)
                        if not p.is_absolute():
                            p = (self.workspace / c_dir).resolve()
                        p.mkdir(parents=True, exist_ok=True)
                        return p
            except Exception:
                pass

        # Default: workspace/Tai_Lieu
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        return self.docs_dir

    def save_file(self, rel_path, content, file_format="md", topic="", references=None, charts=None, custom_storage_dir=None):
        target_dir = self.get_custom_storage_dir(custom_storage_dir) if custom_storage_dir else None
        
        fpath = (self.workspace / rel_path).resolve()
        fpath.parent.mkdir(parents=True, exist_ok=True)
        ext = fpath.suffix.lower()

        if ext == ".docx" or file_format == "docx":
            if not fpath.name.endswith(".docx"):
                fpath = fpath.with_suffix(".docx")
            title = topic if topic else fpath.stem.replace("_", " ")
            actual_path = self.build_academic_docx(fpath, title, content, references, charts=charts)
            if actual_path:
                fpath = actual_path
        else:
            try:
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(content)
            except PermissionError:
                alt_fpath = fpath.parent / f"{fpath.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{fpath.suffix}"
                with open(alt_fpath, "w", encoding="utf-8") as f:
                    f.write(content)
                fpath = alt_fpath

        # If custom storage directory is specified or configured, also copy/save directly to it
        if target_dir and target_dir != self.docs_dir:
            try:
                custom_fpath = target_dir / fpath.name
                import shutil
                shutil.copy2(fpath, custom_fpath)
            except Exception as e_copy:
                self.add_log("custom_storage_save", f"Cảnh báo sao chép sang {target_dir}: {e_copy}")

        abs_path_str = str(fpath).replace("/", "\\")
        file_url = f"file:///{fpath.as_posix()}"

        return {
            "success": True,
            "rel_path": str(fpath.relative_to(self.workspace)).replace("\\", "/"),
            "abs_path": abs_path_str,
            "file_url": file_url,
            "custom_storage_path": str(target_dir / fpath.name) if (target_dir and target_dir != self.docs_dir) else abs_path_str
        }

    def delete_file(self, rel_path):
        import urllib.parse
        clean = urllib.parse.unquote(str(rel_path).strip())
        if clean.startswith("file:///"):
            clean = clean.replace("file:///", "")
        clean = clean.replace("\\", "/").lstrip("/")
        
        # Remove leading "workspace/" if present to prevent double nesting
        if clean.lower().startswith("workspace/"):
            clean = clean[len("workspace/"):]

        fpath = Path(clean)
        if not (fpath.is_absolute() and fpath.exists()):
            fpath = (self.workspace / clean).resolve()

        ws_str = str(self.workspace.resolve()).lower()
        if not str(fpath).lower().startswith(ws_str):
            raise PermissionError("Truy cập ngoài Workspace bị từ chối.")

        if fpath.exists() and fpath.is_file():
            try:
                fpath.unlink()
                return {"success": True, "message": f"Đã xóa file {clean}"}
            except PermissionError:
                # If file is locked by MS Word or another process, try retry with gc collect
                import time, gc
                gc.collect()
                time.sleep(0.15)
                try:
                    fpath.unlink()
                    return {"success": True, "message": f"Đã xóa file {clean}"}
                except Exception:
                    raise PermissionError(f"Tệp '{fpath.name}' đang được mở bởi Microsoft Word hoặc chương trình khác. Vui lòng đóng tệp trước khi xóa.")
            except Exception as e_del:
                return {"success": False, "message": f"Lỗi khi xóa tệp: {str(e_del)}"}

        # Fallback check in subdirectories (Tai_Lieu, Ban_Thao, Xuat_Ban, Zotero)
        fname = Path(clean).name
        for sub in [self.docs_dir, self.drafts_dir, self.publish_dir, self.zotero_dir]:
            cand = (sub / fname).resolve()
            if cand.exists() and cand.is_file():
                try:
                    cand.unlink()
                    return {"success": True, "message": f"Đã xóa file {clean}"}
                except Exception as e_c:
                    raise PermissionError(f"Không thể xóa tệp '{fname}': {str(e_c)}")

        return {"success": False, "message": f"Không tìm thấy file: {clean}"}

    def delete_files(self, rel_paths: list) -> dict:
        """Xóa hàng loạt tệp tin trong Workspace"""
        deleted = []
        failed = []
        errors = []
        for rel in rel_paths:
            try:
                res = self.delete_file(rel)
                if res.get("success"):
                    deleted.append(rel)
                else:
                    failed.append(rel)
                    errors.append(f"{rel}: {res.get('message')}")
            except Exception as e:
                failed.append(rel)
                errors.append(f"{rel}: {str(e)}")

        is_success = len(deleted) > 0 or len(failed) == 0
        return {
            "success": is_success,
            "deleted_count": len(deleted),
            "deleted_files": deleted,
            "failed_files": failed,
            "detail": "; ".join(errors) if errors else None
        }

    def open_file_in_system(self, rel_path):
        """Mở tệp tin trực tiếp bằng ứng dụng mặc định của hệ điều hành (Microsoft Word)"""
        import os as _os
        import urllib.parse
        import subprocess
        import ctypes

        clean_rel = urllib.parse.unquote(str(rel_path).strip())
        if clean_rel.startswith("file:///"):
            clean_rel = clean_rel.replace("file:///", "")
        clean_rel = clean_rel.replace("\\", "/").lstrip("/")

        fpath = Path(clean_rel)
        if not (fpath.is_absolute() and fpath.exists()):
            fpath = (self.workspace / clean_rel).resolve()

        if not fpath.exists() or not fpath.is_file():
            filename = Path(clean_rel).name
            custom_dir = self.get_custom_storage_dir()
            candidates = [
                (custom_dir / filename).resolve(),
                (self.workspace / "Tai_Lieu" / filename).resolve(),
                (self.drafts_dir / filename).resolve(),
                (self.docs_dir / filename).resolve(),
                (self.publish_dir / filename).resolve(),
                (self.zotero_dir / filename).resolve(),
                (self.workspace / "Tai_Lieu_Goc" / filename).resolve(),
                (self.workspace / "Ghi_Chu_Phan_Tich" / filename).resolve(),
            ]
            for cand in candidates:
                if cand.exists() and cand.is_file():
                    fpath = cand
                    break

        if not fpath.exists() or not fpath.is_file():
            target_name = Path(clean_rel).name.lower()
            for found_file in self.workspace.rglob("*"):
                if found_file.is_file() and found_file.name.lower() == target_name:
                    fpath = found_file.resolve()
                    break

        ws_str = str(self.workspace.resolve()).lower()
        if not str(fpath).lower().startswith(ws_str):
            fpath = (self.workspace / clean_rel).resolve()

        if fpath.exists() and fpath.is_file():
            win_path = str(fpath.resolve()).replace("/", "\\")
            opened = False
            
            # Method 1: Win32 API ShellExecuteW (Forces visible window)
            try:
                ret = ctypes.windll.shell32.ShellExecuteW(None, "open", win_path, None, None, 1)
                if ret > 32:
                    opened = True
            except Exception:
                pass

            # Method 2: os.startfile fallback
            if not opened:
                try:
                    _os.startfile(win_path)
                    opened = True
                except Exception:
                    pass

            # Method 3: cmd start fallback
            if not opened:
                try:
                    subprocess.Popen(f'start "" "{win_path}"', shell=True)
                    opened = True
                except Exception:
                    pass
            
            return {
                "success": True,
                "path": win_path,
                "file_url": f"/api/files/download?path={clean_rel}",
                "message": f"Đã mở tệp '{fpath.name}' trên Microsoft Word thành công."
            }

        return {"success": False, "message": f"Không tìm thấy tệp: {clean_rel}"}

    def open_folder(self, rel_path=None, custom_dir=None):
        """Opens Windows Explorer directly for the target folder or file"""
        import os as _os
        import urllib.parse
        import subprocess
        import ctypes

        target_str = (custom_dir or rel_path or "").strip()
        if target_str:
            clean_rel = urllib.parse.unquote(target_str)
            if clean_rel.startswith("file:///"):
                clean_rel = clean_rel.replace("file:///", "")
            clean_rel = clean_rel.replace("\\", "/").rstrip("/")

            fpath = Path(clean_rel)
            if fpath.is_absolute() and fpath.exists():
                pass
            else:
                fpath = self.get_custom_storage_dir(clean_rel)
        else:
            fpath = self.get_custom_storage_dir()

        if not fpath.exists():
            fpath.mkdir(parents=True, exist_ok=True)

        target_folder = str(fpath.parent if fpath.is_file() else fpath).replace("/", "\\")
        win_path = str(fpath.resolve()).replace("/", "\\")

        # 1. Win32 API ShellExecuteW with 'open' / 'explore'
        try:
            verb = "open" if not fpath.is_file() else "explore"
            ctypes.windll.shell32.ShellExecuteW(None, verb, target_folder, None, None, 1)
        except Exception:
            pass

        # 2. Explorer.exe process
        try:
            if fpath.is_file():
                subprocess.Popen(f'explorer.exe /select,"{win_path}"', shell=True)
            else:
                subprocess.Popen(f'explorer.exe "{target_folder}"', shell=True)
        except Exception:
            pass

        # 3. os.startfile fallback
        try:
            _os.startfile(target_folder)
        except Exception:
            pass

        return {
            "success": True,
            "path": win_path,
            "folder": target_folder,
            "message": f"Đã mở thư mục: {target_folder}"
        }

    def add_log(self, task_name, log_text):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.logs_dir / f"log_{task_name}.txt"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {log_text}\n")
        return str(log_file)

file_mgr = FileManager()
