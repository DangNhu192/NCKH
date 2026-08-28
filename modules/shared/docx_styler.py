# backend/docx_styler.py
"""
Professional Document Styler for WEB SUPER (viet-chuyen-nghiep-v3.1 & Academic Paradigm).
Provides high-fidelity DOCX generation, table styling, callouts, headers/footers,
Word native Heading 1/2/3 styles, scientific chart/diagram embedding,
and in-place docx transformation preserving all images, charts, styles, and tables.
"""

import io
import re
import math
import zipfile
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

COLOR_PRIMARY = RGBColor(30, 58, 138)       # Navy Blue #1E3A8A
COLOR_SECONDARY = RGBColor(37, 99, 235)     # Steel Blue #2563EB
COLOR_DARK = RGBColor(15, 23, 42)           # Dark Slate #0F172A
COLOR_BODY = RGBColor(30, 41, 59)           # Charcoal #1E293B
COLOR_MUTED = RGBColor(100, 116, 139)       # Slate Grey #64748B
HEX_HEADER_BG = "1E3A8A"                    # Navy Blue Hex
HEX_ZEBRA_BG = "F8FAFC"                     # Light Slate Hex
HEX_BORDER = "CBD5E1"                       # Border Hex


def sanitize_and_repair_docx(source: Union[bytes, str, Path]) -> bytes:
    """
    Sửa chữa và chuẩn hóa toàn diện cấu trúc gói OPC ZIP của tệp .docx:
    1. Tự động nhận diện magic bytes của toàn bộ tệp trong `word/media/`
       (JPEG, PNG, GIF, BMP, EMF, WMF, TIFF, SVG) để gán đúng Content-Type.
    2. Sửa lỗi các tệp ảnh bị gán đuôi `.undefined` hoặc không có phần mở rộng.
    3. Đảm bảo [Content_Types].xml có đầy đủ các thẻ <Default> và <Override> hợp lệ.
    4. Cập nhật đường dẫn mục tiêu trong word/_rels/document.xml.rels.
    5. Bỏ qua các mục thư mục rỗng trong ZIP gây lỗi cho OPC unpacker.
    6. Cho phép python-docx và Microsoft Word mở trực tiếp 100% không còn bị KeyError.
    """
    if isinstance(source, (str, Path)):
        p = Path(source)
        with open(p, "rb") as f:
            docx_bytes = f.read()
    else:
        docx_bytes = source

    in_buf = io.BytesIO(docx_bytes)
    out_buf = io.BytesIO()

    try:
        with zipfile.ZipFile(in_buf, "r") as zin, zipfile.ZipFile(out_buf, "w", zipfile.ZIP_DEFLATED) as zout:
            namelist = zin.namelist()

            # 1. Đọc hoặc khởi tạo [Content_Types].xml
            if "[Content_Types].xml" in namelist:
                ct_xml = zin.read("[Content_Types].xml").decode("utf-8", errors="ignore")
            else:
                ct_xml = '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>'

            # 2. Đọc rels nếu có
            rels_xml = ""
            if "word/_rels/document.xml.rels" in namelist:
                rels_xml = zin.read("word/_rels/document.xml.rels").decode("utf-8", errors="ignore")

            # 3. Đảm bảo toàn bộ MIME Types chuẩn cho ảnh và tài liệu
            standard_defaults = {
                "png": "image/png",
                "jpeg": "image/jpeg",
                "jpg": "image/jpeg",
                "gif": "image/gif",
                "bmp": "image/bmp",
                "svg": "image/svg+xml",
                "emf": "image/x-emf",
                "wmf": "image/x-wmf",
                "tiff": "image/tiff",
                "tif": "image/tiff",
                "rels": "application/vnd.openxmlformats-package.relationships+xml",
                "xml": "application/xml",
                "undefined": "image/png"
            }

            for ext, ct in standard_defaults.items():
                if f'Extension="{ext}"' not in ct_xml and f'extension="{ext}"' not in ct_xml:
                    ct_xml = ct_xml.replace("</Types>", f'<Default Extension="{ext}" ContentType="{ct}"/></Types>')

            # 4. Quét toàn bộ tệp trong word/media/
            rename_map = {}
            for name in namelist:
                if name.startswith("word/media/") and not name.endswith("/"):
                    data = zin.read(name)
                    ext = name.split(".")[-1].lower() if "." in name else ""

                    detected_ext = "png"
                    detected_ct = "image/png"
                    if data.startswith(b"\xff\xd8\xff"):
                        detected_ext = "jpeg"
                        detected_ct = "image/jpeg"
                    elif data.startswith(b"\x89PNG\r\n\x1a\n"):
                        detected_ext = "png"
                        detected_ct = "image/png"
                    elif data.startswith(b"GIF8"):
                        detected_ext = "gif"
                        detected_ct = "image/gif"
                    elif data.startswith(b"BM"):
                        detected_ext = "bmp"
                        detected_ct = "image/bmp"
                    elif data.startswith(b"\x01\x00\x00\x00"):
                        detected_ext = "emf"
                        detected_ct = "image/x-emf"
                    elif data.startswith(b"\xd7\xcd\xc6\x9a") or data.startswith(b"\x01\x00\x09\x00"):
                        detected_ext = "wmf"
                        detected_ct = "image/x-wmf"
                    elif data.startswith(b"II*\x00") or data.startswith(b"MM\x00*"):
                        detected_ext = "tiff"
                        detected_ct = "image/tiff"
                    elif b"<svg" in data[:200]:
                        detected_ext = "svg"
                        detected_ct = "image/svg+xml"
                    elif ext in standard_defaults:
                        detected_ext = ext
                        detected_ct = standard_defaults[ext]

                    # Bổ sung Override cho partname hiện tại
                    partname = f"/{name}"
                    if f'PartName="{partname}"' not in ct_xml:
                        ct_xml = ct_xml.replace("</Types>", f'<Override PartName="{partname}" ContentType="{detected_ct}"/></Types>')

                    # Nếu tệp có đuôi .undefined hoặc không có đuôi, đổi tên sang định dạng ảnh chuẩn
                    if ext == "undefined" or not ext:
                        base_no_ext = name.rsplit(".", 1)[0] if "." in name else name
                        new_name = f"{base_no_ext}.{detected_ext}"
                        rename_map[name] = new_name
                        new_partname = f"/{new_name}"
                        if f'PartName="{new_partname}"' not in ct_xml:
                            ct_xml = ct_xml.replace("</Types>", f'<Override PartName="{new_partname}" ContentType="{detected_ct}"/></Types>')

            # Cập nhật rels nếu có đổi tên
            if rels_xml and rename_map:
                for old_name, new_name in rename_map.items():
                    old_target = old_name.replace("word/", "")
                    new_target = new_name.replace("word/", "")
                    rels_xml = rels_xml.replace(f'Target="{old_target}"', f'Target="{new_target}"')

            # 5. Ghi lại các phần tệp sạch vào ZIP đầu ra
            for item in zin.infolist():
                if item.filename.endswith("/"):
                    continue  # Bỏ qua các mục thư mục rỗng
                elif item.filename == "[Content_Types].xml":
                    zout.writestr("[Content_Types].xml", ct_xml.encode("utf-8"))
                elif item.filename == "word/_rels/document.xml.rels" and rels_xml:
                    zout.writestr("word/_rels/document.xml.rels", rels_xml.encode("utf-8"))
                elif item.filename in rename_map:
                    data = zin.read(item.filename)
                    zout.writestr(rename_map[item.filename], data)
                    zout.writestr(item.filename, data)
                else:
                    zout.writestr(item.filename, zin.read(item.filename))

        return out_buf.getvalue()
    except Exception:
        return docx_bytes


