# modules/humanizer/humanizer_router.py
import io
from docx import Document
from fastapi import APIRouter, HTTPException, Body, UploadFile, File, Depends, Form
from modules.auth.auth_service import require_operational_user, get_current_user
from modules.auth.user_config_manager import load_user_config
from modules.humanizer.humanizer_engine import humanizer_engine
from modules.shared.file_manager import file_mgr
from modules.shared.docx_styler import DocxStyler, sanitize_and_repair_docx
from modules.history.history_manager import history_mgr

humanizer_router = APIRouter(tags=["AI Detector, Humanizer & Turnitin Rephrase Pro"])

@humanizer_router.post("/api/files/extract-docx-text")
async def extract_docx_text(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ tệp định dạng .docx")
    try:
        content = await file.read()
        repaired_bytes = sanitize_and_repair_docx(content)
        doc = Document(io.BytesIO(repaired_bytes))
        paragraphs = []
        for p in doc.paragraphs:
            txt = p.text.strip()
            if txt:
                paragraphs.append(txt)
        full_text = "\n\n".join(paragraphs)
        
        # Determine smart title from first non-empty paragraph or file stem
        title_cand = ""
        for p in paragraphs[:5]:
            p_clean = p.strip().strip('#*_- ')
            if len(p_clean) > 5 and not p_clean.lower().startswith(("tác giả", "author", "trường", "viện")):
                title_cand = p_clean
                break
        if not title_cand:
            import pathlib
            title_cand = pathlib.Path(file.filename).stem.replace("_", " ").replace("-", " ")

        return {
            "success": True,
            "filename": file.filename,
            "title": title_cand,
            "paragraph_count": len(paragraphs),
            "paragraphs_count": len(paragraphs),
            "word_count": len(full_text.split()),
            "full_text": full_text,
            "text": full_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi đọc tệp .docx: {str(e)}")

@humanizer_router.post("/api/humanize/analyze")
def analyze_anti_ai(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    text = payload.get("text", "")
    return humanizer_engine.analyze(text)


@humanizer_router.post("/api/humanize/unified-process")
def process_unified_humanize_turnitin(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    """Gộp 1-Click: Khử Dấu Vết AI & Chống Đạo Văn Turnitin Chuẩn Học Thuật theo 4 Quy Tắc Bất Biến"""
    text = payload.get("text", "")
    persona = payload.get("persona", "professor")
    citation_style = payload.get("citation_style", "apa7")
    if not text:
        raise HTTPException(status_code=400, detail="Vui lòng cung cấp văn bản cần xử lý.")
    user_cfg = load_user_config(user)
    user_key = user_cfg.get("gemini_api_key", "").strip() or None
    analysis = humanizer_engine.analyze(text)
    processed_text = humanizer_engine.process_unified(text, api_key=user_key, persona=persona, citation_style=citation_style)
    after_analysis = humanizer_engine.analyze(processed_text)
    res = {
        "success": True,
        "persona": persona,
        "citation_style": citation_style,
        "original_analysis": analysis,
        "processed_text": processed_text,
        "humanized_text": processed_text,
        "rephrased_text": processed_text,
        "after_analysis": after_analysis
    }
    history_mgr.add_entry(
        module="humanizer",
        action_title=f"Khử AI & Chống Đạo Văn Turnitin ({len(text.split())} từ) [{persona.upper()}]",
        inputs={"text": text, "persona": persona, "citation_style": citation_style},
        result_data=res,
        summary=f"Điểm Human: {analysis.get('human_score', 0)}% ➔ {after_analysis.get('human_score', 0)}% | Turnitin Sim: {analysis.get('similarity_index', 0)}% ➔ {after_analysis.get('similarity_index', 5)}%"
    )
    return res

@humanizer_router.post("/api/humanize/process")
def process_humanize(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    text = payload.get("text", "")
    persona = payload.get("persona", "professor")
    citation_style = payload.get("citation_style", "apa7")
    if not text:
        raise HTTPException(status_code=400, detail="Vui lòng cung cấp văn bản.")
    user_cfg = load_user_config(user)
    user_key = user_cfg.get("gemini_api_key", "").strip() or None
    analysis = humanizer_engine.analyze(text)
    humanized = humanizer_engine.humanize(text, api_key=user_key, persona=persona, citation_style=citation_style)
    after_analysis = humanizer_engine.analyze(humanized)
    res = {
        "success": True,
        "persona": persona,
        "citation_style": citation_style,
        "original_analysis": analysis,
        "humanized_text": humanized,
        "after_analysis": after_analysis
    }
    history_mgr.add_entry(
        module="humanizer",
        action_title=f"Khử Dấu Vết AI ({len(text.split())} từ) [{persona.upper()}]",
        inputs={"text": text, "persona": persona, "citation_style": citation_style},
        result_data=res,
        summary=f"Điểm Human: {analysis.get('human_score', 0)}% ➔ {after_analysis.get('human_score', 0)}% | Turnitin Sim: {after_analysis.get('similarity_index', 5)}%"
    )
    return res

@humanizer_router.post("/api/humanize/turnitin-rephrase")
def process_turnitin_rephrase(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    text = payload.get("text", "")
    persona = payload.get("persona", "graduate")
    citation_style = payload.get("citation_style", "apa7")
    if not text:
        raise HTTPException(status_code=400, detail="Vui lòng cung cấp đoạn văn bị cờ đỏ Turnitin.")
    user_cfg = load_user_config(user)
    user_key = user_cfg.get("gemini_api_key", "").strip() or None
    analysis = humanizer_engine.analyze(text)
    rephrased = humanizer_engine.turnitin_rephrase(text, api_key=user_key, persona=persona, citation_style=citation_style)
    after_analysis = humanizer_engine.analyze(rephrased)
    res = {
        "success": True,
        "mode": "turnitin_rephrase",
        "persona": persona,
        "citation_style": citation_style,
        "original_analysis": analysis,
        "rephrased_text": rephrased,
        "humanized_text": rephrased,
        "after_analysis": after_analysis
    }
    history_mgr.add_entry(
        module="turnitin_rephrase",
        action_title=f"Chống Đạo Văn Turnitin ({len(text.split())} từ) [{persona.upper()}]",
        inputs={"text": text, "persona": persona, "citation_style": citation_style},
        result_data=res,
        summary=f"Tái cấu trúc 5 kỹ thuật: Turnitin Similarity giảm còn {after_analysis.get('similarity_index', 5)}% (Điểm Human: {after_analysis.get('human_score', 0)}%)"
    )
    return res

@humanizer_router.post("/api/humanize/plagiarism-audit")
def process_plagiarism_audit(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    text = payload.get("text", "")
    persona = payload.get("persona", "professor")
    if not text:
        raise HTTPException(status_code=400, detail="Vui lòng cung cấp văn bản cần kiểm định.")
    user_cfg = load_user_config(user)
    user_key = user_cfg.get("gemini_api_key", "").strip() or None
    analysis = humanizer_engine.analyze(text)
    audit_report = humanizer_engine.plagiarism_audit(text, api_key=user_key, persona=persona)
    return {
        "success": True,
        "persona": persona,
        "analysis": analysis,
        "audit_report": audit_report
    }

@humanizer_router.post("/api/humanize/process-docx")
async def process_docx_humanizer(
    file: UploadFile = File(...),
    persona: str = Form("professor"),
    citation_style: str = Form("apa7"),
    user: dict = Depends(require_operational_user)
):
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ tệp định dạng .docx")
    
    try:
        user_cfg = load_user_config(user)
        user_key = user_cfg.get("gemini_api_key", "").strip() or None

        content = await file.read()
        doc_orig = Document(io.BytesIO(content))
        raw_text = "\n\n".join([p.text.strip() for p in doc_orig.paragraphs if p.text.strip()])
        analysis = humanizer_engine.analyze(raw_text)
        
        humanized_bytes = humanizer_engine.humanize_docx_bytes(content, api_key=user_key, persona=persona, citation_style=citation_style)
        clean_name = f"HUMANIZED_{persona.upper()}_{file.filename}"
        rel_path = f"Ban_Thao/{clean_name}"
        saved_file = file_mgr.save_bytes(rel_path, humanized_bytes)
        
        doc_new = Document(io.BytesIO(humanized_bytes))
        humanized_text = "\n\n".join([p.text.strip() for p in doc_new.paragraphs if p.text.strip()])
        analysis_after = humanizer_engine.analyze(humanized_text)
        
        res = {
            "success": True,
            "filename": saved_file["filename"],
            "rel_path": saved_file["rel_path"],
            "abs_path": saved_file["abs_path"],
            "file_url": saved_file["file_url"],
            "persona": persona,
            "citation_style": citation_style,
            "original_text": raw_text,
            "humanized_text": humanized_text,
            "analysis_before": analysis,
            "analysis_after": analysis_after,
            "word_count": len(humanized_text.split()),
            "cliches_removed": len(analysis.get("found_cliches", []))
        }
        history_mgr.add_entry(
            module="humanizer",
            action_title=f"Khử AI tệp Word In-Place: {file.filename}",
            inputs={"filename": file.filename, "persona": persona, "citation_style": citation_style},
            result_data=res,
            summary=f"Xuất bản: {clean_name} (Điểm Human: {analysis_after.get('human_score', 0)}% | Turnitin Sim: {analysis_after.get('similarity_index', 5)}%)"
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý tệp .docx: {str(e)}")


@humanizer_router.post("/api/humanize/paragraph-by-paragraph")
def humanize_paragraph_route(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    """Khử dấu vết AI từng đoạn văn kèm Bản đồ nhiệt Burstiness & Perplexity."""
    text = payload.get("text", "")
    mode = payload.get("mode", "moderate")
    persona = payload.get("persona", "professor")
    citation_style = payload.get("citation_style", "apa7")
    if not text:
        raise HTTPException(status_code=400, detail="Vui lòng cung cấp văn bản cần xử lý.")
    user_cfg = load_user_config(user)
    user_key = user_cfg.get("gemini_api_key", "").strip() or None
    return humanizer_engine.humanize_paragraph_by_paragraph(
        text, mode=mode, api_key=user_key, persona=persona, citation_style=citation_style
    )


