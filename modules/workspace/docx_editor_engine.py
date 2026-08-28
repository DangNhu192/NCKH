# modules/workspace/docx_editor_engine.py
"""
DOCX Content & Data Editor Engine for WEB SUPER v3.2 / v2.0
Enables:
1. Parsing uploaded .docx files into structured sections, paragraphs, tables, and extracted numerical data points.
2. In-place editing of text and table cells.
3. Batch search and replace of metrics/terms across the Word document.
4. Saving back to .docx with 100% In-Place DOM preservation (Times New Roman 14pt, 1.5 spacing, Vietnamese decimals, Chemical subscripts).
"""

import io
import re
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

from modules.shared.file_manager import file_mgr
from modules.shared.docx_styler import DocxStyler, replace_text_in_paragraph_runs, sanitize_and_repair_docx


class DocxEditorEngine:
    def __init__(self):
        self.workspace = file_mgr.workspace

    def parse_docx(self, source: Union[bytes, str, Path], filename: str = "document.docx") -> Dict[str, Any]:
        """
        Đọc và phân tích toàn diện tệp .docx thành cấu trúc có thể biên tập:
        - Danh sách đoạn văn (Paragraphs) kèm cấp độ Heading
        - Danh sách bảng biểu (Tables) kèm các ô số liệu
        - Danh mục số liệu/chỉ số định lượng được trích xuất tự động (Metrics & Data Points)
        """
        if isinstance(source, bytes):
            repaired_bytes = sanitize_and_repair_docx(source)
            doc = Document(io.BytesIO(repaired_bytes))
        else:
            fpath = Path(source)
            if not fpath.is_absolute():
                fpath = self.workspace / source
            if not fpath.exists():
                raise FileNotFoundError(f"Không tìm thấy tệp .docx: {source}")
            repaired_bytes = sanitize_and_repair_docx(fpath)
            doc = Document(io.BytesIO(repaired_bytes))

        paragraphs_data = []
        full_text_lines = []
        raw_text_parts = []
        extracted_data_points = []
        
        # Regex trích xuất số liệu / chỉ số định lượng
        data_pattern = re.compile(
            r'\b\d+(?:[.,]\d+)?\s*(?:%|mg/L|g/L|ppm|ppb|kg|g|mg|µg|ml|L|m³|m3|cm|mm|m|km|ha|°C|K|pH|WQI|DO|BOD|COD|USD|VNĐ|đồng|nghìn|triệu|tỷ)?(?=[\s,;.:\)\?]|$)|(?:p|r|R²|MAPE|RMSE|N)\s*[<=]=?\s*\d+(?:[.,]\d+)?%?',
            re.IGNORECASE
        )

        for p_idx, p in enumerate(doc.paragraphs):
            p_text = p.text.strip()
            style_name = p.style.name if p.style else "Normal"
            is_heading = "Heading" in style_name or "Tiêu đề" in style_name
            heading_level = 0
            if is_heading:
                m = re.search(r'\d+', style_name)
                heading_level = int(m.group(0)) if m else 1

            if p_text:
                full_text_lines.append(f"{'#' * heading_level + ' ' if heading_level else ''}{p_text}")
                raw_text_parts.append(p_text)

                # Scan for data points in this paragraph
                matches = data_pattern.findall(p_text)
                for m_val in matches:
                    extracted_data_points.append({
                        "id": f"p_{p_idx}_{len(extracted_data_points)}",
                        "type": "paragraph_data",
                        "location": f"Đoạn {p_idx + 1}" + (f" (Heading {heading_level})" if is_heading else ""),
                        "paragraph_index": p_idx,
                        "value": m_val,
                        "context": p_text[:120] + ("..." if len(p_text) > 120 else "")
                    })

            paragraphs_data.append({
                "index": p_idx,
                "style": style_name,
                "is_heading": is_heading,
                "heading_level": heading_level,
                "text": p_text
            })

        # Process Tables
        tables_data = []
        for t_idx, table in enumerate(doc.tables):
            rows_data = []
            for r_idx, row in enumerate(table.rows):
                cells_data = []
                for c_idx, cell in enumerate(row.cells):
                    c_text = cell.text.strip()
                    cells_data.append(c_text)
                    
                    # Scan for data points in table cells
                    if c_text:
                        matches = data_pattern.findall(c_text)
                        for m_val in matches:
                            extracted_data_points.append({
                                "id": f"t_{t_idx}_r_{r_idx}_c_{c_idx}",
                                "type": "table_cell_data",
                                "location": f"Bảng {t_idx + 1} (Hàng {r_idx + 1}, Cột {c_idx + 1})",
                                "table_index": t_idx,
                                "row_index": r_idx,
                                "col_index": c_idx,
                                "value": m_val,
                                "context": f"Ô [{r_idx+1},{c_idx+1}]: {c_text}"
                            })
                rows_data.append(cells_data)

            tables_data.append({
                "index": t_idx,
                "title": f"Bảng {t_idx + 1}",
                "row_count": len(rows_data),
                "col_count": len(rows_data[0]) if rows_data else 0,
                "rows": rows_data
            })

        unified_markdown = "\n\n".join(full_text_lines)
        word_count = len(unified_markdown.split())

        return {
            "success": True,
            "filename": filename,
            "metadata": {
                "word_count": word_count,
                "paragraph_count": len(paragraphs_data),
                "table_count": len(tables_data),
                "data_points_count": len(extracted_data_points)
            },
            "paragraphs": paragraphs_data,
            "tables": tables_data,
            "extracted_data_points": extracted_data_points,
            "full_text": unified_markdown,
            "raw_text": "\n\n".join(raw_text_parts)
        }

    def save_edited_docx(
        self,
        rel_path: str,
        content_text: str = "",
        paragraphs: List[Dict[str, Any]] = None,
        tables: List[Dict[str, Any]] = None,
        topic: str = "Tài Liệu Chỉnh Sửa"
    ) -> Dict[str, Any]:
        """
        Lưu nội dung và bảng số liệu đã chỉnh sửa thành file Word (.docx) chuẩn mực:
        - Bảo toàn font Times New Roman 14pt, giãn dòng 1.5, spacing 6pt after.
        - Đóng khung bảng dạng lưới thanh mảnh (#CBD5E1), header nổi bật.
        - Tự động áp dụng chuẩn số thập phân tiếng Việt và chỉ số hóa học.
        """
        styler = DocxStyler()
        doc = Document()
        styler.apply_document_styles(doc)

        clean_path = rel_path.strip().replace("\\", "/").lstrip("/")
        if not clean_path.lower().endswith(".docx"):
            clean_path += ".docx"

        # 1. Nếu có paragraphs dạng cấu trúc
        if paragraphs and isinstance(paragraphs, list):
            for p in paragraphs:
                p_text = (p.get("text") or "").strip()
                if not p_text:
                    continue
                h_level = p.get("heading_level", 0)
                if h_level == 1:
                    styler.add_heading_1(doc, p_text)
                elif h_level == 2:
                    styler.add_heading_2(doc, p_text)
                elif h_level == 3:
                    styler.add_heading_3(doc, p_text)
                else:
                    styler.add_paragraph(doc, p_text)

        # 2. Hoặc phân tích từ văn bản markdown / plain text
        elif content_text:
            lines = content_text.split("\n")
            for line in lines:
                l_str = line.strip()
                if not l_str:
                    continue
                if l_str.startswith("# "):
                    styler.add_heading_1(doc, l_str[2:].strip())
                elif l_str.startswith("## "):
                    styler.add_heading_2(doc, l_str[3:].strip())
                elif l_str.startswith("### "):
                    styler.add_heading_3(doc, l_str[4:].strip())
                else:
                    styler.add_paragraph(doc, l_str)

        # 3. Thêm các Bảng số liệu nếu có
        if tables and isinstance(tables, list):
            for t in tables:
                rows = t.get("rows", [])
                if rows:
                    styler.add_heading_2(doc, t.get("title", "Bảng Số Liệu"))
                    headers = rows[0]
                    data_rows = rows[1:] if len(rows) > 1 else []
                    styler.add_styled_table(doc, headers=headers, data=data_rows)

        # Lưu file vào Workspace
        target_fpath = (self.workspace / clean_path).resolve()
        target_fpath.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(target_fpath))

        stat = target_fpath.stat()
        return {
            "success": True,
            "filename": target_fpath.name,
            "rel_path": clean_path,
            "abs_path": str(target_fpath).replace("/", "\\"),
            "file_url": f"file:///{target_fpath.as_posix()}",
            "size": stat.st_size,
            "mtime": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "message": f"Đã lưu tệp Word '{target_fpath.name}' thành công với chuẩn hóa In-Place DOM."
        }

    def batch_replace_in_docx(
        self,
        rel_path: str,
        replacements: List[Dict[str, str]],
        output_rel_path: str = None
    ) -> Dict[str, Any]:
        """
        Tìm và thay thế hàng loạt số liệu hoặc thuật ngữ trong toàn bộ tệp .docx (Paragraphs & Tables):
        - `replacements`: `[{"find": "24.5%", "replace": "28,5%"}, {"find": "1000", "replace": "1.200"}]`
        """
        fpath = (self.workspace / rel_path).resolve()
        if not fpath.exists():
            raise FileNotFoundError(f"Không tìm thấy tệp .docx: {rel_path}")

        repaired_bytes = sanitize_and_repair_docx(fpath)
        doc = Document(io.BytesIO(repaired_bytes))
        total_replacements_count = 0
        details = []

        for rep in replacements:
            find_str = rep.get("find", "").strip()
            replace_str = rep.get("replace", "").strip()
            if not find_str:
                continue

            rep_count = 0

            # 1. Replace in paragraphs
            for p in doc.paragraphs:
                c = replace_text_in_paragraph_runs(p, find_str, replace_str)
                rep_count += c

            # 2. Replace in tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for p in cell.paragraphs:
                            c = replace_text_in_paragraph_runs(p, find_str, replace_str)
                            rep_count += c

            total_replacements_count += rep_count
            details.append({"find": find_str, "replace": replace_str, "occurrences": rep_count})

        # Save result
        out_path_str = output_rel_path or rel_path
        clean_out = out_path_str.strip().replace("\\", "/").lstrip("/")
        target_fpath = (self.workspace / clean_out).resolve()
        target_fpath.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(target_fpath))

        return {
            "success": True,
            "filename": target_fpath.name,
            "rel_path": clean_out,
            "abs_path": str(target_fpath).replace("/", "\\"),
            "file_url": f"file:///{target_fpath.as_posix()}",
            "total_replacements": total_replacements_count,
            "details": details,
            "message": f"Đã thay thế thành công {total_replacements_count} vị trí số liệu/thuật ngữ trong tệp Word."
        }


docx_editor = DocxEditorEngine()
