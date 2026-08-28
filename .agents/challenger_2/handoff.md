# 5-Component Handoff Report — challenger_2

**Role:** Empirical Stress-Testing Specialist for PDF AI OCR & BigQuery AI/ML Analytics  
**Date:** 2026-08-26  
**Verdict:** `REQUEST_CHANGES`

---

## 1. Observation

An empirical adversarial test suite consisting of 17 stress tests (`test_adversarial_ocr_bq_rag.py`) was executed in an isolated hermetic environment via Python 3.11:

```powershell
& "H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\.venv\Scripts\python.exe" test_adversarial_ocr_bq_rag.py
```

### Test Suite Execution Output:
- **Total Stress Tests Run:** 17
- **Passed:** 15
- **Failures:** 2
- **Errors:** 0
- **Execution Time:** 33.99s

```
======================================================================
FAIL: test_11_bq_forecast_timestamp_formatting_and_vn_numbers (__main__.TestAdversarialOcrBqRag.test_11_bq_forecast_timestamp_formatting_and_vn_numbers)
Adversarial Test: Quarters (Q1/2026), Months (T05/2026), Vietnamese comma numbers ('28,5%').
----------------------------------------------------------------------
Traceback (most recent call last):
  File "H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\test_adversarial_ocr_bq_rag.py", line 412, in test_11_bq_forecast_timestamp_formatting_and_vn_numbers
    self.assertEqual(res_m["forecast_results"][0]["time"], "T01/2026")
AssertionError: 'T12/2025 (+1)' != 'T01/2026'
- T12/2025 (+1)
+ T01/2026

======================================================================
FAIL: test_12_bq_anomaly_detection_boundaries (__main__.TestAdversarialOcrBqRag.test_12_bq_anomaly_detection_boundaries)
Adversarial Test: Small sample sizes (<4 error, =4 success), zero variance, multimodal.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\test_adversarial_ocr_bq_rag.py", line 447, in test_12_bq_anomaly_detection_boundaries
    self.assertGreaterEqual(res_4["anomaly_points_count"], 1)
AssertionError: 0 not greater than or equal to 1
```

### Detailed Observations by Subsystem:

#### Subsystem A: PDF AI Document OCR (`modules/shared/pdf_ocr_engine.py`) — PASSED (7/7)
1. **Corrupted / Invalid PDFs (`test_01`):** Truncated PDF streams, broken headers, and random binary byte sequences are caught gracefully at line 120 (`pypdf.PdfReader`) and line 179 (`except Exception as e`), returning structured `{"status": "error", "message": ...}` without uncaught crashes.
2. **Empty & Blank PDFs (`test_02`):** 0-byte files return explicit error at line 115 (`len(pdf_bytes) < 10`). Completely blank 3-page PDFs are accurately triaged as `SCANNED_IMAGE_ONLY` and processed into 3 RAG chunks.
3. **Single-Page Digital vs Scanned (`test_03`):** Digital pages with chemical formulas (`FeS₂`, `H₂SO₄`) and LaTeX formulas are triaged as `DIGITAL_SEARCHABLE` with `fast_native` mode.
4. **Multi-Page Large Documents (`test_04`):** 15-page PDFs with `max_pages=5` boundary truncation accurately process 5 pages, generating page breaks `<!-- PAGE_BREAK: X -->` and `## [Trang X]`.
5. **Non-ASCII & Vietnamese Unicode Filenames (`test_05`):** Complex filenames with diacritics, spaces, brackets, chemical formulas (`Báo cáo ĐTM & Ô nhiễm_FeS₂_H₂SO₄_NH₄⁺_v3.2 [2026] (Đo đạc #01).pdf`) are sanitized at line 501 (`re.sub(r'[^\w\-]', '_', ...)`) producing persistent `.md`, `.json`, and `.docx` artifacts.
6. **Hybrid Multi-tier Scenarios (`test_06`):** 5-page mixed documents (Digital, Scanned, Degraded, Blank, Digital Table) are classified as `HYBRID_DEGRADED` (auto mode) with exact citation anchors `[filename, Trang X]`.
7. **Malformed Table Extraction (`test_07`):** Ragged Markdown tables with missing or extra columns are safely padded to header length at lines 347-348.

