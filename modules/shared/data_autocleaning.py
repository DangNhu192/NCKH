"""
Data Autocleaning & Profiling Service (modules/shared/data_autocleaning.py)
--------------------------------------------------------------------------
Tự động làm sạch, kiểm định chất lượng số liệu khoa học, phát hiện ngoại lai (outliers),
chuẩn hóa đơn vị đo lường (SI/Academic Units) và định dạng số thập phân tiếng Việt
(Quy tắc Bất biến số 3: Dấu phẩy cho số thập phân '1,5', dấu chấm cho hàng nghìn '1.000').
"""

import re
from typing import Any, Dict, List, Optional, Tuple, Union


class ScientificDataCleaner:
    """Bộ xử lý làm sạch, chuẩn hóa và kiểm định số liệu khoa học thực chứng."""

    # Quy chuẩn giới hạn khoa học hợp lý (Boundary sanity checks)
    PHYSICAL_BOUNDS = {
        "ph": (0.0, 14.0),
        "percentage": (0.0, 100.0),
        "efficiency": (0.0, 100.0),
        "recovery": (0.0, 100.0),
        "q_max": (0.0, 5000.0),      # mg/g (dung lượng hấp phụ cực đại thông thường)
        "s_bet": (0.0, 4000.0),      # m2/g (diện tích bề mặt riêng)
        "cod": (0.0, 100000.0),      # mg/L
        "bod": (0.0, 50000.0),       # mg/L
        "cec": (0.0, 150.0),         # cmol/kg
        "temperature": (-50.0, 1500.0) # độ C
    }

    # Đơn vị đo lường khoa học chuẩn hóa
    UNIT_MAPPINGS = {
        r"mg[./\s]*g[-1]?|mg\s*g\^-1": "mg/g",
        r"m[2²][./\s]*g[-1]?|m\^2\s*g\^-1": "m²/g",
        r"mg[./\s]*[lL][-1]?|mg\s*[lL]\^-1": "mg/L",
        r"g[./\s]*[kK]g[-1]?|g\s*[kK]g\^-1": "g/kg",
        r"meq/100g|cmol\(\+\)/kg": "cmol/kg",
        r"ppm|parts\s*per\s*million": "ppm",
        r"ppb|parts\s*per\s*billion": "ppb",
        r"ug/[lL]|µg/[lL]": "µg/L",
        r"ng/[lL]": "ng/L",
        r"tan\s*CO2e|t\s*CO2e|tấn\s*CO2e": "tấn CO₂e"
    }

    @staticmethod
    def format_vietnamese_number(val: Union[float, int, str], decimal_places: Optional[int] = None) -> str:
        """
        Chuẩn hóa số theo phong cách tiếng Việt:
        - Dấu phẩy ngăn cách phần thập phân: 1.5 -> '1,5'
        - Dấu chấm ngăn cách hàng nghìn: 10000 -> '10.000'
        """
        if val is None or val == "":
            return ""
        if isinstance(val, str):
            val_clean = val.strip().replace(" ", "")
            # Nếu chuỗi có định dạng số kiểu Anh như '1,234.56'
            if re.match(r"^-?\d{1,3}(,\d{3})+(\.\d+)?$", val_clean):
                val_clean = val_clean.replace(",", "")
                try:
                    val = float(val_clean)
                except ValueError:
                    return val
            # Nếu chuỗi có dấu chấm thập phân đơn giản '12.34'
            elif re.match(r"^-?\d+\.\d+$", val_clean):
                try:
                    val = float(val_clean)
                except ValueError:
                    return val
            # Nếu là số nguyên '1234'
            elif re.match(r"^-?\d+$", val_clean):
                try:
                    val = int(val_clean)
                except ValueError:
                    return val
            else:
                # Đã là text hoặc chuỗi phức hợp, thay thế dấu chấm thập phân nội tại
                # ví dụ: '25.4%' -> '25,4%'
                return re.sub(r"(\d+)\.(\d+)", r"\1,\2", val)

        if isinstance(val, (int, float)):
            if decimal_places is not None:
                formatted = f"{val:,.{decimal_places}f}"
            else:
                if isinstance(val, int) or val.is_integer():
                    formatted = f"{int(val):,}"
                else:
                    formatted = f"{val:,}"
            # Đổi định dạng chuẩn quốc tế (comma thousand, dot decimal) sang chuẩn tiếng Việt
            # 1,234,567.89 -> 1.234.567,89
            parts = formatted.split(".")
            integer_part = parts[0].replace(",", ".")
            if len(parts) > 1:
                return f"{integer_part},{parts[1]}"
            return integer_part

        return str(val)

    @classmethod
    def clean_scientific_text(cls, text: str) -> str:
        """
        Làm sạch và chuẩn hóa các ký hiệu, số liệu và đơn vị đo trong một đoạn văn học thuật:
        - Chuẩn hóa dấu phẩy số thập phân
        - Chuẩn hóa đơn vị đo
        - Chuẩn hóa các ion/hóa chất thường gặp
        """
        if not text:
            return ""

        res = text

        # 1. Chuẩn hóa đơn vị đo
        for pattern, replacement in cls.UNIT_MAPPINGS.items():
            res = re.sub(pattern, replacement, res, flags=re.IGNORECASE)

        # 2. Chuẩn hóa số thập phân kèm đơn vị hoặc phần trăm (ví dụ: '12.5%' -> '12,5%', '3.4 mg/g' -> '3,4 mg/g')
        res = re.sub(r"(?<=\d)\.(?=\d)", ",", res)

        # 3. Chuẩn hóa công thức hóa học / ion
        chem_replacements = {
            r"\bFeS2\b": "FeS₂",
            r"\bH2SO4\b": "H₂SO₄",
            r"\bNH4\+(?!\w)": "NH₄⁺",
            r"\bNO3\-(?!\w)": "NO₃⁻",
            r"\bAl3\+(?!\w)": "Al³⁺",
            r"\bFe2\+(?!\w)": "Fe²⁺",
            r"\bFe3\+(?!\w)": "Fe³⁺",
            r"\bCO2\b": "CO₂",
            r"\bCH4\b": "CH₄",
            r"\bN2O\b": "N₂O",
            r"\bSO4\s*2\-(?!\w)": "SO₄²⁻",
            r"\bPO4\s*3\-(?!\w)": "PO₄³⁻",
            r"\bBOD5\b": "BOD₅",
            r"\bCaCO3\b": "CaCO₃"
        }
        for pat, rep in chem_replacements.items():
            res = re.sub(pat, rep, res)

        return res

    @classmethod
    def detect_and_fix_outliers(
        cls,
        metric_name: str,
        value: float
    ) -> Tuple[bool, float, Optional[str]]:
        """
        Phát hiện số liệu bất thường dựa trên quy luật khoa học tự nhiên.
        Trả về: (is_outlier, cleaned_value, alert_message)
        """
        metric_lower = metric_name.lower().strip()
        matched_bound_key = None

        for key in cls.PHYSICAL_BOUNDS:
            if key in metric_lower:
                matched_bound_key = key
                break

        if not matched_bound_key:
            return False, value, None

        min_val, max_val = cls.PHYSICAL_BOUNDS[matched_bound_key]

        if value < min_val:
            # Giá trị âm bất hợp lý (ví dụ: COD < 0 hoặc dung lượng hấp phụ < 0)
            return True, min_val, f"Số liệu '{metric_name}' ({value}) nhỏ hơn ngưỡng vật lý cho phép ({min_val}). Tự động điều chỉnh về {min_val}."
        elif value > max_val:
            # Vượt quá trần thực tế (ví dụ: hiệu suất > 100%)
            if matched_bound_key in ["percentage", "efficiency", "recovery"]:
                return True, 100.0, f"Hiệu suất '{metric_name}' ({value}%) vượt quá 100%. Tự động trần hóa về 100%."
            return True, max_val, f"Số liệu '{metric_name}' ({value}) vượt ngưỡng tối đa thông thường ({max_val}). Cảnh báo dị biệt."

        return False, value, None

    @classmethod
    def clean_evidence_matrix_rows(cls, rows: List[List[str]]) -> List[List[str]]:
        """
        Làm sạch toàn bộ bảng Ma trận đối soát thực chứng 6 cột (File B):
        - Cột 1: STT
        - Cột 2: Luận điểm
        - Cột 3: Tác giả & Năm
        - Cột 4: Tệp gốc
        - Cột 5: Trích đoạn nguyên văn
        - Cột 6: Bản dịch & Trang
        """
        cleaned_rows = []
        garbage_patterns = [r"^(null|none|n/a|undefined|---|\s*)$"]

        for row in rows:
            if not row or len(row) < 6:
                continue
            cleaned_row = []
            for col_idx, cell in enumerate(row):
                cell_str = str(cell or "").strip()
                # Kiểm tra rác
                if any(re.match(p, cell_str, re.IGNORECASE) for p in garbage_patterns) and col_idx > 0:
                    cell_str = "Chưa có dữ liệu" if col_idx != 0 else "1"

                # Áp dụng chuẩn hóa văn phong và số liệu
                if col_idx in [1, 4, 5]: # Luận điểm, trích đoạn, diễn giải
                    cell_str = cls.clean_scientific_text(cell_str)

                cleaned_row.append(cell_str)

            cleaned_rows.append(cleaned_row)

        return cleaned_rows

    @classmethod
    def profile_and_clean_dataset(cls, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Thẩm định dữ liệu (Profiling) và làm sạch tự động tập bản ghi dữ liệu thực nghiệm:
        - Thống kê null rate, distinct count, outlier count
        - Tự động chuẩn hóa chuỗi và số liệu
        """
        if not records:
            return {
                "total_records": 0,
                "null_rate": 0.0,
                "anomalies_detected": 0,
                "cleaned_records": [],
                "field_profiles": {}
            }

        total_records = len(records)
        fields = list(records[0].keys())
        field_profiles = {f: {"null_count": 0, "type": "unknown", "outliers": 0} for f in fields}
        cleaned_records = []
        total_anomalies = 0

        for r in records:
            cleaned_r = {}
            for f in fields:
                val = r.get(f)
                if val is None or val == "" or str(val).lower() in ["null", "none", "n/a"]:
                    field_profiles[f]["null_count"] += 1
                    cleaned_r[f] = None
                    continue

                # Nhận diện số
                if isinstance(val, (int, float)):
                    field_profiles[f]["type"] = "numeric"
                    is_outlier, fixed_val, _ = cls.detect_and_fix_outliers(f, float(val))
                    if is_outlier:
                        field_profiles[f]["outliers"] += 1
                        total_anomalies += 1
                    cleaned_r[f] = fixed_val
                elif isinstance(val, str):
                    # Thử parse số
                    num_match = re.match(r"^-?\d+(\.\d+)?$", val.strip())
                    if num_match:
                        field_profiles[f]["type"] = "numeric"
                        num_val = float(val.strip())
                        is_outlier, fixed_val, _ = cls.detect_and_fix_outliers(f, num_val)
                        if is_outlier:
                            field_profiles[f]["outliers"] += 1
                            total_anomalies += 1
                        cleaned_r[f] = fixed_val
                    else:
                        field_profiles[f]["type"] = "string"
                        cleaned_r[f] = cls.clean_scientific_text(val)
                else:
                    cleaned_r[f] = val

            cleaned_records.append(cleaned_r)

        return {
            "total_records": total_records,
            "total_anomalies": total_anomalies,
            "field_profiles": field_profiles,
            "cleaned_records": cleaned_records
        }


# Singleton service export
scientific_data_cleaner = ScientificDataCleaner()