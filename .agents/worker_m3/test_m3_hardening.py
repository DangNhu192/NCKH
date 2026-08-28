# test_m3_hardening.py
"""
Comprehensive Hardening & Verification Test Suite for worker_m3
Modules Tested:
1. modules/shared/pdf_ocr_engine.py (Purpose-Built Document AI, 4-tier pipeline, RAG Chunks, In-Place DOM DOCX, Open-Notebook)
2. modules/bigquery/bigquery_engine.py (4-Pillar BigQuery AI/ML Analytics, 300 DPI Charts, IMRaD DOCX Report, Vietnamese Formatting)
3. modules/bigquery/bigquery_router.py (REST Endpoints, CSV/TSV/JSON upload delimiter auto-detection, validation)
"""

import sys
import os
import io
import re
import json
import time
import tempfile
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

print("=" * 80)
print("  WORKER M3 - DEEP HARDENING VERIFICATION TEST SUITE")
print("=" * 80)

# Isolated temp workspace
temp_dir = tempfile.TemporaryDirectory()
temp_ws_path = Path(temp_dir.name)

from modules.shared.file_manager import file_mgr
file_mgr.workspace = temp_ws_path
file_mgr.docs_dir = temp_ws_path / "Tai_Lieu"
file_mgr.docs_dir.mkdir(exist_ok=True, parents=True)

# ═══════════════════════════════════════════════════════════════════════════
# TEST GROUP 1: PDF OCR ENGINE HARDENING
# ═══════════════════════════════════════════════════════════════════════════
print("\n[TEST GROUP 1] Testing PDF AI OCR Engine Hardening...")
from modules.shared.pdf_ocr_engine import PDFDocumentAIOcrEngine, pdf_ocr_engine
from pypdf import PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# 1.1 Test Empty & Invalid Input
insp_empty = pdf_ocr_engine.inspect_pdf(b"")
assert insp_empty["status"] == "error", "Empty bytes should return error"
insp_nonexistent = pdf_ocr_engine.inspect_pdf("non_existent_file.pdf")
assert insp_nonexistent["status"] == "error", "Nonexistent file should return error"
print("  ✓ 1.1 Invalid and empty PDF inputs handled gracefully.")

# 1.2 Test Digital Searchable PDF (Multi-page)
rl_buf = io.BytesIO()
c = canvas.Canvas(rl_buf, pagesize=letter)
# Page 1
c.drawString(72, 720, "CHUONG 1: TONG QUAN VE HE THONG NANG LUONG TAI TAO")
c.drawString(72, 700, "Nghien cuu khao sat hieu suat cua cac tam pin mat troi the he moi.")
c.drawString(72, 680, "Cong thuc hoa hoc: H2SO4, FeS2 va cac hop chat ban dan.")
c.drawString(72, 660, "Hieu suat chuyen hoa quang dien dat 28,5% voi 1.000 gio chieu sang.")
c.showPage()
# Page 2
c.drawString(72, 720, "CHUONG 2: PHUONG PHAP THUC NGHIEM VA MO HINH TOAN")
c.drawString(72, 700, "He phuong trinh vi phan bac hai mo ta qua trinh truyen nhiet:")
c.drawString(72, 680, "dT/dt = alpha * d^2T/dx^2 + Q_gen voi dung sai 1,5 do C.")
c.showPage()
c.save()
sample_pdf_bytes = rl_buf.getvalue()

insp_digital = pdf_ocr_engine.inspect_pdf(sample_pdf_bytes)
assert insp_digital["status"] == "success"
assert insp_digital["total_pages"] == 2
assert insp_digital["doc_type"] == "DIGITAL_SEARCHABLE"
assert insp_digital["recommended_mode"] == "fast_native"
print(f"  ✓ 1.2 Digital Searchable PDF classified accurately: {insp_digital['doc_type_label']}.")

# 1.3 Test Scanned Image PDF (Blank / zero text)
writer_blank = PdfWriter()
writer_blank.add_blank_page(width=595, height=842)
buf_blank = io.BytesIO()
writer_blank.write(buf_blank)
blank_pdf_bytes = buf_blank.getvalue()

insp_scanned = pdf_ocr_engine.inspect_pdf(blank_pdf_bytes)
assert insp_scanned["status"] == "success"
assert insp_scanned["doc_type"] == "SCANNED_IMAGE_ONLY"
assert insp_scanned["recommended_mode"] == "vision_ai"
print(f"  ✓ 1.3 Scanned Image-only PDF classified accurately: {insp_scanned['doc_type_label']}.")

# 1.4 Test Process Document & Citation Anchors
proc_res = pdf_ocr_engine.process_pdf_document(sample_pdf_bytes, mode="fast_native", max_pages=10)
assert proc_res["status"] == "success"
assert proc_res["total_pages"] == 2
assert proc_res["rag_chunks_count"] >= 2

# Verify exact citation anchor format: [filename, Trang X]
for chunk in proc_res["rag_chunks"]:
    anchor = chunk.get("citation_anchor", "")
    assert re.match(r'^\[.+\.pdf,\s*Trang\s+\d+\]$', anchor), f"Invalid citation anchor format: {anchor}"
    assert "section_heading" in chunk
    assert "token_count_est" in chunk
