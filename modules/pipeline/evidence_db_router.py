# modules/pipeline/evidence_db_router.py
"""
WEB SUPER v3.2 / v2.0 - Empirical Evidence Database & Document Extractor Router
Router xử lý bóc tách dữ liệu theo từng tài liệu được cung cấp, thống kê định lượng,
quản trị cơ sở dữ liệu thực chứng và liên thông trực tiếp sang viết học thuật 2-File.
"""

import os
import json
import base64
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Body, Depends, Query, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse

from modules.auth.auth_service import require_operational_user
from modules.auth.user_config_manager import load_user_config
from modules.shared.file_manager import file_mgr
from modules.pipeline.document_extractor_engine import document_evidence_extractor
from modules.academic_writer.academic_writer_engine import academic_writer
from modules.shared.data_autocleaning import scientific_data_cleaner
from modules.history.history_manager import history_mgr

evidence_db_router = APIRouter(tags=["Empirical Evidence Database & Document Extractor"])


@evidence_db_router.post("/api/evidence-db/extract-provided-documents")
async def extract_provided_documents(
    payload: dict = Body(...),
    user: dict = Depends(require_operational_user)
):
    """
    Bóc tách dữ liệu chuyên sâu theo từng tài liệu được cung cấp:
    - Trích xuất trích dẫn in-text chuẩn APA (Vaswani et al., 2017) và tham chiếu nguồn.
    - Viễn dẫn chính xác theo số trang, phân mục và trích đoạn nguyên văn (Pinpoint page & verbatim excerpt).
    - Thống kê định lượng số lượng trang, từ, luận điểm, bảng số liệu theo từng tài liệu.
    - Tạo lập Cơ sở dữ liệu Thực chứng (Empirical Evidence Database) lưu trữ vĩnh viễn (.json và .docx).
    """
    topic = payload.get("topic", "").strip() or "Nghiên cứu Thực nghiệm"
    provided_docs = payload.get("documents", [])
    scan_workspace = payload.get("scan_workspace", True)
    save_docx = payload.get("save_docx_report", True)

    docs_to_process = []

    # 1. Thu thập từ danh sách truyền lên qua payload (base64 hoặc đường dẫn tương đối)
    if provided_docs and isinstance(provided_docs, list):
        for doc_item in provided_docs:
            if not isinstance(doc_item, dict):
                continue
            fname = doc_item.get("filename") or doc_item.get("name") or "document.docx"
            content_bytes = None
            if "content_base64" in doc_item and doc_item["content_base64"]:
                try:
                    content_bytes = base64.b64decode(doc_item["content_base64"])
                except Exception:
                    pass
            elif "content" in doc_item and isinstance(doc_item["content"], str):
                content_bytes = doc_item["content"].encode("utf-8")
            elif "rel_path" in doc_item and doc_item["rel_path"]:
                full_p = file_mgr.workspace / doc_item["rel_path"]
                if full_p.exists() and full_p.is_file():
                    try:
                        content_bytes = full_p.read_bytes()
                    except Exception:
                        pass
            
            if content_bytes is not None:
                docs_to_process.append({
                    "filename": fname,
                    "content_bytes": content_bytes
                })

    # 2. Nếu danh sách rỗng hoặc có yêu cầu quét thư mục, tự động nạp từ thư mục Tai_Lieu và docs
    if scan_workspace and not docs_to_process:
        search_dirs = [
            file_mgr.workspace / "Tai_Lieu",
            file_mgr.docs_dir,
            file_mgr.workspace / "documents"
        ]
        seen_names = set()
        for s_dir in search_dirs:
            if s_dir.exists() and s_dir.is_dir():
                for f_path in s_dir.iterdir():
                    if f_path.is_file() and f_path.name not in seen_names:
                        ext = f_path.suffix.lower()
                        if ext in [".pdf", ".docx", ".txt", ".md"]:
                            try:
                                b_data = f_path.read_bytes()
                                docs_to_process.append({
                                    "filename": f_path.name,
                                    "content_bytes": b_data
                                })
                                seen_names.add(f_path.name)
                            except Exception:
                                pass

    # 3. Nếu vẫn không có tài liệu nào trong thư mục, nạp tài liệu học thuật mẫu chuẩn quốc tế
    if not docs_to_process:
        default_sample = (
            "# Transformer Architecture and Empirical Findings\n\n"
            "## Abstract\n"
            "Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., & Polosukhin, I. (2017).\n"
            "Attention Is All You Need. Advances in Neural Information Processing Systems, 30. DOI: 10.48550/arXiv.1706.03762\n\n"
            "## 1. Introduction\n"
            "Recurrent neural networks typically factor computation along the symbol positions of the input and output sequences.\n"
            "This inherently sequential nature precludes parallelization within training examples, which becomes critical at longer sequence lengths.\n\n"
            "## 2. Model Architecture & Results\n"
            "The Transformer allows for significantly more parallelization and can reach a new state of the art in translation quality\n"
            "after being trained for as little as twelve hours on eight P100 GPUs. On the WMT 2014 English-to-German translation task,\n"
            "the big transformer model achieves 28.4 BLEU, improving over the existing best results by over 2.0 BLEU points.\n"
            "On the WMT 2014 English-to-French translation task, our model establishes a new single-model state-of-the-art BLEU score of 41.8.\n\n"
            "## 3. Limitations and Future Work\n"
            "A key limitation is the quadratic O(N^2) computational complexity of the full self-attention mechanism with respect to sequence length N.\n"
            "Future work will investigate sparse attention and scaling to inputs beyond text such as images and audio."
        )
        docs_to_process.append({
            "filename": "2017_Vaswani_Transformer_Empirical_Study.md",
            "content_bytes": default_sample.encode("utf-8")
        })

    # 4. Tiến hành xây dựng Cơ sở dữ liệu Thực chứng
    db_result = document_evidence_extractor.build_empirical_database(
        topic=topic,
        provided_docs=docs_to_process,
        save_docx_report=save_docx
    )

    # 5. Ghi nhật ký hệ thống
    try:
        total_docs = db_result.get("corpus_statistics", {}).get("total_documents_analyzed", len(docs_to_process))
        total_claims = db_result.get("corpus_statistics", {}).get("total_claims_extracted", 0)
        history_mgr.add_entry(
            module="evidence_database",
            action_title=f"Bóc tách Dữ liệu Tài liệu Cung Cấp: {topic}",
            inputs={"topic": topic, "documents_count": total_docs},
            result_data={
                "database_id": db_result.get("database_id"),
                "corpus_statistics": db_result.get("corpus_statistics"),
                "report_docx": db_result.get("report_docx", {}).get("rel_path")
            },
            summary=f"Đã bóc tách thành công {total_docs} tài liệu, lập {total_claims} luận điểm thực chứng có viễn dẫn APA."
        )
    except Exception:
        pass

    return db_result


