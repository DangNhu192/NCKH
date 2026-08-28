# test_server_load.py
"""
WEB SUPER v3.2 / v2.0 - Comprehensive E2E Test Suite for Server Endpoints, API Contracts & Concurrent Load.
Covers:
1. System Health & Static Root Endpoints (GET /api/health, GET /).
2. Workspace File Management Endpoints (GET /api/files, POST /api/files/save, GET /api/files/read, DELETE /api/files/delete).
3. BigQuery AI/ML Analytics Endpoints (POST /api/bigquery/forecast, /detect-anomalies, /key-drivers, /generate-sql).
4. PDF Document AI OCR Endpoints (POST /api/pdf-ocr/inspect, POST /api/pdf-ocr/process).
5. Authentication & Authorization Security Guards (JWT Token Generation, Validation, 401/403 Handling).
6. Input Validation & Fault Tolerance (400 Bad Request, 404 Not Found, 422 Unprocessable Entity).
7. High-Concurrency Load Simulation (Multi-Threaded Concurrent API Requests, Latency & Consistency Checks).
"""

import os
import io
import sys
import json
import time
import shutil
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from starlette.testclient import TestClient
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from server import app
from modules.shared.file_manager import file_mgr
from modules.auth.auth_service import create_jwt_token
from modules.auth.user_config_manager import ADMIN_EMAILS