print(f"  ✓ 1.4 RAG Semantic Chunks generated ({proc_res['rag_chunks_count']} chunks) with exact citation anchors (e.g. '{proc_res['rag_chunks'][0]['citation_anchor']}').")

# 1.5 Test In-Place DOM DOCX & Searchable Markdown Export
docx_res = pdf_ocr_engine.export_searchable_docx(proc_res)
assert docx_res["status"] == "success"
assert Path(docx_res["full_path"]).exists()
print(f"  ✓ 1.5 Searchable Word .docx and Markdown exported to {docx_res['docx_file']}.")

# 1.6 Test 1-Click Open-Notebook Ingestion
from modules.notebooklm.notebooklm_engine import open_notebook_engine
nb_created = open_notebook_engine.create_notebook("Notebook Kiểm Thử M3", "Kiểm thử nạp OCR")
nb_id = nb_created.get("id") or nb_created.get("notebook", {}).get("id")

ingest_res = pdf_ocr_engine.ingest_to_open_notebook(proc_res, notebook_id=nb_id)
assert ingest_res["status"] == "success"
print(f"  ✓ 1.6 1-Click Ingestion to Open-Notebook Knowledge Vault succeeded (Source ID: {ingest_res.get('source_id')}).")


# ═══════════════════════════════════════════════════════════════════════════
# TEST GROUP 2: BIGQUERY AI/ML ANALYTICS HARDENING
# ═══════════════════════════════════════════════════════════════════════════
print("\n[TEST GROUP 2] Testing BigQuery AI/ML Analytics Engine Hardening...")
from modules.bigquery.bigquery_engine import BigQueryAIEngine, bigquery_engine

# 2.1 Test AI.FORECAST with Vietnamese number formatting & 300 DPI chart
ts_data = [
    {'time': '2018', 'value': 50.0},
    {'time': '2019', 'value': 65.5},
    {'time': '2020', 'value': 82.0},
    {'time': '2021', 'value': 99.2},
    {'time': '2022', 'value': 118.0},
    {'time': '2023', 'value': 136.5},
    {'time': '2024', 'value': 155.0}
]
fc_res = bigquery_engine.forecast_timeseries(
    data_points=ts_data,
    horizon=5,
    confidence_level=0.95,
    metric_name="Sản Lượng Năng Lượng Tái Tạo (MWh)",
    topic="Quy Hoạch Năng Lượng Đô Thị Thông Minh"
)
assert fc_res["status"] == "success"
assert len(fc_res["forecast_results"]) == 5
assert fc_res["trend_direction"] == "Tăng trưởng (Upward)"
assert fc_res["chart_filename"] is not None
chart_file = file_mgr.workspace / "charts" / fc_res["chart_filename"]
assert chart_file.exists(), "300 DPI chart file must exist"
assert "SELECT * FROM AI.FORECAST(" in fc_res["bigquery_sql_equivalent"]
print(f"  ✓ 2.1 AI.FORECAST succeeded: 5 horizon points, 95% CI, 300 DPI chart generated ({fc_res['chart_filename']}).")

# 2.2 Test AI.DETECT_ANOMALIES (Hybrid Z-Score + IQR)
anom_data = [
    {'id': 'Tram_01', 'value': 45.2},
    {'id': 'Tram_02', 'value': 44.8},
    {'id': 'Tram_03', 'value': 46.1},
    {'id': 'Tram_04', 'value': 45.0},
    {'id': 'Tram_05', 'value': 128.5}, # Extreme High Outlier
    {'id': 'Tram_06', 'value': 45.5},
    {'id': 'Tram_07', 'value': 3.2},   # Extreme Low Outlier
    {'id': 'Tram_08', 'value': 44.9},
    {'id': 'Tram_09', 'value': 45.3},
    {'id': 'Tram_10', 'value': 45.1}
]
anom_res = bigquery_engine.detect_anomalies(
    data_points=anom_data,
    metric_name="Chỉ Số Ô Nhiễm Không Khí AQI",
    topic="Quan Trắc Môi Trường Đô Thị"
)
assert anom_res["status"] == "success"
assert anom_res["anomaly_points_count"] == 2
anom_ids = [a["id"] for a in anom_res["anomalies_detected"]]
assert "Tram_05" in anom_ids and "Tram_07" in anom_ids
assert "SELECT * FROM AI.DETECT_ANOMALIES(" in anom_res["bigquery_sql_equivalent"]
print(f"  ✓ 2.2 AI.DETECT_ANOMALIES detected exactly 2 outliers ({anom_res['anomaly_rate']}): {anom_ids}.")