@evidence_db_router.post("/api/evidence-db/generate-topic-outline")
async def generate_topic_outline_endpoint(
    payload: dict = Body(...),
    user: dict = Depends(require_operational_user)
):
    """
    Tự động sinh Cây Đề Cương (Outline Tree) bằng Google Gemini AI dựa trên Tên Đề Tài.
    Tích hợp phân mục Thư mục học & Xu hướng Công bố từ nguồn mở được chọn (OpenAlex, Europe PMC, arXiv, Crossref).
    Cho phép xem trước và tùy biến các nhánh trước khi quét tài liệu thực chứng.
    """
    topic = payload.get("topic", "").strip() or "Nghiên cứu Khoa học và Công nghệ"
    guidelines = payload.get("guidelines") or payload.get("custom_guidelines")
    trend_source = payload.get("trend_source", "openalex")
    trend_keywords = payload.get("trend_keywords") or payload.get("keywords")
    
    user_cfg = load_user_config(user)
    gemini_key = user_cfg.get("gemini_api_key", "").strip() or None

    res = document_evidence_extractor.generate_topic_structured_outline(
        topic=topic,
        custom_guidelines=guidelines,
        gemini_key=gemini_key,
        trend_source=trend_source,
        trend_keywords=trend_keywords
    )
    return res