#### Subsystem B: BigQuery AI/ML Analytics (`modules/bigquery/bigquery_engine.py`) — FAILED (2/8)
1. **Short History Time-Series Forecasting (`test_08`):** 0, 1, and 2 data points return clean error messages; boundary condition $n = 3$ succeeds with accurate slope and forecast.
2. **Extreme Outliers & Zero Variance (`test_09`, `test_10`):** 10,000,000x spikes and zero-variance/constant data (e.g. all 42.0 or all 0.0) do not cause `ZeroDivisionError` or NaN outputs due to fallback `residual_std` at lines 182-183.
3. **Defect 1 — Vietnamese Month Label Parsing (`test_11`):**
   - In `bigquery_engine.py:700`:
     ```python
     m_m = re.match(r'^(?:(\d{1,2})[/_-](\d{4})|(\d{4})[/_-](\d{1,2}))$', last_label)
     ```
   - When given `T12/2025` or `Tháng 12/2025` (standard Vietnamese month format), the regex fails to match because it does not accept the optional `T` or `Tháng ` prefix. Consequently, it falls back to line 709 (`f"{last_label} (+{step})"`) generating `'T12/2025 (+1)'` instead of rolling over to `'T01/2026'`.
4. **Defect 2 — Small Sample Anomaly Blindness (`test_12`):**
   - In `bigquery_engine.py:285-322`:
     ```python
     if not data_points or len(data_points) < 4:
         return {"status": "error", "message": "Cần ít nhất 4 điểm dữ liệu để phát hiện điểm dị biệt."}
     ...
     z_score = abs(v - mean_val) / std_val
     is_anomaly = (v < lower_threshold) or (v > upper_threshold) or (z_score > 2.5)
     ```
   - For a 4-point dataset `[9.8, 10.0, 10.2, 500.0]`, $q_3 = \text{sorted\_v}[\text{int}(4 \times 0.75)] = \text{sorted\_v}[3] = 500.0$.
   - Thus $\text{IQR} = 500.0 - 10.0 = 490.0$, making $\text{upper\_threshold} = 500.0 + 1.5 \times 490.0 = 1235.0 > 500.0$.
   - The sample $z$-score of $500.0$ is $z = \frac{500.0 - 132.5}{212.17} = 1.732 < 2.5$.
   - By Cauchy-Schwarz inequality, for ANY dataset of size $n$, the maximum possible sample $z$-score for any data point is mathematically bounded by:
     $$|z_i| \le \sqrt{n-1}$$
   - For $n=4$: $|z| \le \sqrt{3} \approx 1.732 < 2.5$.
   - For $n=5$: $|z| \le \sqrt{4} = 2.000 < 2.5$.
   - For $n=6$: $|z| \le \sqrt{5} \approx 2.236 < 2.5$.
   - For $n=7$: $|z| \le \sqrt{6} \approx 2.449 < 2.5$.
   - Therefore, with fixed threshold $z > 2.5$, it is mathematically impossible to detect ANY outlier for sample sizes $n \le 7$.
5. **Key Drivers Analysis (`test_14`, `test_15`):** Collinear features ($r=1.0$), negative correlations ($r=-1.0$), and constant features ($s=0$) are correctly computed without zero division at lines 418, 424, and 428.

#### Subsystem C: Open-Notebook RAG Knowledge Vault (`modules/notebooklm/notebooklm_engine.py`) — PASSED (2/2)
1. **Adversarial Queries (`test_16`):** Empty strings `""`, whitespace `" \t\n "`, and punctuation spam `??? !!! @@@` return `[]` gracefully. Non-accented/misspelled terms match via $N$-gram character cosine similarity ($N=3, 4$). Prompt injection payloads (5,000+ chars) execute safely without system prompt leakage.
2. **Grounded Q&A & Transformations (`test_17`):** Sparse notebooks with 1 brief source generate full APA 7th citations `[Author, Year]` and render all 5 signature transformations plus the 7-column Literature Review Matrix `.docx`.

---

## 2. Logic Chain

