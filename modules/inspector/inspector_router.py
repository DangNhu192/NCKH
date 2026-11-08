# -*- coding: utf-8 -*-
"""
modules/inspector/inspector_router.py
=====================================
API Endpoints cho Trình Đối Soát Song Song & Cổng Kiểm Duyệt 4 Tầng
(Dual-Pane Evidence Inspector & 4-Layer Pre-Commit Verification Gate Router v4.2)
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Request, Response
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from pydantic import BaseModel

from modules.inspector.evidence_inspector_engine import evidence_inspector_engine
from modules.shared.file_manager import file_mgr

inspector_router = APIRouter(prefix="/api/inspector", tags=["Dual-Pane Evidence Inspector v4.2"])


class GenerateBundleRequest(BaseModel):
    docx_filename: Optional[str] = None
    article_title: Optional[str] = "BÁO CÁO KHOA HỌC CHUẨN MỰC THẠC SĨ (KÈM BỘ ĐỐI SOÁT THỰC CHỨNG)"
    evidence_items: Optional[List[Dict[str, Any]]] = None
    target_dir: Optional[str] = None


class VerifyGateRequest(BaseModel):
    catalog: Optional[Dict[str, Any]] = None
    html_filename: Optional[str] = "doi_soat.html"
    docx_filename: Optional[str] = None


@inspector_router.post("/generate-bundle")
async def generate_inspection_bundle(req: GenerateBundleRequest):
    """
    Sinh trọn bộ gói sản phẩm đối soát song song và kiểm duyệt 4 tầng (v4.2):
    1. multi_evidence_catalog.json
    2. Bang_Truy_Xuat_Nguon_Goc_Tai_Lieu.docx (Khổ ngang A4)
    3. Bang_Truy_Xuat_Nguon_Goc_Tai_Lieu.md
    4. doi_soat.html
    5. server.js & Khoi_Chay_Doi_Soat.bat (Node.js HTTP 206 Streaming)
    """
    try:
        dest_dir = Path(req.target_dir) if req.target_dir else evidence_inspector_engine.xuat_ban_dir
        dest_dir.mkdir(parents=True, exist_ok=True)

        # 1. Tạo catalog 10 trường
        catalog = evidence_inspector_engine.generate_multi_evidence_catalog(req.evidence_items)
        catalog_path = dest_dir / "multi_evidence_catalog.json"
        catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")

        # 2. Tạo Bảng ma trận truy xuất nguồn gốc DOCX (A4 Landscape) và MD
        matrix_docx = dest_dir / "Bang_Truy_Xuat_Nguon_Goc_Tai_Lieu.docx"
        evidence_inspector_engine.generate_traceability_matrix_docx(catalog, matrix_docx)
        
        matrix_md = dest_dir / "Bang_Truy_Xuat_Nguon_Goc_Tai_Lieu.md"
        evidence_inspector_engine.generate_traceability_matrix_md(catalog, matrix_md)

        # 3. Xác định file DOCX bản thảo nguồn
        docx_file = None
        if req.docx_filename:
            docx_file = dest_dir / req.docx_filename
            if not docx_file.exists():
                docx_file = evidence_inspector_engine.ban_thao_dir / req.docx_filename
        else:
            # Tìm file docx gần nhất trong Xuat_Ban hoặc Ban_Thao
            for d in [dest_dir, evidence_inspector_engine.xuat_ban_dir, evidence_inspector_engine.ban_thao_dir]:
                candidates = list(d.glob("*.docx"))
                if candidates:
                    docx_file = candidates[0]
                    break

        if not docx_file:
            docx_file = dest_dir / "Bao_Cao_Khoa_Hoc.docx"

        # 4. Sinh giao diện song song doi_soat.html
        html_path = dest_dir / "doi_soat.html"
        evidence_inspector_engine.generate_dual_pane_html(
            docx_path=docx_file,
            catalog=catalog,
            output_html_path=html_path,
            article_title=req.article_title or "BÁO CÁO KHOA HỌC CHUẨN MỰC THẠC SĨ"
        )

        # 5. Đóng gói server.js và bat launcher
        evidence_inspector_engine.package_standalone_bundle(dest_dir, port=8765)

        return {
            "status": "success",
            "message": "Đã tạo thành công trọn bộ gói đối soát song song v4.2!",
            "bundle_dir": str(dest_dir),
            "total_evidences": len(catalog),
            "files": {
                "catalog": str(catalog_path),
                "matrix_docx": str(matrix_docx),
                "matrix_md": str(matrix_md),
                "doi_soat_html": str(html_path),
                "server_js": str(dest_dir / "server.js"),
                "bat_launcher": str(dest_dir / "Khoi_Chay_Doi_Soat.bat")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tạo gói đối soát: {str(e)}")


@inspector_router.post("/verify-gate")
async def verify_precommit_gate(req: VerifyGateRequest):
    """
    Thực thi Cổng kiểm duyệt 4 tầng tự động (Pre-Commit Verification Gate v4.2):
    - Tầng 1: Match ratio >= 0.60 trên PDF thô.
    - Tầng 2: Interactive Buttons & Anti-Topic Fraud.
    - Tầng 3: DOCX Synchronization & Metric Locking.
    - Tầng 4: Zero-Hallucination Circuit Breaker (Pass/Fail).
    """
    try:
        catalog = req.catalog
        if not catalog:
            catalog_file = evidence_inspector_engine.xuat_ban_dir / "multi_evidence_catalog.json"
            if catalog_file.exists():
                catalog = json.loads(catalog_file.read_text(encoding="utf-8"))
            else:
                catalog = evidence_inspector_engine.generate_multi_evidence_catalog()

        html_file = evidence_inspector_engine.xuat_ban_dir / (req.html_filename or "doi_soat.html")
        docx_file = None
        if req.docx_filename:
            docx_file = evidence_inspector_engine.xuat_ban_dir / req.docx_filename
            if not docx_file.exists():
                docx_file = evidence_inspector_engine.ban_thao_dir / req.docx_filename

        report = evidence_inspector_engine.run_4_layer_verification_gate(
            catalog=catalog,
            html_path=html_file,
            docx_path=docx_file
        )

        return {
            "status": "success",
            "gate_passed": report.get("passed", False),
            "report": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi thực thi cổng kiểm duyệt: {str(e)}")


@inspector_router.get("/catalog")
async def get_current_catalog():
    """Lấy danh mục vi luận điểm thực chứng hiện hành."""
    catalog_file = evidence_inspector_engine.xuat_ban_dir / "multi_evidence_catalog.json"
    if catalog_file.exists():
        try:
            catalog = json.loads(catalog_file.read_text(encoding="utf-8"))
            return {"status": "success", "catalog": catalog, "total": len(catalog)}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi đọc catalog: {str(e)}")
    
    catalog = evidence_inspector_engine.generate_multi_evidence_catalog()
    return {"status": "success", "catalog": catalog, "total": len(catalog)}


@inspector_router.post("/generate-matrix")
async def generate_traceability_matrix(req: GenerateBundleRequest):
    """Xuất bản riêng tệp Bảng Ma trận Truy xuất Nguồn gốc (Bang_Truy_Xuat_Nguon_Goc_Tai_Lieu.docx)."""
    try:
        catalog = evidence_inspector_engine.generate_multi_evidence_catalog(req.evidence_items)
        out_docx = evidence_inspector_engine.xuat_ban_dir / "Bang_Truy_Xuat_Nguon_Goc_Tai_Lieu.docx"
        evidence_inspector_engine.generate_traceability_matrix_docx(catalog, out_docx)
        out_md = evidence_inspector_engine.xuat_ban_dir / "Bang_Truy_Xuat_Nguon_Goc_Tai_Lieu.md"
        evidence_inspector_engine.generate_traceability_matrix_md(catalog, out_md)

        return {
            "status": "success",
            "docx_path": str(out_docx),
            "md_path": str(out_md),
            "message": "Đã xuất bản Bảng Ma trận Truy xuất Nguồn gốc Tài liệu (Khổ ngang A4) thành công!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xuất bảng ma trận: {str(e)}")


@inspector_router.get("/view-html", response_class=HTMLResponse)
async def view_doi_soat_html():
    """Xem trực tiếp tệp doi_soat.html được sinh ra."""
    html_file = evidence_inspector_engine.xuat_ban_dir / "doi_soat.html"
    if not html_file.exists():
        # Tự động sinh nếu chưa có
        catalog = evidence_inspector_engine.generate_multi_evidence_catalog()
        evidence_inspector_engine.generate_dual_pane_html(
            docx_path=evidence_inspector_engine.xuat_ban_dir / "Bao_Cao_Khoa_Hoc.docx",
            catalog=catalog,
            output_html_path=html_file
        )

    return HTMLResponse(content=html_file.read_text(encoding="utf-8"))


@inspector_router.get("/stream-pdf/{filename}")
async def stream_pdf(filename: str, request: Request):
    """
    Truyền phát file PDF theo chuẩn HTTP 206 Partial Content (Range Requests)
    phục vụ xem tức thì trên Mozilla PDF.js Canvas.
    """
    pdf_path = evidence_inspector_engine.tai_lieu_dir / filename
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy tệp PDF.")

    file_size = pdf_path.stat().st_size
    range_header = request.headers.get("range")

    if range_header:
        # Xử lý HTTP 206 Partial Content
        range_match = re.match(r"bytes=(\d+)-(\d*)", range_header)
        if range_match:
            start = int(range_match.group(1))
            end = int(range_match.group(2)) if range_match.group(2) else file_size - 1
            if start >= file_size:
                raise HTTPException(status_code=416, detail="Requested Range Not Satisfiable")
            chunk_size = (end - start) + 1

            def iter_chunk():
                with open(pdf_path, "rb") as f:
                    f.seek(start)
                    bytes_left = chunk_size
                    while bytes_left > 0:
                        chunk = f.read(min(65536, bytes_left))
                        if not chunk:
                            break
                        bytes_left -= len(chunk)
                        yield chunk

            headers = {
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(chunk_size),
                "Content-Type": "application/pdf"
            }
            return StreamingResponse(iter_chunk(), status_code=206, headers=headers)

    # Nếu không có header range, trả về toàn bộ tệp với Accept-Ranges
    return FileResponse(
        str(pdf_path),
        media_type="application/pdf",
        headers={"Accept-Ranges": "bytes", "Content-Length": str(file_size)}
    )
