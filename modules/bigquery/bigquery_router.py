# modules/bigquery/bigquery_router.py
"""
BigQuery AI & ML API Router for WEB SUPER v3.2 / v2.0
Provides REST endpoints for Time-Series Forecast, Anomaly Detection, Key Drivers, and NL2SQL.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Body, Depends, UploadFile, File, Form, Query
import json
import csv
import io

from modules.auth.auth_service import require_operational_user, get_current_user
from modules.bigquery.bigquery_engine import bigquery_engine
from modules.history.history_manager import history_mgr

bigquery_router = APIRouter(prefix="/api/bigquery", tags=["BigQuery AI/ML Analytics"])

# ── 1. TIME-SERIES FORECASTING ──────────────────────────────────────────────
@bigquery_router.post("/forecast")
def run_time_series_forecast(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    data_points = payload.get("data_points", [])
    time_key = payload.get("time_key", "time")
    value_key = payload.get("value_key", "value")
    horizon = int(payload.get("horizon", 6))
    confidence_level = float(payload.get("confidence_level", 0.95))
    metric_name = payload.get("metric_name", "Chỉ Số Đo Đạc")
    topic = payload.get("topic", "Nghiên Cứu Khoa Học")
    api_key = payload.get("api_key")

    if not data_points or len(data_points) < 3:
        raise HTTPException(status_code=400, detail="Cần ít nhất 3 điểm dữ liệu để thực hiện dự báo chuỗi thời gian.")

    res = bigquery_engine.forecast_timeseries(
        data_points=data_points,
        time_key=time_key,
        value_key=value_key,
        horizon=horizon,
        confidence_level=confidence_level,
        metric_name=metric_name,
        topic=topic,
        api_key=api_key
    )

    if res.get("status") == "success":
        history_mgr.add_entry(
            module="bigquery",
            action_title=f"Dự báo chuỗi thời gian BigQuery AI.FORECAST: {metric_name}",
            inputs={"metric": metric_name, "horizon": horizon, "points": len(data_points)},
            result_data=res,
            summary=f"Dự báo {horizon} chu kỳ tiếp theo, xu hướng: {res.get('trend_direction')}"
        )
    return res

# ── 2. DETECT ANOMALIES ─────────────────────────────────────────────────────
@bigquery_router.post("/detect-anomalies")
def run_detect_anomalies(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    data_points = payload.get("data_points", [])
    id_or_time_key = payload.get("id_key", "id")
    value_key = payload.get("value_key", "value")
    contamination = float(payload.get("contamination", 0.05))
    metric_name = payload.get("metric_name", "Thông Số Thực Nghiệm")
    topic = payload.get("topic", "Kiểm Định Chất Lượng Dữ Liệu")
    api_key = payload.get("api_key")

    if not data_points or len(data_points) < 4:
        raise HTTPException(status_code=400, detail="Cần ít nhất 4 điểm dữ liệu để kiểm định điểm dị biệt.")

    res = bigquery_engine.detect_anomalies(
        data_points=data_points,
        id_or_time_key=id_or_time_key,
        value_key=value_key,
        contamination=contamination,
        metric_name=metric_name,
        topic=topic,
        api_key=api_key
    )

    if res.get("status") == "success":
        history_mgr.add_entry(
            module="bigquery",
            action_title=f"Kiểm định dị biệt BigQuery AI.DETECT_ANOMALIES: {metric_name}",
            inputs={"metric": metric_name, "points": len(data_points)},
            result_data=res,
            summary=f"Phát hiện {res.get('anomaly_points_count', 0)} điểm dị biệt ({res.get('anomaly_rate')})"
        )
    return res

# ── 3. KEY DRIVERS ANALYSIS ─────────────────────────────────────────────────
@bigquery_router.post("/key-drivers")
def run_key_drivers_analysis(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    data_points = payload.get("data_points", [])
    target_key = payload.get("target_key", "")
    feature_keys = payload.get("feature_keys")
    topic = payload.get("topic", "Nghiên Cứu Thực Nghiệm")
    api_key = payload.get("api_key")

    if not target_key:
        raise HTTPException(status_code=400, detail="Vui lòng chỉ định biến mục tiêu (target_key).")

    if not data_points or len(data_points) < 5:
        raise HTTPException(status_code=400, detail="Cần ít nhất 5 mẫu dữ liệu để phân tích động lực cốt lõi.")

    res = bigquery_engine.analyze_key_drivers(
        data_points=data_points,
        target_key=target_key,
        feature_keys=feature_keys,
        topic=topic,
        api_key=api_key
    )

    if res.get("status") == "success":
        history_mgr.add_entry(
            module="bigquery",
            action_title=f"Phân tích động lực cốt lõi BigQuery AI.KEY_DRIVERS: {target_key}",
            inputs={"target": target_key, "samples": len(data_points)},
            result_data=res,
            summary=f"Nhân tố ảnh hưởng lớn nhất: {res.get('top_driver')}"
        )
    return res

# ── 4. NL2SQL GENERATOR ─────────────────────────────────────────────────────
@bigquery_router.post("/generate-sql")
def generate_sql_query(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    prompt = payload.get("prompt", "").strip()
    schema_context = payload.get("schema_context", "")
    task_type = payload.get("task_type", "general")
    api_key = payload.get("api_key")

    if not prompt:
        raise HTTPException(status_code=400, detail="Vui lòng nhập câu hỏi hoặc yêu cầu phân tích.")

    res = bigquery_engine.generate_bigquery_sql(
        prompt=prompt,
        schema_context=schema_context,
        task_type=task_type,
        api_key=api_key
    )
    return res

# ── 5. UPLOAD DATASET (CSV/JSON/TSV) ───────────────────────────────────────
@bigquery_router.post("/upload-dataset")
async def upload_dataset_file(file: UploadFile = File(...), user: dict = Depends(require_operational_user)):
    try:
        content_bytes = await file.read()
        filename = file.filename or "dataset.csv"
        text = content_bytes.decode('utf-8', errors='replace')
        
        parsed_rows = []
        columns = []

        if filename.lower().endswith('.json'):
            data = json.loads(text)
            if isinstance(data, list):
                parsed_rows = data
                if parsed_rows and isinstance(parsed_rows[0], dict):
                    columns = list(parsed_rows[0].keys())
            elif isinstance(data, dict):
                # check if wrapped in "data" or "rows"
                rows = data.get("data") or data.get("rows") or [data]
                if isinstance(rows, list):
                    parsed_rows = rows
                    if parsed_rows and isinstance(parsed_rows[0], dict):
                        columns = list(parsed_rows[0].keys())
        else:
            # Auto-detect CSV/TSV delimiter (comma, semicolon, tab)
            sample_snippet = text[:2048]
            delimiter = ','
            try:
                sniffer = csv.Sniffer()
                dialect = sniffer.sniff(sample_snippet, delimiters=[',', ';', '\t', '|'])
                delimiter = dialect.delimiter
            except Exception:
                if ';' in sample_snippet and sample_snippet.count(';') > sample_snippet.count(','):
                    delimiter = ';'
                elif '\t' in sample_snippet:
                    delimiter = '\t'

            csv_file = io.StringIO(text)
            reader = csv.DictReader(csv_file, delimiter=delimiter)
            columns = reader.fieldnames or []
            for row in reader:
                parsed_rows.append(dict(row))

        return {
            "status": "success",
            "filename": filename,
            "total_rows": len(parsed_rows),
            "columns": columns,
            "sample_rows": parsed_rows[:10],
            "all_data": parsed_rows[:300],
            "message": f"✅ Đã nạp thành công tệp '{filename}' ({len(parsed_rows)} dòng, {len(columns)} cột)."
        }
    except Exception as e:
        return {"status": "error", "message": f"⚠️ Lỗi đọc tệp dữ liệu: {str(e)}"}

# ── 6. EXPORT REPORT TO DOCX ────────────────────────────────────────────────
@bigquery_router.post("/export-docx")
def export_analysis_report(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    analysis_type = payload.get("analysis_type", "forecast")
    result_data = payload.get("result_data", {})
    topic = payload.get("topic", "Phân Tích Dữ Liệu Nghiên Cứu")
    custom_storage = payload.get("custom_storage_dir")

    if not result_data:
        raise HTTPException(status_code=400, detail="Thiếu dữ liệu kết quả phân tích (result_data).")

    res = bigquery_engine.export_analysis_report_docx(
        analysis_type=analysis_type,
        result_data=result_data,
        topic=topic,
        custom_storage_dir=custom_storage
    )
    return res