1. **Premise 1:** The mission requires stress-testing PDF OCR triage, BigQuery AI time-series forecasting, anomaly detection, key drivers, and Open-Notebook RAG search under hostile edge cases.
2. **Premise 2 (Observation 1 & Subsystem A):** PDF OCR triage, structure extraction, Word DOM export, and Open-Notebook ingestion pass 100% of adversarial edge cases.
3. **Premise 3 (Observation 1 & Subsystem C):** Open-Notebook RAG hybrid retrieval, grounded Q&A, and transformations pass 100% of noisy/misspelled/adversarial queries.
4. **Premise 4 (Observation 1 & Subsystem B - Defect 1):** In `modules/bigquery/bigquery_engine.py:700`, `_generate_next_time_label` uses `re.match(r'^(?:(\d{1,2})[/_-](\d{4})|(\d{4})[/_-](\d{1,2}))$', last_label)`, which omits the `T` or `Tháng ` prefix. When input timestamps follow the standard Vietnamese format `T12/2025` (which `_generate_next_time_label` itself emits at line 707 as `T{new_m:02d}/{new_y}`), subsequent horizons produce `'T12/2025 (+1)'` rather than `'T01/2026'`.
5. **Premise 5 (Observation 1 & Subsystem B - Defect 2):** In `modules/bigquery/bigquery_engine.py:285-322`, `detect_anomalies` permits minimum sample size $n=4$, but applies a fixed threshold $z > 2.5$. Because the sample $z$-score is strictly bounded by $|z| \le \sqrt{n-1}$, for $n \in [4, 7]$ the maximum possible $z$-score is $\sqrt{6} \approx 2.449 < 2.5$. Combined with discrete quartile indexing where $q_3 = x_{(n)}$, outlier detection fails completely for $n < 8$.
6. **Deductive Conclusion:** The system is functionally strong and highly resilient in PDF OCR and Open-Notebook RAG, but contains 2 critical algorithmic flaws in `bigquery_engine.py`. Thus, `REQUEST_CHANGES` is required.

---

## 3. Caveats

1. **Remote Cloud API / BigQuery Live Connection:** Tests were executed against local BigQuery AI/ML algorithmic representations and fallback query generators; actual Google Cloud BigQuery quota/IAM permissions were not tested against a live GCP project.
2. **Vision AI Fallback in Hermetic Mode:** Gemini Vision AI tests operated using mock/heuristic fallback paths in isolated CI environment where external Gemini API keys are omitted.

---

## 4. Conclusion

**Verdict: `REQUEST_CHANGES`**

### Required Actionable Remediations:

1. **Fix Vietnamese Month Regex in `modules/bigquery/bigquery_engine.py:700`:**
   - Update regex from:
     ```python
     m_m = re.match(r'^(?:(\d{1,2})[/_-](\d{4})|(\d{4})[/_-](\d{1,2}))$', last_label)
     ```
     to:
     ```python
     m_m = re.match(r'^(?:(?:T|Tháng\s*)?(\d{1,2})[/_-](\d{4})|(\d{4})[/_-](?:T|Tháng\s*)?(\d{1,2}))$', last_label, re.I)
     ```
2. **Fix Small-Sample Outlier Detection in `modules/bigquery/bigquery_engine.py`:**
   - Either adjust the minimum sample size constraint from $n \ge 4$ to $n \ge 8$:
     ```python
     if not data_points or len(data_points) < 8:
         return {"status": "error", "message": "Cần ít nhất 8 điểm dữ liệu để phát hiện điểm dị biệt theo chuẩn thống kê."}
     ```
   - OR adopt an adaptive Z-score threshold for small samples:
     ```python
     adaptive_z_thresh = min(2.5, 0.8 * math.sqrt(n - 1)) if n > 3 else 2.5
     is_anomaly = (v < lower_threshold) or (v > upper_threshold) or (z_score >= adaptive_z_thresh)
     ```
     along with continuous quartile interpolation or Dixon's Q test for $n \in [4, 7]$.

---

## 5. Verification Method

To independently verify the defects and validate future fixes:

1. **Run the Adversarial Test Suite:**
   ```powershell
   & "H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\.venv\Scripts\python.exe" test_adversarial_ocr_bq_rag.py
   ```
2. **Inspect Test Outputs:**
   - `test_11_bq_forecast_timestamp_formatting_and_vn_numbers` will pass when `T12/2025` increments to `T01/2026`.
   - `test_12_bq_anomaly_detection_boundaries` will pass when small-sample outliers are either detected or rejected with a clean minimum sample size error ($n \ge 8$).
3. **Invalidation Condition:**
   - If both tests exit with code 0 (`Ran 17 tests ... OK`), the findings are invalidated and the system can be upgraded to `APPROVE`.