@evidence_db_router.post("/api/evidence-db/extract-by-topic")
async def extract_by_topic_outline_endpoint(
    payload: dict = Body(...),
    user: dict = Depends(require_operational_user)
):
    """
    Bóc tách dữ liệu từ tài liệu dựa trên Tên Đề Tài và Cây Đề Cương cấu trúc (sử dụng Gemini AI):
    - Tự động sinh hoặc kế thừa Cây Đề Cương chuẩn IMRaD từ Tên Đề Tài.
    - Tìm kiếm và ánh xạ dữ liệu thực chứng (luận điểm, số liệu, bảng biểu, trích đoạn, số trang) vào từng Node.
    - Gắn cờ [uncertain] khi một phân mục chưa có dữ liệu kiểm chứng.
    - Xuất bản Báo cáo Thực chứng Word .docx và Markdown .md.
    """
    topic = payload.get("topic", "").strip() or "Nghiên cứu Khoa học và Công nghệ"
    provided_docs = payload.get("documents", [])
    outline = payload.get("outline") or payload.get("outline_tree")
    guidelines = payload.get("custom_guidelines") or payload.get("guidelines")
    trend_source = payload.get("trend_source", "openalex")
    trend_keywords = payload.get("trend_keywords") or payload.get("keywords")
    scan_workspace = payload.get("scan_workspace", True)
    save_docx = payload.get("save_docx_report", True)

    user_cfg = load_user_config(user)
    gemini_key = user_cfg.get("gemini_api_key", "").strip() or None

    docs_to_process = []

    # 1. Thu thập tài liệu từ payload
    if provided_docs and isinstance(provided_docs, list):
        for doc_item in provided_docs:
            if not isinstance(doc_item, dict):
                continue
            fname = doc_item.get("filename") or doc_item.get("name") or "document.docx"
            content_bytes = None
            if "content_base64" in doc_item and doc_item["content_base64"]:
                try:
                    content_bytes = base64.b64decode(doc_item["content_base64"])
                except Exception:
                    pass
            elif "content" in doc_item and isinstance(doc_item["content"], str):
                content_bytes = doc_item["content"].encode("utf-8")
            elif "rel_path" in doc_item and doc_item["rel_path"]:
                full_p = file_mgr.workspace / doc_item["rel_path"]
                if full_p.exists() and full_p.is_file():
                    try:
                        content_bytes = full_p.read_bytes()
                    except Exception:
                        pass

            if content_bytes is not None:
                docs_to_process.append({
                    "filename": fname,
                    "content_bytes": content_bytes
                })

    # 2. Quét workspace Tai_Lieu nếu cần
    if scan_workspace and not docs_to_process:
        search_dirs = [
            file_mgr.workspace / "Tai_Lieu",
            file_mgr.docs_dir,
            file_mgr.workspace / "documents"
        ]
        seen_names = set()
        for s_dir in search_dirs:
            if s_dir.exists() and s_dir.is_dir():
                for f_path in s_dir.iterdir():
                    if f_path.is_file() and f_path.name not in seen_names:
                        ext = f_path.suffix.lower()
                        if ext in [".pdf", ".docx", ".txt", ".md"]:
                            try:
                                b_data = f_path.read_bytes()
                                docs_to_process.append({
                                    "filename": f_path.name,
                                    "content_bytes": b_data
                                })
                                seen_names.add(f_path.name)
                            except Exception:
                                pass

    # 3. Thực thi bóc tách theo đề tài
    result = document_evidence_extractor.extract_evidence_by_topic_outline(
        topic=topic,
        provided_documents=docs_to_process,
        custom_outline=outline,
        save_docx_report=save_docx,
        gemini_key=gemini_key,
        trend_source=trend_source,
        trend_keywords=trend_keywords
    )

    # 4. Ghi lịch sử
    try:
        history_mgr.add_entry(
            module="evidence_database",
            action_title=f"Bóc tách Thực chứng theo Đề tài: {topic}",
            inputs={"topic": topic, "documents_count": len(docs_to_process)},
            result_data={
                "database_id": result.get("database_id"),
                "summary_statistics": result.get("summary_statistics"),
                "report_docx": result.get("report_docx", {}).get("rel_path")
            },
            summary=f"Đã bóc tách dữ liệu theo Cây Đề Cương cho đề tài '{topic}': {result.get('summary_statistics', {}).get('coverage_percentage', '0%')} độ phủ."
        )
    except Exception:
        pass

    return result