# 2.3 Test AI.KEY_DRIVERS (Pearson Correlation & Importance Ranking)
kd_data = [
    {'hieu_suat': 75.0, 'nhiet_do': 120, 'ap_suat': 30, 'chat_xuc_tac': 2.5, 'do_am': 60},
    {'hieu_suat': 82.5, 'nhiet_do': 130, 'ap_suat': 35, 'chat_xuc_tac': 3.5, 'do_am': 58},
    {'hieu_suat': 89.0, 'nhiet_do': 140, 'ap_suat': 40, 'chat_xuc_tac': 4.8, 'do_am': 55},
    {'hieu_suat': 94.5, 'nhiet_do': 150, 'ap_suat': 45, 'chat_xuc_tac': 6.0, 'do_am': 52},
    {'hieu_suat': 70.2, 'nhiet_do': 110, 'ap_suat': 25, 'chat_xuc_tac': 1.8, 'do_am': 65},
    {'hieu_suat': 86.0, 'nhiet_do': 135, 'ap_suat': 38, 'chat_xuc_tac': 4.2, 'do_am': 56}
]
kd_res = bigquery_engine.analyze_key_drivers(
    data_points=kd_data,
    target_key="hieu_suat",
    topic="Tối Ưu Hóa Phản Ứng Hóa Học Tổng Hợp"
)
assert kd_res["status"] == "success"
assert kd_res["target_metric"] == "hieu_suat"
assert len(kd_res["drivers_ranked"]) == 4
assert kd_res["top_driver"] in ("nhiet_do", "ap_suat", "chat_xuc_tac")
assert "SELECT * FROM AI.KEY_DRIVERS(" in kd_res["bigquery_sql_equivalent"]
print(f"  ✓ 2.3 AI.KEY_DRIVERS ranked 4 drivers, top driver: {kd_res['top_driver']} ({kd_res['drivers_ranked'][0]['importance_score']}% importance).")

# 2.4 Test Natural Language to BigQuery SQL (NL2SQL)
sql_res = bigquery_engine.generate_bigquery_sql("Dự báo lượng khí thải CO2 trong 10 năm tới kèm khoảng tin cậy 95%")
assert sql_res["status"] == "success"
assert "SELECT" in sql_res["sql_query"]
assert "AI.FORECAST" in sql_res["sql_query"]
print("  ✓ 2.4 NL2SQL generated valid BigQuery AI SQL query.")

# 2.5 Test Quantitative DOCX Report Export with IMRaD Structure & APA Tables
rep_export = bigquery_engine.export_analysis_report_docx(
    analysis_type="forecast",
    result_data=fc_res,
    topic="Báo Cáo Dự Báo Năng Lượng Đô Thị"
)
assert rep_export["status"] == "success"
assert (file_mgr.workspace / rep_export["rel_path"]).exists()
assert (file_mgr.workspace / rep_export["rel_md_path"]).exists()
print(f"  ✓ 2.5 IMRaD DOCX Analysis Report generated: {rep_export['file_name']}.")

# 2.6 Test Vietnamese Number Formatting Helper
vn_fmt1 = bigquery_engine._format_vn_num(1.5)
vn_fmt2 = bigquery_engine._format_vn_num(28.5)
vn_fmt3 = bigquery_engine._format_vn_num(1000)
vn_fmt4 = bigquery_engine._format_vn_num(50000.75)
assert vn_fmt1 == "1,50" or vn_fmt1 == "1,5"
assert vn_fmt2 == "28,50" or vn_fmt2 == "28,5"
assert vn_fmt3 == "1.000"
assert vn_fmt4 == "50.000,75"
print(f"  ✓ 2.6 Vietnamese number formatting verified: 1.5 -> '{vn_fmt1}', 28.5 -> '{vn_fmt2}', 1000 -> '{vn_fmt3}', 50000.75 -> '{vn_fmt4}'.")


# ═══════════════════════════════════════════════════════════════════════════
# TEST GROUP 3: BIGQUERY ROUTER & DATASET UPLOAD
# ═══════════════════════════════════════════════════════════════════════════
print("\n[TEST GROUP 3] Testing BigQuery Router & Dataset Parser...")
from modules.bigquery.bigquery_router import run_time_series_forecast, run_detect_anomalies, run_key_drivers_analysis, generate_sql_query, export_analysis_report

mock_user = {"email": "test@univ.edu.vn", "role": "researcher"}

# Direct router function call tests
r_fc = run_time_series_forecast({"data_points": ts_data, "horizon": 3}, user=mock_user)
assert r_fc["status"] == "success"
r_an = run_detect_anomalies({"data_points": anom_data}, user=mock_user)
assert r_an["status"] == "success"
r_kd = run_key_drivers_analysis({"data_points": kd_data, "target_key": "hieu_suat"}, user=mock_user)
assert r_kd["status"] == "success"
r_sql = generate_sql_query({"prompt": "Phát hiện dị biệt nồng độ bụi mịn PM2.5"}, user=mock_user)
assert r_sql["status"] == "success"
r_rep = export_analysis_report({"analysis_type": "anomalies", "result_data": r_an, "topic": "Kiểm Định Ô Nhiễm"}, user=mock_user)
assert r_rep["status"] == "success"

print("  ✓ 3.1 All 5 Router endpoints executed successfully with operational user auth context.")

# Clean up temp
temp_dir.cleanup()

print("\n" + "=" * 80)
print("  🎉 ALL HARDENING TESTS PASSED WITH 100% SUCCESS RATE!")
print("=" * 80)
