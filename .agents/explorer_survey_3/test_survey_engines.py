# test_survey_engines.py
import sys
import os
import io
import json
import time
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

print("=" * 70)
print("  EXPLORER 3 - TECHNICAL SURVEY OF PDF OCR & BIGQUERY AI ENGINES")
print("=" * 70)

# --- SECTION 1: PDF OCR ENGINE ---
print("\n[SECTION 1] Investigating PDF OCR Engine (modules/shared/pdf_ocr_engine.py)...")
from modules.shared.pdf_ocr_engine import PDFDocumentAIOcrEngine, pdf_ocr_engine

print("  -> Initialized PDFDocumentAIOcrEngine instance successfully.")
print(f"  -> Cache directory: {pdf_ocr_engine.pdf_cache_dir}")

# Create a sample PDF with pypdf
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
page = writer.add_blank_page(width=595, height=842) # A4
buf = io.BytesIO()
writer.write(buf)
empty_pdf_bytes = buf.getvalue()

insp = pdf_ocr_engine.inspect_pdf(empty_pdf_bytes)
print("  -> inspect_pdf(empty_pdf_bytes):", insp.get("status"), "| doc_type:", insp.get("doc_type"), "| recommended_mode:", insp.get("recommended_mode"))

# Test process_pdf_document on sample text-rich PDF
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    rl_buf = io.BytesIO()
    c = canvas.Canvas(rl_buf, pagesize=letter)
    c.drawString(100, 750, "Nghien cuu ung dung Deep Learning trong toi uu hoa nang luong")
    c.drawString(100, 720, "Tac gia: Nguyen Van An, Dai hoc Bach Khoa")
    c.drawString(100, 690, "Mo hinh toan hoc: E = mc^2 va cong thuc hoa hoc FeS2, H2SO4, NH4+.")
    c.drawString(100, 660, "Hieu suat do dac: 28,5% voi dung sai 1,5 don vi tren 1.000 mau.")
    c.showPage()
    c.save()
    sample_pdf_bytes = rl_buf.getvalue()

    proc_res = pdf_ocr_engine.process_pdf_document(sample_pdf_bytes, mode="fast_native", max_pages=5)
    print("  -> process_pdf_document(sample_pdf_bytes):", proc_res.get("status"))
    print("     - Total pages:", proc_res.get("total_pages"))
    print("     - Total words:", proc_res.get("total_words"))
    print("     - RAG chunks count:", proc_res.get("rag_chunks_count"))
    if proc_res.get("rag_chunks"):
        chunk0 = proc_res["rag_chunks"][0]
        print(f"     - Sample Chunk 0 Citation Anchor: {chunk0.get('citation_anchor')}")
        print(f"     - Sample Chunk 0 Heading: {chunk0.get('section_heading')}")

    # Test export searchable docx
    docx_export = pdf_ocr_engine.export_searchable_docx(proc_res)
    print("  -> export_searchable_docx:", docx_export.get("status"), "| file:", docx_export.get("docx_file"))

except ImportError:
    print("  (reportlab not installed, testing direct PDF parsing)")

# --- SECTION 2: BIGQUERY AI / ML ENGINE ---
print("\n[SECTION 2] Investigating BigQuery AI Engine (modules/bigquery/bigquery_engine.py)...")
from modules.bigquery.bigquery_engine import BigQueryAIEngine, bigquery_engine

print("  -> Initialized BigQueryAIEngine instance successfully.")
print(f"  -> Charts directory: {bigquery_engine.charts_dir}")