def set_cell_background(cell, hex_color: str):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)


def set_table_borders(table, hex_color=HEX_BORDER):
    tblPr = table._tbl.tblPr
    tblBorders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="6" w:space="0" w:color="{hex_color}"/>'
        f'<w:bottom w:val="single" w:sz="8" w:space="0" w:color="{hex_color}"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="{hex_color}"/>'
        f'<w:insideV w:val="none"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(tblBorders)


def sanitize_xml_text(text: str) -> str:
    """Removes XML-incompatible control characters while keeping standard whitespace."""
    if not text:
        return ""
    return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f]', '', str(text))


def replace_text_in_paragraph_runs(paragraph, old_t: str, new_t: str) -> int:
    """
    Replaces occurrences of old_t with new_t in paragraph runs,
    preserving individual run styles (bold, italic, color, font, size).
    Returns the number of occurrences replaced.
    """
    if not old_t or not paragraph.runs:
        return 0

    # 1. Fast path: check if old_t exists inside individual runs
    replaced_count = 0
    found_in_single_run = False
    for r in paragraph.runs:
        if r.text and old_t in r.text:
            count = r.text.count(old_t)
            r.text = r.text.replace(old_t, new_t)
            replaced_count += count
            found_in_single_run = True

    if found_in_single_run:
        return replaced_count

    # 2. Cross-run path: old_t spans across run boundaries
    full_text = "".join(r.text or "" for r in paragraph.runs)
    if old_t not in full_text:
        return 0

    while old_t in full_text:
        run_spans = []
        cur_pos = 0
        for r in paragraph.runs:
            t = r.text or ""
            run_spans.append((cur_pos, cur_pos + len(t), r))
            cur_pos += len(t)

        match_start = full_text.find(old_t)
        match_end = match_start + len(old_t)

        start_run_idx = None
        end_run_idx = None

        for idx, (s, e, r) in enumerate(run_spans):
            if s <= match_start < e or (s == match_start and match_start == cur_pos):
                start_run_idx = idx
            if s < match_end <= e or (e == match_end and match_end == cur_pos):
                end_run_idx = idx

        if start_run_idx is None:
            for idx, (s, e, r) in enumerate(run_spans):
                if s == match_start:
                    start_run_idx = idx
                    break
        if end_run_idx is None:
            for idx, (s, e, r) in reversed(list(enumerate(run_spans))):
                if e >= match_end:
                    end_run_idx = idx
                    break

        if start_run_idx is not None and end_run_idx is not None:
            s_run_start, s_run_end, s_run = run_spans[start_run_idx]
            e_run_start, e_run_end, e_run = run_spans[end_run_idx]

            prefix = s_run.text[:match_start - s_run_start]
            suffix = e_run.text[match_end - e_run_start:]

            if start_run_idx == end_run_idx:
                s_run.text = prefix + new_t + suffix
            else:
                s_run.text = prefix + new_t
                for mid_idx in range(start_run_idx + 1, end_run_idx):
                    run_spans[mid_idx][2].text = ""
                e_run.text = suffix

            replaced_count += 1
            full_text = "".join(r.text or "" for r in paragraph.runs)
        else:
            paragraph.runs[0].text = full_text.replace(old_t, new_t, 1)
            for r in paragraph.runs[1:]:
                r.text = ""
            replaced_count += 1
            full_text = "".join(r.text or "" for r in paragraph.runs)

    return replaced_count