class TestServerLoadAndAPIContracts(unittest.TestCase):
    """Hermetic, Isolated End-to-End Test Suite for Server Endpoints and Load Simulation."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_workspace = Path(self.temp_dir.name)

        # Redirect file_mgr workspace
        self.orig_workspace = file_mgr.workspace
        file_mgr.workspace = self.temp_workspace
        file_mgr.docs_dir = self.temp_workspace / "Tai_Lieu"
        file_mgr.drafts_dir = self.temp_workspace / "Ban_Thao"
        file_mgr.publish_dir = self.temp_workspace / "Xuat_Ban"
        file_mgr.docs_dir.mkdir(parents=True, exist_ok=True)
        file_mgr.drafts_dir.mkdir(parents=True, exist_ok=True)
        file_mgr.publish_dir.mkdir(parents=True, exist_ok=True)

        self.client = TestClient(app)

        # Generate a valid test Admin JWT authentication token
        admin_email = list(ADMIN_EMAILS)[0] if ADMIN_EMAILS else "admin@websuper.edu.vn"
        self.admin_user = {
            "email": admin_email,
            "name": "Lead AI Academic Architect",
            "role": "admin",
            "status": "active",
            "plan": "enterprise"
        }
        self.auth_token = create_jwt_token(self.admin_user)
        self.auth_headers = {"Authorization": f"Bearer {self.auth_token}"}

    def tearDown(self):
        file_mgr.workspace = self.orig_workspace
        file_mgr.docs_dir = self.orig_workspace / "Tai_Lieu"
        file_mgr.drafts_dir = self.orig_workspace / "Ban_Thao"
        file_mgr.publish_dir = self.orig_workspace / "Xuat_Ban"
        self.temp_dir.cleanup()

    # ── TEST 1: SYSTEM HEALTH & STATIC SPA ───────────────────────────────────

    def test_01_health_and_root_endpoints(self):
        """Verify GET /api/health and GET / return healthy status and HTML payload."""
        # 1. Health check
        res_health = self.client.get("/api/health")
        self.assertEqual(res_health.status_code, 200)
        data = res_health.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("WEB SUPER", data["service"])

        # 2. Root SPA endpoint
        res_root = self.client.get("/")
        self.assertEqual(res_root.status_code, 200)
        self.assertIn("text/html", res_root.headers.get("content-type", ""))

    # ── TEST 2: WORKSPACE FILE MANAGEMENT API ────────────────────────────────

    def test_02_workspace_file_lifecycle_api(self):
        """Verify full file lifecycle via Workspace Router: list, save, read, and delete."""
        # 1. Initial list should be empty or a list
        res_list_init = self.client.get("/api/files")
        self.assertEqual(res_list_init.status_code, 200)
        self.assertIsInstance(res_list_init.json(), list)

        # 2. Save a Markdown file
        save_payload = {
            "rel_path": "Ban_Thao/Khao_Sat_Moi_Truong_2026.md",
            "content": "# Báo Cáo Khảo Sát\n\nNồng độ FeS₂ đạt 28,5% và H₂SO₄ đạt 1,5 mg/L.",
            "file_format": "md",
            "topic": "Khảo Sát Môi Trường"
        }
        res_save = self.client.post("/api/files/save", json=save_payload)
        self.assertEqual(res_save.status_code, 200)
        save_data = res_save.json()
        self.assertTrue(save_data.get("success", False))

        # 3. Read back the saved file
        res_read = self.client.get("/api/files/read", params={"path": "Ban_Thao/Khao_Sat_Moi_Truong_2026.md"})
        self.assertEqual(res_read.status_code, 200)
        read_data = res_read.json()
        self.assertIn("28,5%", read_data["content"])

        # 4. List files with category filter
        res_list_drafts = self.client.get("/api/files", params={"category": "drafts"})
        self.assertEqual(res_list_drafts.status_code, 200)
        drafts = res_list_drafts.json()
        self.assertTrue(any("Khao_Sat_Moi_Truong_2026.md" in f.get("name", "") for f in drafts))

        # 5. Delete file
        res_del = self.client.delete("/api/files/delete", params={"path": "Ban_Thao/Khao_Sat_Moi_Truong_2026.md"})
        self.assertEqual(res_del.status_code, 200)
        self.assertTrue(res_del.json().get("success", False))

        # 6. Read deleted file -> 404
        res_read_after = self.client.get("/api/files/read", params={"path": "Ban_Thao/Khao_Sat_Moi_Truong_2026.md"})
        self.assertEqual(res_read_after.status_code, 404)

    # ── TEST 3: BIGQUERY AI/ML TIME-SERIES FORECAST API ──────────────────────

    def test_03_bigquery_forecast_endpoint(self):
        """Verify POST /api/bigquery/forecast computes 95% confidence intervals and returns forecast points."""
        history_points = [
            {"time": f"2025-{m:02d}", "value": 100 + m * 5.5 + (m % 2) * 2}
            for m in range(1, 13)
        ]
        payload = {
            "data_points": history_points,
            "time_key": "time",
            "value_key": "value",
            "horizon": 4,
            "confidence_level": 0.95,
            "metric_name": "Lượng Phát Thải CO₂",
            "topic": "Dự Báo Phát Thải Công Nghiệp"
        }

        res = self.client.post("/api/bigquery/forecast", json=payload, headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(len(data["forecast_results"]), 4)
        self.assertIn("trend_direction", data)
        self.assertIn("academic_interpretation", data)

        # Verify each forecast point has confidence bounds
        for pt in data["forecast_results"]:
            self.assertIn("forecast_value", pt)
            self.assertIn("lower_bound", pt)
            self.assertIn("upper_bound", pt)
            self.assertLessEqual(pt["lower_bound"], pt["forecast_value"])
            self.assertGreaterEqual(pt["upper_bound"], pt["forecast_value"])

    # ── TEST 4: BIGQUERY AI/ML ANOMALY DETECTION & KEY DRIVERS API ───────────

    def test_04_bigquery_anomalies_and_key_drivers(self):
        """Verify POST /api/bigquery/detect-anomalies and /key-drivers calculate robust metrics."""
        # 1. Anomaly Detection with deliberate spikes
        data_points = [{"id": f"s_{i}", "value": 50.0 + (i % 3)} for i in range(20)]
        data_points.append({"id": "s_spike", "value": 500.0})  # Extreme anomaly

        res_anomaly = self.client.post(
            "/api/bigquery/detect-anomalies",
            json={"data_points": data_points, "id_key": "id", "value_key": "value", "metric_name": "Nồng Độ Kim Loại"},
            headers=self.auth_headers
        )
        self.assertEqual(res_anomaly.status_code, 200)
        anom_data = res_anomaly.json()
        self.assertEqual(anom_data["status"], "success")
        self.assertGreaterEqual(anom_data["anomaly_points_count"], 1)
        self.assertGreaterEqual(len(anom_data["anomalies_detected"]), 1)
        spike_pt = [p for p in anom_data["anomalies_detected"] if p["id"] == "s_spike"][0]
        self.assertIn("Quá Cao", spike_pt["deviation_type"])

        # 2. Key Drivers Analysis (Pearson Correlation)
        kd_points = [
            {"target": 10 + i * 2, "temp": 20 + i * 1.5, "pressure": 100 - i * 0.5, "noise": (i % 4) * 3}
            for i in range(15)
        ]
        res_kd = self.client.post(
            "/api/bigquery/key-drivers",
            json={"data_points": kd_points, "target_key": "target", "feature_keys": ["temp", "pressure", "noise"]},
            headers=self.auth_headers
        )
        self.assertEqual(res_kd.status_code, 200)
        kd_data = res_kd.json()
        self.assertEqual(kd_data["status"], "success")
        self.assertGreaterEqual(len(kd_data["drivers_ranked"]), 3)
        # Temp should be the strongest positive driver
        top_driver = kd_data["drivers_ranked"][0]
        self.assertEqual(top_driver["driver_name"], "temp")
        self.assertGreater(top_driver["correlation_coefficient"], 0.9)

        # 3. BigQuery NL2SQL Generation
        res_sql = self.client.post(
            "/api/bigquery/generate-sql",
            json={
                "prompt": "Dự báo doanh thu 6 tháng tới và phát hiện dị biệt trong bảng sales_data",
                "table_name": "project.dataset.sales_data"
            },
            headers=self.auth_headers
        )
        self.assertEqual(res_sql.status_code, 200)
        sql_data = res_sql.json()
        self.assertEqual(sql_data["status"], "success")
        self.assertIn("SELECT", sql_data["sql_query"].upper())

    # ── TEST 5: PDF OCR REST API ENDPOINTS ───────────────────────────────────

    def test_05_pdf_ocr_api_inspect_and_process(self):
        """Verify /api/pdf-ocr/inspect and /process endpoints via Workspace Router."""
        pdf_path = self.temp_workspace / "Tai_Lieu" / "Digital_Api_Test.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(72, 750, "Bao Cao Nghien Cuu Khoa Hoc API Test")
        c.setFont("Helvetica", 11)
        c.drawString(72, 720, "Chi tieu FeS2 dat 28.5% va H2SO4 dat 1.5 mg/L.")
        c.showPage()
        c.save()

        # 1. Inspect endpoint (POST /api/pdf-ocr/inspect with rel_path)
        res_insp = self.client.post(
            "/api/pdf-ocr/inspect",
            json={"rel_path": "Tai_Lieu/Digital_Api_Test.pdf"},
            headers=self.auth_headers
        )
        self.assertEqual(res_insp.status_code, 200)
        insp_data = res_insp.json()
        self.assertEqual(insp_data["status"], "success")
        self.assertEqual(insp_data["doc_type"], "DIGITAL_SEARCHABLE")

        # 2. Process endpoint (POST /api/pdf-ocr/process)
        res_proc = self.client.post(
            "/api/pdf-ocr/process",
            json={"rel_path": "Tai_Lieu/Digital_Api_Test.pdf", "mode": "auto", "max_pages": 5},
            headers=self.auth_headers
        )
        self.assertEqual(res_proc.status_code, 200)
        proc_data = res_proc.json()
        self.assertEqual(proc_data["status"], "success")
        self.assertGreater(proc_data["rag_chunks_count"], 0)

    # ── TEST 6: AUTHENTICATION GUARDS & SECURITY ─────────────────────────────

    def test_06_auth_guards_unauthorized_access(self):
        """Verify endpoints requiring authentication reject unauthenticated or malformed requests."""
        # Unauthenticated request to /api/bigquery/forecast
        res_unauth = self.client.post("/api/bigquery/forecast", json={"data_points": []})
        self.assertIn(res_unauth.status_code, [401, 403])

        # Malformed Authorization header
        res_bad_auth = self.client.post(
            "/api/bigquery/forecast",
            json={"data_points": []},
            headers={"Authorization": "Bearer INVALID_CORRUPT_TOKEN_XYZ"}
        )
        self.assertIn(res_bad_auth.status_code, [401, 403])

    # ── TEST 7: ERROR RESILIENCE & INPUT VALIDATION ──────────────────────────

    def test_07_error_resilience_and_validation(self):
        """Verify API returns structured HTTP error codes without unhandled exceptions."""
        # Missing required parameter in save file
        res_bad_save = self.client.post("/api/files/save", json={})
        self.assertEqual(res_bad_save.status_code, 400)

        # Missing target_key in key-drivers
        res_bad_kd = self.client.post(
            "/api/bigquery/key-drivers",
            json={"data_points": [{"a": 1}]},
            headers=self.auth_headers
        )
        self.assertEqual(res_bad_kd.status_code, 400)

        # Delete non-existent file
        res_del_missing = self.client.delete("/api/files/delete", params={"path": "non_existent_file.xyz"})
        self.assertEqual(res_del_missing.status_code, 404)

    # ── TEST 8: CONCURRENT LOAD SIMULATION ───────────────────────────────────

    def test_08_concurrent_api_load_simulation(self):
        """Simulate concurrent multi-threaded requests to verify throughput and thread-safety."""
        concurrency = 15
        urls = [
            ("/api/health", "GET", None, {}),
            ("/api/files", "GET", None, {}),
            ("/api/bigquery/forecast", "POST", {
                "data_points": [{"time": f"2026-{m:02d}", "value": 50 + m * 2} for m in range(1, 7)],
                "horizon": 2,
                "metric_name": "Tải Đồng Thời"
            }, self.auth_headers)
        ]

        def send_request(req_info):
            path, method, payload, headers = req_info
            t_start = time.time()
            if method == "GET":
                r = self.client.get(path, headers=headers)
            else:
                r = self.client.post(path, json=payload, headers=headers)
            t_elapsed = time.time() - t_start
            return r.status_code, t_elapsed

        requests_to_run = [urls[i % len(urls)] for i in range(concurrency)]

        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(send_request, req) for req in requests_to_run]
            for f in as_completed(futures):
                results.append(f.result())

        self.assertEqual(len(results), concurrency)
        status_codes = [r[0] for r in results]
        latencies = [r[1] for r in results]

        # 100% of concurrent requests must succeed
        self.assertTrue(all(code == 200 for code in status_codes))
        avg_latency = sum(latencies) / len(latencies)
        self.assertLess(avg_latency, 1.0)  # Average latency under 1 second


def run_tests():
    """Test runner with formatted console output."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestServerLoadAndAPIContracts)
    runner = unittest.TextTestRunner(verbosity=2)
    start_time = time.time()
    result = runner.run(suite)
    elapsed = round(time.time() - start_time, 2)

    print("\n" + "=" * 70)
    print(f"📊 SERVER LOAD & API CONTRACTS TEST SUITE SUMMARY:")
    print(f"   Total Tests Run: {result.testsRun}")
    print(f"   Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Execution Time: {elapsed}s")
    print("=" * 70)

    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