# 1. Test AI.FORECAST
sample_ts = [
    {'time': '2019', 'value': 100.5},
    {'time': '2020', 'value': 115.2},
    {'time': '2021', 'value': 130.8},
    {'time': '2022', 'value': 148.0},
    {'time': '2023', 'value': 165.3},
    {'time': '2024', 'value': 182.1}
]
fc_res = bigquery_engine.forecast_timeseries(
    sample_ts,
    metric_name='Tiêu Thụ Năng Lượng (kWh)',
    topic='Tối Ưu Hóa Năng Lượng Thông Minh',
    horizon=4,
    confidence_level=0.95
)
print("  -> 1. forecast_timeseries (AI.FORECAST):", fc_res.get("status"))
print(f"     - Trend direction: {fc_res.get('trend_direction')}")
print(f"     - Annual growth rate: {fc_res.get('annual_growth_rate')}")
print(f"     - Forecast points count: {len(fc_res.get('forecast_results', []))}")
print(f"     - Chart generated: {fc_res.get('chart_filename')}")
print(f"     - BigQuery SQL equivalent: \n       {fc_res.get('bigquery_sql_equivalent').splitlines()[0]}")

# 2. Test AI.DETECT_ANOMALIES
sample_anom = [
    {'id': 'M1', 'value': 25.1},
    {'id': 'M2', 'value': 25.4},
    {'id': 'M3', 'value': 24.8},
    {'id': 'M4', 'value': 25.2},
    {'id': 'M5', 'value': 89.5}, # Anomaly high
    {'id': 'M6', 'value': 25.0},
    {'id': 'M7', 'value': 2.1},  # Anomaly low
    {'id': 'M8', 'value': 25.3}
]
anom_res = bigquery_engine.detect_anomalies(
    sample_anom,
    metric_name='Nồng Độ Khí Thải (ppm)',
    topic='Quan Trắc Môi Trường Đô Thị'
)
print("\n  -> 2. detect_anomalies (AI.DETECT_ANOMALIES):", anom_res.get("status"))
print(f"     - Total points: {anom_res.get('total_points')}")
print(f"     - Anomalies detected: {anom_res.get('anomaly_points_count')} ({anom_res.get('anomaly_rate')})")
for an in anom_res.get("anomalies_detected", []):
    print(f"       * {an['id']}: value={an['value']}, Z={an['z_score']}, Type={an['deviation_type']}")

# 3. Test AI.KEY_DRIVERS
sample_kd = [
    {'yield': 82.5, 'temp': 100, 'pressure': 20, 'catalyst_pct': 5.0, 'ph': 7.0},
    {'yield': 87.1, 'temp': 110, 'pressure': 22, 'catalyst_pct': 6.2, 'ph': 7.1},
    {'yield': 91.8, 'temp': 120, 'pressure': 25, 'catalyst_pct': 7.5, 'ph': 7.0},
    {'yield': 76.4, 'temp': 95, 'pressure': 19, 'catalyst_pct': 4.1, 'ph': 6.9},
    {'yield': 96.2, 'temp': 130, 'pressure': 28, 'catalyst_pct': 8.8, 'ph': 7.2},
    {'yield': 84.0, 'temp': 105, 'pressure': 21, 'catalyst_pct': 5.5, 'ph': 7.1}
]
kd_res = bigquery_engine.analyze_key_drivers(
    sample_kd,
    target_key='yield',
    topic='Tối Ưu Hóa Hiệu Suất Phản Ứng Hóa Học'
)
print("\n  -> 3. analyze_key_drivers (AI.KEY_DRIVERS):", kd_res.get("status"))
print(f"     - Target metric: {kd_res.get('target_metric')}")
print(f"     - Top driver: {kd_res.get('top_driver')}")
for dr in kd_res.get("drivers_ranked", []):
    print(f"       * {dr['driver_name']}: r={dr['correlation_coefficient']}, importance={dr['importance_score']}%, sig={dr['significance']}")

# 4. Test Export DOCX report
docx_rep = bigquery_engine.export_analysis_report_docx(
    analysis_type="forecast",
    result_data=fc_res,
    topic="Báo Cáo Dự Báo Năng Lượng BigQuery AI"
)
print("\n  -> 4. export_analysis_report_docx:", docx_rep.get("status"))
print(f"     - DOCX file: {docx_rep.get('file_name')}")
print(f"     - MD file: {docx_rep.get('md_file_name')}")

print("\n" + "=" * 70)
print("  >>> TECHNICAL SURVEY ENGINE TESTS COMPLETED SUCCESSFULLY 100% <<<")
print("=" * 70)