class DocxStyler:

    @classmethod
    def apply_document_styles(cls, doc: Document):
        """Sets standard academic A4 margins: Top 2.5cm, Bottom 2.0cm, Left 3.0cm, Right 2.0cm."""
        for section in doc.sections:
            section.top_margin = Inches(0.98)     # 2.5 cm
            section.bottom_margin = Inches(0.79)  # 2.0 cm
            section.left_margin = Inches(1.18)    # 3.0 cm
            section.right_margin = Inches(0.79)   # 2.0 cm

    @classmethod
    def add_heading_1(cls, doc: Document, text: str):
        """Adds Heading 1 (Times New Roman 14pt Bold Navy Blue)."""
        p = doc.add_paragraph(style='Heading 1')
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.25
        run = p.add_run(sanitize_xml_text(text.upper()))
        run.font.name = "Times New Roman"
        run.font.size = Pt(14)
        run.bold = True
        run.font.color.rgb = COLOR_PRIMARY
        return p

    @classmethod
    def add_heading_2(cls, doc: Document, text: str):
        """Adds Heading 2 (Times New Roman 13.5pt Bold Steel Blue)."""
        p = doc.add_paragraph(style='Heading 2')
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.25
        run = p.add_run(sanitize_xml_text(text))
        run.font.name = "Times New Roman"
        run.font.size = Pt(13.5)
        run.bold = True
        run.font.color.rgb = COLOR_SECONDARY
        return p

    @classmethod
    def add_heading_3(cls, doc: Document, text: str):
        """Adds Heading 3 (Times New Roman 12.5pt Bold Italic Dark Slate)."""
        p = doc.add_paragraph(style='Heading 3')
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.25
        run = p.add_run(sanitize_xml_text(text))
        run.font.name = "Times New Roman"
        run.font.size = Pt(12.5)
        run.bold = True
        run.font.italic = True
        run.font.color.rgb = COLOR_DARK
        return p

    @classmethod
    def add_paragraph(cls, doc: Document, text: str):
        """Adds standard justified paragraph with Vietnamese decimal and subscript formatting."""
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.25
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(5)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.first_line_indent = Inches(0.3)
        cls.apply_vietnamese_decimal_and_subscripts(p, text, font_size=13)
        return p

    @classmethod
    def add_styled_table(cls, doc: Document, headers: List[str], data: List[List[str]]):
        """Adds a standardized academic grid table with Navy Blue headers and auto-fitted columns."""
        table_lines = ["| " + " | ".join(str(h) for h in headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
        for row in data:
            table_lines.append("| " + " | ".join(str(c) for c in row) + " |")
        cls._render_styled_table(doc, table_lines)

    @classmethod
    def clean_inline_latex_math(cls, text: str) -> str:
        """Loại bỏ hoàn toàn các dấu $ của LaTeX và chuyển đổi ký hiệu toán/hóa học sang Unicode chuẩn."""
        if not text:
            return ""
        
        # 1. Chuyển đổi các ký hiệu toán Hy Lạp và phép toán thông dụng
        math_map = {
            r"\alpha": "α", r"\beta": "β", r"\gamma": "γ", r"\delta": "δ",
            r"\epsilon": "ε", r"\theta": "θ", r"\lambda": "λ", r"\mu": "μ",
            r"\pi": "π", r"\rho": "ρ", r"\sigma": "σ", r"\tau": "τ",
            r"\omega": "ω", r"\Delta": "Δ", r"\Sigma": "Σ", r"\Omega": "Ω",
            r"\pm": "±", r"\approx": "≈", r"\leq": "≤", r"\le": "≤",
            r"\geq": "≥", r"\ge": "≥", r"\neq": "≠", r"\times": "×",
            r"\cdot": "·", r"\div": "÷", r"\infty": "∞", r"\rightarrow": "→",
            r"\leftarrow": "←", r"\leftrightarrow": "↔", r"\Rightarrow": "⇒",
            r"\in": "∈", r"\forall": "∀", r"\exists": "∃", r"\subset": "⊂",
            r"\cup": "∪", r"\cap": "∩", r"\partial": "∂", r"\nabla": "∇",
            r"\sum": "∑", r"\prod": "∏", r"\int": "∫"
        }
        
        res = text
        for sym_latex, sym_uni in math_map.items():
            res = res.replace(sym_latex, sym_uni)

        # 2. Xử lý căn bậc hai và phân số
        res = re.sub(r'\\sqrt\{([^}]+)\}', r'√(\1)', res)
        res = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1/\2)', res)
        res = re.sub(r'\\(?:text|mathrm|mathbf)\{([^}]+)\}', r'\1', res)

        # 3. Chuyển đổi chỉ số trên và dưới
        sub_map = str.maketrans("0123456789+-=()aijklmnoprstuvx", "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓ")
        sup_map = str.maketrans("0123456789+-=()abdegijklmnoprstuvwxyz", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ᵃᵇᵈᵉᵍⁱʲᵏˡᵐⁿᵒᵖʳˢᵗᵘᵛʷˣʸᶻ")
        
        res = re.sub(r'_\{([0-9+\-=()a-zA-Z]+)\}', lambda m: m.group(1).translate(sub_map), res)
        res = re.sub(r'_([0-9+\-=()a-zA-Z])', lambda m: m.group(1).translate(sub_map), res)
        res = re.sub(r'\^\{([0-9+\-=()a-zA-Z]+)\}', lambda m: m.group(1).translate(sup_map), res)
        res = re.sub(r'\^([0-9+\-=()a-zA-Z])', lambda m: m.group(1).translate(sup_map), res)

        # 4. Loại bỏ các cặp dấu $ ... $ hoặc $$ ... $$ trong câu văn xuôi
        res = re.sub(r'\$\$([^\$]+)\$\$', r'\1', res)
        res = re.sub(r'\$([^\$]+)\$', r'\1', res)
        res = re.sub(r'(?<!\d)\$(?!\d)', '', res)

        # 5. Áp dụng bảng ánh xạ hóa học Unicode
        from modules.shared.docx_formula_engine import UNICODE_CHEM_MAP
        for k, v in sorted(UNICODE_CHEM_MAP.items(), key=lambda x: len(x[0]), reverse=True):
            if k in res:
                res = res.replace(k, v)

        return res


    """High-fidelity styler conforming to viet-chuyen-nghiep-v3.1."""

    @staticmethod
    def convert_decimals_preserve_sections(text: str) -> str:
        """Converts standalone decimal numbers to Vietnamese comma (15,5%) and thousands to dot (1.000) while strictly preserving:
        - Section numbers (1.1, 1.2., 2.3.4, etc.)
        - Software/model versions (v3.1, Gemini 1.5, Python 3.11)
        - DOIs, URLs, file extensions, emails
        - Standards, timestamps, citations
        """
        if not text:
            return ""

        protected = []
        def save_token(m):
            idx = len(protected)
            val = m.group(0) if hasattr(m, "group") else str(m)
            protected.append(val)
            return f"__SAFE_TOK_{idx}__"

        protect_patterns = [
            r'https?://[^\s<>"]+',
            r'doi(?:\.org|:)\s*/?[^\s<>"\)]+',
            r'10\.\d{4,9}/[^\s<>"\)]+',
            r'[\w\.\-]+\.(?:docx|pdf|ris|py|json|html|xml|txt|png|jpg|jpeg|csv|xlsx|zip|tar|gz)',
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            r'\bv\d+(?:\.\d+)*(?:-[a-zA-Z0-9]+)?\b',
            r'\b(?:Gemini|Python|GPT|Word|Office|Claude|Llama|YOLO|ResNet|BERT|GPT-4|Windows|Ubuntu|CUDA)\s+v?\d+(?:\.\d+)*\b',
            r'(?:Mục|Muc|Điều|Dieu|Chương|Chuong|Phần|Phan|Bảng|Bang|Hình|Hinh|Sơ đồ|So do|Biểu đồ|Bieu do|Mẫu|Mau|Section|Table|Figure|Eq\.|Equation)\s+\d+(?:\.\d+)*',
            r'\(\s*(?:Mục|Muc|Điều|Dieu|Chương|Chuong|Bảng|Bang|Hình|Hinh|Section|Table|Figure)?\s*\d+(?:\.\d+)+\s*\)',
            r'\b\d+(?:\.\d+){2,}\.?\b',
            r'(?:QCVN|TCVN|ISO|ASTM|IEEE)\s+[\w\d:/\.-]+',
            r'\b[a-zA-Z_][\w]*=\d+(?:\.\d+)+\b',
            r'\b[1-9]\d{0,2}(?:\.\d{3})+(?=[^\d\.,%]|$)',
        ]
        
        combined_protect = re.compile('|'.join(f'({p})' for p in protect_patterns), re.IGNORECASE | re.MULTILINE)
        safe_text = combined_protect.sub(save_token, text)

        # 1. Convert English numbers with thousand commas AND decimal point (e.g. 1,234,567.89 -> 1.234.567,89)
        def repl_en_thousands_decimal(m):
            th_part = m.group(1).replace(',', '.')
            dec_part = m.group(2)
            return save_token(f"{th_part},{dec_part}")

        safe_text = re.sub(r'\b(\d{1,3}(?:,\d{3})+)\.(\d+)\b', repl_en_thousands_decimal, safe_text)

        # 2. Convert English thousand commas without decimals (e.g. 500,000 -> 500.000, 12,500,000,000 -> 12.500.000.000)
        def repl_en_thousands_only(m):
            th_part = m.group(0).replace(',', '.')
            return save_token(th_part)

        safe_text = re.sub(r'\b\d{1,3}(?:,\d{3})+\b', repl_en_thousands_only, safe_text)

        # 3. Protect existing thousands numbers with dot
        safe_text = re.sub(r'\b[1-9]\d{0,2}(?:\.\d{3})+(?=[^\d\.,%]|$)', save_token, safe_text)

        # 4. Convert all remaining decimal numbers (\d+\.\d+) to Vietnamese comma (\1,\2)
        safe_text = re.sub(r'(\d+)\.(\d+)', r'\1,\2', safe_text)

        # 5. Restore protected tokens
        for idx, token in enumerate(protected):
            safe_text = safe_text.replace(f"__SAFE_TOK_{idx}__", token)

        return safe_text

    @classmethod
    def convert_document_decimals(cls, doc) -> int:
        """Converts decimals to Vietnamese commas across all paragraphs and tables in a docx Document in-place."""
        count = 0
        def _process_paragraph(p):
            nonlocal count
            orig_text = p.text
            if not orig_text or not re.search(r'\d+\.\d+|\d{1,3}(?:,\d{3})+', orig_text):
                return
            new_text = cls.convert_decimals_preserve_sections(orig_text)
            if new_text != orig_text:
                if len(p.runs) == 1:
                    p.runs[0].text = new_text
                    count += 1
                elif len(p.runs) == 0:
                    p.text = new_text
                    count += 1
                else:
                    changed_any = False
                    for r in p.runs:
                        if r.text and re.search(r'\d+\.\d+|\d{1,3}(?:,\d{3})+', r.text):
                            r_new = cls.convert_decimals_preserve_sections(r.text)
                            if r_new != r.text:
                                r.text = r_new
                                changed_any = True
                    if changed_any:
                        count += 1
                    elif p.text != new_text:
                        for r in p.runs[1:]:
                            r.text = ""
                        p.runs[0].text = new_text
                        count += 1

        for p in doc.paragraphs:
            _process_paragraph(p)
        for tbl in doc.tables:
            for row in tbl.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        _process_paragraph(p)
        return count

    @classmethod
    def apply_vietnamese_decimal_and_subscripts(cls, paragraph, raw_text: str, is_bold=False, is_italic=False, font_size=13, font_color=COLOR_BODY):
        converted_body = cls.convert_decimals_preserve_sections(raw_text)
        final_text = cls.clean_inline_latex_math(converted_body)

        # Parse inline bold, italic, subscripts
        tokens = re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*|_[^_]+_|`[^`]+`)', final_text)
        for token in tokens:
            if not token:
                continue
            run = paragraph.add_run()
            run.font.name = "Times New Roman"
            run.font.size = Pt(font_size)
            run.font.color.rgb = font_color

            if token.startswith("**") and token.endswith("**"):
                run.text = sanitize_xml_text(token[2:-2])
                run.bold = True
            elif (token.startswith("*") and token.endswith("*")) or (token.startswith("_") and token.endswith("_")):
                run.text = sanitize_xml_text(token[1:-1])
                run.italic = True
            elif token.startswith("`") and token.endswith("`"):
                run.text = sanitize_xml_text(token[1:-1])
                run.font.name = "Consolas"
                run.font.size = Pt(font_size - 1)
                run.font.color.rgb = RGBColor(220, 38, 38)
            else:
                run.text = sanitize_xml_text(token)
                run.bold = is_bold
                run.italic = is_italic

    @classmethod
    def insert_chart_with_caption(cls, doc: Document, chart_data: Dict[str, Any], width_inches: float = 5.6):
        """Embeds high-resolution chart/diagram image and adds standardized academic caption and spacing"""
        img_source = chart_data.get("bytes") or chart_data.get("file_path") or chart_data.get("path")
        if not img_source:
            return

        # Intelligently resolve file path if it's a string
        if isinstance(img_source, str):
            p_cand = Path(img_source)
            if not p_cand.is_absolute() or not p_cand.exists():
                from modules.shared.file_manager import file_mgr
                search_dirs = [
                    file_mgr.workspace / "charts",
                    file_mgr.workspace / "Tai_Lieu",
                    file_mgr.workspace,
                    Path("workspace/charts"),
                    Path("workspace/Tai_Lieu"),
                    Path("workspace"),
                    Path(".")
                ]
                for s_dir in search_dirs:
                    cand = (s_dir / p_cand.name).resolve()
                    if cand.exists() and cand.is_file():
                        img_source = str(cand)
                        break
                    cand_full = (s_dir / img_source).resolve()
                    if cand_full.exists() and cand_full.is_file():
                        img_source = str(cand_full)
                        break

        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(12)
        p_img.paragraph_format.space_after = Pt(4)

        img_loaded = False
        try:
            from PIL import Image
            img_bytes = None
            if isinstance(img_source, bytes):
                img_bytes = img_source
            elif isinstance(img_source, (str, Path)) and Path(img_source).exists():
                img_bytes = Path(img_source).read_bytes()

            if img_bytes:
                with Image.open(io.BytesIO(img_bytes)) as pil_img:
                    # Convert palette or RGBA to RGB for clean Word OpenXML compatibility
                    if pil_img.mode in ("RGBA", "P", "LA"):
                        rgb_img = Image.new("RGB", pil_img.size, (255, 255, 255))
                        if pil_img.mode == "P":
                            pil_img = pil_img.convert("RGBA")
                        rgb_img.paste(pil_img, mask=pil_img.split()[-1] if pil_img.mode == "RGBA" else None)
                        out_io = io.BytesIO()
                        rgb_img.save(out_io, format="JPEG", quality=95, dpi=(300, 300))
                        out_io.seek(0)
                        p_img.add_run().add_picture(out_io, width=Inches(width_inches))
                        img_loaded = True
                    else:
                        out_io = io.BytesIO()
                        pil_img.save(out_io, format="JPEG" if pil_img.format != "PNG" else "PNG", quality=95, dpi=(300, 300))
                        out_io.seek(0)
                        p_img.add_run().add_picture(out_io, width=Inches(width_inches))
                        img_loaded = True
            elif isinstance(img_source, (str, Path)) and Path(img_source).exists():
                p_img.add_run().add_picture(str(img_source), width=Inches(width_inches))
                img_loaded = True
        except Exception:
            try:
                if isinstance(img_source, bytes):
                    stream = io.BytesIO(img_source)
                    p_img.add_run().add_picture(stream, width=Inches(width_inches))
                    img_loaded = True
                elif isinstance(img_source, (str, Path)) and Path(img_source).exists():
                    p_img.add_run().add_picture(str(img_source), width=Inches(width_inches))
                    img_loaded = True
            except Exception:
                pass

        if not img_loaded:
            p_err = p_img.add_run(f"[{chart_data.get('caption', 'Hình ảnh/Biểu đồ tài liệu')}]")
            p_err.font.italic = True
            p_err.font.color.rgb = COLOR_MUTED
            return

        # Add caption paragraph (Centered, Bold Title, Italic description)
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(12)

        caption_text = chart_data.get("caption") or chart_data.get("title") or "Hình ảnh / Sơ đồ nguyên bản từ tài liệu gốc"
        run_cap = p_cap.add_run(caption_text)
        run_cap.font.name = "Times New Roman"
        run_cap.font.size = Pt(10.5)
        run_cap.font.bold = True
        run_cap.font.italic = True
        run_cap.font.color.rgb = COLOR_DARK

    @classmethod
    def render_markdown_to_docx(cls, doc: Document, markdown_text: str, title: str = None, charts: List[Dict[str, Any]] = None):
        """Standard entry point for rendering full markdown text into a styled docx document."""
        if title and not markdown_text.strip().startswith("# "):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(16)
            p.paragraph_format.space_after = Pt(12)
            p.paragraph_format.line_spacing = 1.3
            run = p.add_run(title.upper())
            run.font.name = "Times New Roman"
            run.font.size = Pt(16)
            run.bold = True
            run.font.color.rgb = COLOR_PRIMARY
        return cls.render_markdown_body(doc, markdown_text, charts=charts)

    @classmethod
    def clean_and_stitch_markdown(cls, text: str) -> List[str]:
        """
        Stitches hard-wrapped lines from PDF/HTML extraction into unified paragraphs,
        preserving headings, tables, block math, lists, callouts, and chart/image tags.
        Intelligently splits monolithic text blocks into well-proportioned academic paragraphs.
        """
        if not text:
            return []
        
        # 1. Pre-process structured abstract tags (Background:, Methods:, Results:, Conclusion:)
        pattern_sec = r'(\b(?:Background|Objectives?|Aims?|Methods?|Methodology|Materials and Methods|Results|Findings|Discussion|Conclusions?|Significance|Keywords?|Đặt vấn đề|Mục tiêu|Đối tượng và phương pháp|Phương pháp|Kết quả|Bàn luận|Kết luận|Từ khóa)\s*[:：])'
        text = re.sub(pattern_sec, r'\n\n**\1** ', text, flags=re.I)

        raw_lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        structured_items = []
        cur_para = []

        def flush_cur_para():
            if cur_para:
                joined = []
                for segment in cur_para:
                    seg = segment.strip()
                    if not seg:
                        continue
                    if joined and joined[-1].endswith("-"):
                        joined[-1] = joined[-1][:-1] + seg
                    else:
                        joined.append(seg)
                if joined:
                    full_p = " ".join(joined).strip()
                    # If this paragraph is excessively long and not a heading/list/table, split into coherent 2-4 sentence academic paragraphs
                    if len(full_p) > 500 and not full_p.startswith(('|', '#', '-', '*', '>', '`', '[', '![')):
                        sentences = re.split(r'(?<=[.!?])\s+(?=[A-ZÀ-Ỹ0-9])', full_p)
                        chunk = []
                        chunk_len = 0
                        for s in sentences:
                            chunk.append(s)
                            chunk_len += len(s)
                            if chunk_len >= 320 and len(chunk) >= 2:
                                structured_items.append(" ".join(chunk))
                                chunk = []
                                chunk_len = 0
                        if chunk:
                            structured_items.append(" ".join(chunk))
                    else:
                        structured_items.append(full_p)
                cur_para.clear()

        for line in raw_lines:
            trimmed = line.strip()

            if not trimmed:
                flush_cur_para()
                continue

            if trimmed.startswith("$$") or trimmed.startswith("```") or (trimmed.startswith("|") and trimmed.endswith("|")):
                flush_cur_para()
                structured_items.append(trimmed)
                continue

            # Structural elements: headings, quotes, charts, markdown images (![...](...)), horizontal rules
            if re.match(r'^(?:#+|\d+\.\d+\.?\s+[A-ZÀ-ỹ]|>|\[CHART|!\[|\*\*\*|---)', trimmed):
                flush_cur_para()
                structured_items.append(trimmed)
                continue

            # Start of a new list item (bullet or numbered)
            if re.match(r'^(?:[-*•]|\d+\.)\s+', trimmed):
                flush_cur_para()
                cur_para.append(trimmed)
                continue

            cur_para.append(trimmed)

        flush_cur_para()
        return structured_items

    @classmethod
    def render_markdown_body(cls, doc: Document, markdown_text: str, charts: List[Dict[str, Any]] = None):
        lines = cls.clean_and_stitch_markdown(markdown_text)
        i = 0
        in_references = False
        chart_idx = 0
        total_charts = len(charts) if charts else 0
        rendered_images = set()

        while i < len(lines):
            line = lines[i]
            trimmed = line.strip()

            if not trimmed:
                i += 1
                continue

            # Check for Markdown Image Tag: ![Caption](path/url)
            match_md_img = re.match(r'^!\[(.*?)\]\((.*?)\)$', trimmed)
            if match_md_img:
                img_caption = match_md_img.group(1).strip()
                img_ref = match_md_img.group(2).strip()
                cls.insert_chart_with_caption(doc, {
                    "file_path": img_ref,
                    "caption": img_caption or "Hình ảnh / Sơ đồ nguyên bản từ tài liệu gốc"
                })
                rendered_images.add(img_ref)
                i += 1
                continue

            # Check for explicit chart tag: [CHART] or [CHART: ...]
            if trimmed.startswith("[CHART") and charts and chart_idx < total_charts:
                cls.insert_chart_with_caption(doc, charts[chart_idx])
                chart_idx += 1
                i += 1
                continue

            # Check Equation Block ($$...$$)
            if trimmed.startswith("$$") and trimmed.endswith("$$") and len(trimmed) > 4:
                latex_code = trimmed[2:-2].strip()
                p_eq = doc.add_paragraph()
                p_eq.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_eq.paragraph_format.space_before = Pt(6)
                p_eq.paragraph_format.space_after = Pt(6)
                try:
                    from modules.shared.docx_formula_engine import add_latex_equation
                    add_latex_equation(p_eq, latex_code)
                except Exception:
                    run = p_eq.add_run(latex_code)
                    run.font.name = "Times New Roman"
                    run.font.size = Pt(11)
                    run.italic = True
                i += 1
                continue

            # Check Table
            if trimmed.startswith("|") and trimmed.endswith("|"):
                table_lines = []
                while i < len(lines) and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                    table_lines.append(lines[i].strip())
                    i += 1
                cls._render_styled_table(doc, table_lines)
                continue

            # Check Title (# Title)
            if trimmed.startswith("# ") and not trimmed.startswith("## "):
                title_text = re.sub(r'^#\s*', '', trimmed).replace("**", "").replace("__", "").strip()
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(16)
                p.paragraph_format.space_after = Pt(12)
                p.paragraph_format.line_spacing = 1.3
                run = p.add_run(sanitize_xml_text(title_text.upper()))
                run.font.name = "Times New Roman"
                run.font.size = Pt(16)
                run.bold = True
                run.font.color.rgb = COLOR_PRIMARY
                i += 1
                continue

            # Heading Level 1 (Major Sections: CHƯƠNG, PHẦN, 1. MỞ ĐẦU, TÀI LIỆU THAM KHẢO, etc.)
            is_h1 = (
                trimmed.startswith("# ") or
                (trimmed.startswith("## ") and any(kw in trimmed.upper() for kw in ["PHẦN", "PHAN", "CHƯƠNG", "CHUONG", "TÀI LIỆU THAM KHẢO", "REFERENCES", "TÓM TẮT", "TOM TAT", "DANH MỤC", "DANH MUC", "KẾT LUẬN", "KET LUAN"])) or
                bool(re.match(r'^##\s*\d+\.\s+[A-ZÀ-ỹ]', trimmed)) or
                bool(re.match(r'^\d+\.\s+[A-ZÀ-ỹ\s]{4,}', trimmed))
            )
            if is_h1:
                h_text = re.sub(r'^#+\s*', '', trimmed).replace("**", "").replace("__", "").strip()
                if any(kw in h_text.upper() for kw in ["TÀI LIỆU THAM KHẢO", "REFERENCES"]):
                    in_references = True
                try:
                    p = doc.add_paragraph(style='Heading 1')
                except Exception:
                    p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(16)
                p.paragraph_format.space_after = Pt(6)
                p.paragraph_format.line_spacing = 1.25
                run = p.add_run(sanitize_xml_text(h_text.upper()))
                run.font.name = "Times New Roman"
                run.font.size = Pt(14)
                run.bold = True
                run.font.color.rgb = COLOR_PRIMARY

                # If this is Section 3 or Section 4 (Results/Discussion) and we have charts, embed chart after section header
                if charts and chart_idx < total_charts and any(kw in h_text.upper() for kw in ["KẾT QUẢ", "THỰC NGHIỆM", "PHÂN TÍCH", "THẢO LUẬN"]):
                    # Will embed naturally or at end of subsection
                    pass

                i += 1
                continue

            # Heading Level 2 (Subsections: ## general, ### 1.1, ### 1.2, 2.1, etc.)
            is_h2 = (
                (trimmed.startswith("## ") and not any(kw in trimmed.upper() for kw in ["PHẦN", "PHAN", "CHƯƠNG", "CHUONG", "TÀI LIỆU THAM KHẢO", "REFERENCES", "TÓM TẮT", "TOM TAT", "DANH MỤC", "DANH MUC", "KẾT LUẬN", "KET LUAN"])) or
                (trimmed.startswith("### ") and not bool(re.search(r'\d+\.\d+\.\d+', trimmed))) or
                (bool(re.match(r'^#+\s*[*_]*\d+\.\d+ ', trimmed)) and not bool(re.search(r'\d+\.\d+\.\d+', trimmed)))
            )
            if is_h2:
                h_text = re.sub(r'^#+\s*', '', trimmed).replace("**", "").replace("__", "").strip()
                try:
                    p = doc.add_paragraph(style='Heading 2')
                except Exception:
                    p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(12)
                p.paragraph_format.space_after = Pt(4)
                p.paragraph_format.line_spacing = 1.25
                run = p.add_run(sanitize_xml_text(h_text))
                run.font.name = "Times New Roman"
                run.font.size = Pt(13.5)
                run.bold = True
                run.font.color.rgb = COLOR_SECONDARY
                i += 1
                continue

            # Heading Level 3 (Sub-subsections: #### general, ### 1.1.1, 1.2.1, etc.)
            is_h3 = (
                trimmed.startswith("#### ") or
                bool(re.search(r'\d+\.\d+\.\d+', trimmed)) or
                trimmed.startswith("### ")
            )
            if is_h3:
                h_text = re.sub(r'^#+\s*', '', trimmed).replace("**", "").replace("__", "").strip()
                try:
                    p = doc.add_paragraph(style='Heading 3')
                except Exception:
                    p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(10)
                p.paragraph_format.space_after = Pt(3)
                p.paragraph_format.line_spacing = 1.25
                run = p.add_run(sanitize_xml_text(h_text))
                run.font.name = "Times New Roman"
                run.font.size = Pt(12.5)
                run.bold = True
                run.italic = True
                run.font.color.rgb = COLOR_DARK
                i += 1
                continue

            # Callout quote
            if trimmed.startswith(">"):
                quote_text = re.sub(r'^>\s*', '', trimmed)
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(8)
                p.paragraph_format.space_after = Pt(8)
                p.paragraph_format.left_indent = Inches(0.4)
                p.paragraph_format.right_indent = Inches(0.4)
                p.paragraph_format.line_spacing = 1.2
                run = p.add_run(sanitize_xml_text(f"“ {quote_text} ”"))
                run.font.name = "Times New Roman"
                run.font.size = Pt(11.5)
                run.italic = True
                run.font.color.rgb = COLOR_SECONDARY
                i += 1
                continue

            # Bullet list
            if re.match(r'^[\*\-\•]\s+', trimmed):
                bullet_text = re.sub(r'^[\*\-\•]\s+', '', trimmed)
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.3)
                p.paragraph_format.first_line_indent = Inches(-0.15)
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.line_spacing = 1.25
                run_bullet = p.add_run("● ")
                run_bullet.font.name = "Times New Roman"
                run_bullet.font.size = Pt(8)
                run_bullet.font.color.rgb = COLOR_SECONDARY
                cls.apply_vietnamese_decimal_and_subscripts(p, bullet_text, font_size=13)
                i += 1
                continue

            # Numbered list
            match_num = re.match(r'^(\d+[\.\)])\s+(.*)', trimmed)
            if match_num and len(trimmed) > 5 and not trimmed.startswith("10.") and not re.match(r'^\d+\.\d+', trimmed):
                num_prefix = match_num.group(1)
                item_text = match_num.group(2)
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.35)
                p.paragraph_format.first_line_indent = Inches(-0.2)
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.line_spacing = 1.25
                run_num = p.add_run(f"{num_prefix} ")
                run_num.font.name = "Times New Roman"
                run_num.font.size = Pt(13)
                run_num.bold = True
                run_num.font.color.rgb = COLOR_PRIMARY
                cls.apply_vietnamese_decimal_and_subscripts(p, item_text, font_size=13)
                i += 1
                continue

            # Paragraph or Reference
            p = doc.add_paragraph()
            p.paragraph_format.line_spacing = 1.25
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(5)

            is_metadata = bool(re.match(r'^\*\*(?:Authors?|Tác giả|Publication|Năm|Journal|Publisher|Tạp chí|DOI|Zotero|Source|PDF Document)\b', trimmed, re.I))

            if in_references or (trimmed.startswith("(") and ("http" in trimmed or "doi" in trimmed)):
                p.paragraph_format.first_line_indent = Inches(-0.4)
                p.paragraph_format.left_indent = Inches(0.4)
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                clean_ref = re.sub(r'^[\*\-\•\d+\.]\s*', '', trimmed)
                cls.apply_vietnamese_decimal_and_subscripts(p, clean_ref, font_size=12.5)
            elif is_metadata:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p.paragraph_format.space_before = Pt(1)
                p.paragraph_format.space_after = Pt(2)
                cls.apply_vietnamese_decimal_and_subscripts(p, trimmed, font_size=12)
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p.paragraph_format.first_line_indent = Inches(0.3)  # Chuẩn thụt đầu dòng học thuật
                cls.apply_vietnamese_decimal_and_subscripts(p, trimmed, font_size=13)

            # If this paragraph mentions Results or Data and we haven't embedded chart 1, embed it
            if charts and chart_idx < total_charts and ("kết quả" in trimmed.lower() or "thực nghiệm" in trimmed.lower()) and len(trimmed) > 80:
                cls.insert_chart_with_caption(doc, charts[chart_idx])
                chart_idx += 1

            i += 1

        # If any charts remaining, insert before References or at end
        while charts and chart_idx < total_charts:
            cls.insert_chart_with_caption(doc, charts[chart_idx])
            chart_idx += 1

        # Post-process inline chemical formulas safely
        try:
            from modules.shared.docx_formula_engine import format_inline_chemical_formulas
            for p_item in doc.paragraphs:
                format_inline_chemical_formulas(p_item)
        except Exception:
            pass

    @classmethod
    def _render_styled_table(cls, doc: Document, table_lines: List[str]):
        if len(table_lines) < 2:
            return

        parsed_rows = []
        for line in table_lines:
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if cells and all(re.match(r'^:?-+:?$', c) for c in cells):
                continue
            if cells:
                parsed_rows.append(cells)

        if not parsed_rows:
            return

        cols_count = max(len(r) for r in parsed_rows)
        table = doc.add_table(rows=len(parsed_rows), cols=cols_count)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(table, HEX_BORDER)

        for r_idx, row_data in enumerate(parsed_rows):
            row = table.rows[r_idx]
            is_header = (r_idx == 0)

            for c_idx in range(cols_count):
                cell = row.cells[c_idx]
                cell_text = row_data[c_idx] if c_idx < len(row_data) else ""
                cell.text = ""
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                set_cell_margins(cell, top=100, bottom=100, left=140, right=140)

                p = cell.paragraphs[0]
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.line_spacing = 1.15

                if is_header:
                    set_cell_background(cell, HEX_HEADER_BG)
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    run = p.add_run(cell_text)
                    run.font.name = "Times New Roman"
                    run.font.size = Pt(11)
                    run.bold = True
                    run.font.color.rgb = RGBColor(255, 255, 255)
                else:
                    if r_idx % 2 == 1:
                        set_cell_background(cell, HEX_ZEBRA_BG)
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    cls.apply_vietnamese_decimal_and_subscripts(p, cell_text, font_size=11)

        # Auto-compute column widths based on maximum content length
        max_lens = [max(len(str(r[c])) if c < len(r) else 1 for r in parsed_rows) for c in range(cols_count)]
        total_len = sum(max_lens) or cols_count
        table_width_inches = 6.2  # Full body width on A4 page
        col_widths = [max(0.6, (ml / total_len) * table_width_inches) for ml in max_lens]
        # Normalize sum
        scale = table_width_inches / sum(col_widths)
        col_widths = [Inches(cw * scale) for cw in col_widths]

        for row in table.rows:
            for c_idx, w in enumerate(col_widths):
                if c_idx < len(row.cells):
                    row.cells[c_idx].width = w

        p_after = doc.add_paragraph()
        p_after.paragraph_format.space_before = Pt(4)
        p_after.paragraph_format.space_after = Pt(4)

    @classmethod
    def update_docx_content_preserving_styles(cls, input_bytes: bytes, replacements: Dict[str, str] = None) -> bytes:
        """
        Updates text content in a DOCX file while strictly preserving:
        - Exact paragraph font, size, line spacing, margins, alignments
        - Run styles (Bold, Italic, Color, Underline)
        - Table layouts, cell borders, shading
        - Images, charts, and drawings
        """
        doc = Document(io.BytesIO(input_bytes))
        if not replacements:
            return input_bytes

        for p in doc.paragraphs:
            for old_t, new_t in replacements.items():
                replace_text_in_paragraph_runs(p, old_t, new_t)

        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        for old_t, new_t in replacements.items():
                            replace_text_in_paragraph_runs(p, old_t, new_t)

        out_stream = io.BytesIO()
        doc.save(out_stream)
        out_stream.seek(0)
        return out_stream.getvalue()

    @classmethod
    def humanize_docx_document_inplace(cls, input_bytes: bytes, cliches_list: list) -> bytes:
        doc = Document(io.BytesIO(input_bytes))

        def clean_run_text(text: str) -> str:
            if not text:
                return text
            res = text
            for cliche, suggestion in cliches_list:
                if not suggestion:
                    pattern = re.compile(r'\b' + re.escape(cliche) + r'[,\.]?\s*', re.IGNORECASE)
                    res = pattern.sub("", res)
                else:
                    first_alt = suggestion.split("/")[0].strip()
                    def repl(m, alt=first_alt):
                        matched = m.group(0)
                        if matched and matched[0].isupper():
                            return alt.capitalize()
                        return alt.lower()
                    pattern = re.compile(r'\b' + re.escape(cliche) + r'\b', re.IGNORECASE)
                    res = pattern.sub(repl, res)
            res = res.replace("—", ", ").replace("--", ", ")
            res = cls.convert_decimals_preserve_sections(res)
            return res

        for p in doc.paragraphs:
            for run in p.runs:
                if run.text:
                    run.text = clean_run_text(run.text)

        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        for run in p.runs:
                            if run.text:
                                run.text = clean_run_text(run.text)

        out_stream = io.BytesIO()
        doc.save(out_stream)
        out_stream.seek(0)
        return out_stream.getvalue()