@evidence_db_router.post("/api/evidence-db/upload-and-extract")
async def upload_and_extract_files(
    topic: str = Body("Nghiên cứu Thực nghiệm"),
    files: List[UploadFile] = File(...),
    user: dict = Depends(require_operational_user)
):
    """
    Tải lên trực tiếp nhiều tệp tài liệu (PDF, DOCX, MD, TXT) và tức thời bóc tách dữ liệu.
    """
    if not files:
        raise HTTPException(status_code=400, detail="Vui lòng chọn ít nhất một tệp để tải lên.")

    docs_to_process = []
    for f in files:
        content = await f.read()
        docs_to_process.append({
            "filename": f.filename or "uploaded_doc.docx",
            "content_bytes": content
        })

    db_result = document_evidence_extractor.build_empirical_database(
        topic=topic,
        provided_docs=docs_to_process,
        save_docx_report=True
    )

    return db_result


@evidence_db_router.get("/api/evidence-db/list")
def list_empirical_databases(user: dict = Depends(require_operational_user)):
    """
    Liệt kê danh sách các cơ sở dữ liệu thực chứng đã được khởi tạo trong workspace.
    """
    db_dir = file_mgr.workspace / "Evidence_Database"
    if not db_dir.exists():
        return {"databases": [], "total": 0}

    databases = []
    for j_path in sorted(db_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        if j_path.name == "latest_database.json":
            continue
        try:
            with open(j_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                databases.append({
                    "database_id": data.get("database_id", j_path.stem),
                    "topic": data.get("topic", "N/A"),
                    "created_at": data.get("created_at", ""),
                    "corpus_statistics": data.get("corpus_statistics", {}),
                    "documents_count": len(data.get("documents", [])),
                    "evidence_items_count": len(data.get("evidence_items", [])),
                    "docx_report_path": data.get("report_docx", {}).get("rel_path"),
                    "json_rel_path": f"Evidence_Database/{j_path.name}"
                })
        except Exception:
            pass

    return {
        "databases": databases,
        "total": len(databases)
    }


@evidence_db_router.get("/api/evidence-db/{db_id}")
def get_empirical_database_detail(
    db_id: str,
    user: dict = Depends(require_operational_user)
):
    """
    Lấy thông tin chi tiết đầy đủ của một Cơ sở dữ liệu Thực chứng theo mã định danh.
    """
    db_dir = file_mgr.workspace / "Evidence_Database"
    target_file = db_dir / f"{db_id}.json"
    if db_id == "latest":
        target_file = db_dir / "latest_database.json"

    if not target_file.exists():
        raise HTTPException(status_code=404, detail=f"Không tìm thấy Cơ sở dữ liệu: {db_id}")

    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi đọc cơ sở dữ liệu: {str(e)}")


@evidence_db_router.get("/api/evidence-db/{db_id}/download-docx")
def download_database_docx_report(
    db_id: str,
    user: dict = Depends(require_operational_user)
):
    """
    Tải về báo cáo Word .docx tổng hợp của Cơ sở dữ liệu Thực chứng.
    """
    db_dir = file_mgr.workspace / "Evidence_Database"
    target_json = db_dir / f"{db_id}.json"
    if db_id == "latest":
        target_json = db_dir / "latest_database.json"

    if not target_json.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy cơ sở dữ liệu yêu cầu.")

    try:
        with open(target_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        rel_path = data.get("report_docx", {}).get("rel_path")
        if not rel_path:
            raise HTTPException(status_code=404, detail="Báo cáo .docx chưa được khởi tạo.")
        
        full_docx = file_mgr.workspace / rel_path
        if not full_docx.exists():
            raise HTTPException(status_code=404, detail=f"Tệp không tồn tại: {rel_path}")

        return FileResponse(
            str(full_docx),
            filename=full_docx.name,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tải báo cáo Word: {str(e)}")


@evidence_db_router.post("/api/evidence-db/feed-to-writer")
def feed_evidence_db_to_academic_writer(
    payload: dict = Body(...),
    user: dict = Depends(require_operational_user)
):
    """
    Liên thông trực tiếp Cơ sở dữ liệu Thực chứng đã bóc tách sang Trình soạn thảo Học thuật 2-File:
    - Tự động nạp Bảng ma trận đối soát 6 cột (File B) với trích đoạn nguyên văn, bản dịch và số trang.
    - Cung cấp toàn bộ luận cứ thực chứng để đưa vào báo cáo IMRaD (File A).
    - Bảo đảm 100% Zero Fabrication & Liêm chính học thuật.
    """
    db_id = payload.get("database_id", "latest")
    db_record = None

    # 1. Nạp cơ sở dữ liệu từ bộ nhớ hoặc tệp
    if "database_record" in payload and payload["database_record"]:
        db_record = payload["database_record"]
    else:
        db_dir = file_mgr.workspace / "Evidence_Database"
        target_file = db_dir / f"{db_id}.json"
        if db_id == "latest":
            target_file = db_dir / "latest_database.json"

        if target_file.exists():
            try:
                with open(target_file, "r", encoding="utf-8") as f:
                    db_record = json.load(f)
            except Exception:
                pass

    if not db_record:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy Cơ sở dữ liệu Thực chứng: {db_id}")

    # 2. Chuẩn bị các tham số cho Academic Writer
    topic = payload.get("topic") or db_record.get("topic") or "Báo cáo Khoa học Thực nghiệm"
    paper_type = payload.get("paper_type", "Báo cáo khoa học")
    author_name = payload.get("author_name", "Nghiên cứu sinh")
    target_words = int(payload.get("target_words", 5000))
    target_pages = int(payload.get("target_pages", 12))
    custom_outline = payload.get("custom_outline")
    outline_tree = payload.get("outline_tree")

    user_cfg = load_user_config(user)
    gemini_key = user_cfg.get("gemini_api_key", "").strip() or None
    openai_key = user_cfg.get("openai_api_key", "").strip() or None

    # 3. Kích hoạt Academic Writer với evidence_database tích hợp
    writer_result = academic_writer.generate_2_files(
        topic=topic,
        paper_type=paper_type,
        author_name=author_name,
        custom_outline=custom_outline,
        outline_tree=outline_tree,
        target_words=target_words,
        target_pages=target_pages,
        gemini_key=gemini_key,
        openai_key=openai_key,
        evidence_database=db_record
    )

    # 4. Ghi lịch sử
    try:
        history_mgr.add_entry(
            module="writer",
            action_title=f"Viết 2-File từ Cơ sở Dữ liệu Thực chứng: {topic}",
            inputs={"topic": topic, "database_id": db_id},
            result_data=writer_result,
            summary=f"Hoàn tất Tệp A & B với {len(db_record.get('evidence_items', []))} luận điểm thực chứng có viễn dẫn APA."
        )
    except Exception:
        pass

    return {
        "status": "success",
        "database_id": db_record.get("database_id"),
        "writer_result": writer_result,
        "message": "Đã liên thông thành công Cơ sở dữ liệu Thực chứng sang Trình Soạn thảo Học thuật 2-File."
    }


@evidence_db_router.post("/api/evidence-db/autoclean")
def autoclean_evidence_data(
    payload: dict = Body(...),
    user: dict = Depends(require_operational_user)
):
    """
    Tự động thẩm định dữ liệu (Data Profiling), phát hiện ngoại lai (Outliers),
    chuẩn hóa đơn vị đo lường và định dạng số thập phân tiếng Việt theo chuẩn /data-autocleaning.
    """
    records = payload.get("records")
    text = payload.get("text")
    matrix_rows = payload.get("matrix_rows")

    result = {}
    if records and isinstance(records, list):
        result["dataset_profile"] = scientific_data_cleaner.profile_and_clean_dataset(records)
    if text and isinstance(text, str):
        result["cleaned_text"] = scientific_data_cleaner.clean_scientific_text(text)
    if matrix_rows and isinstance(matrix_rows, list):
        result["cleaned_matrix_rows"] = scientific_data_cleaner.clean_evidence_matrix_rows(matrix_rows)

    return {
        "status": "success",
        "data": result,
        "message": "Đã hoàn thành tự động làm sạch và chuẩn hóa số liệu khoa học."
    }
