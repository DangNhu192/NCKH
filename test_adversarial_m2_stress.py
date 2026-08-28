# test_adversarial_m2_stress.py
# Adversarial Stress-Testing and Fuzzing Suite for Word DOM and Math/Chem Engine
import os
import io
import re
import sys
import zipfile
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import parse_xml
import lxml.etree as ET

from modules.shared.docx_styler import DocxStyler, replace_text_in_paragraph_runs, sanitize_xml_text
from modules.shared.docx_formula_engine import (
    latex_to_mathml, mathml_to_omml, latex_to_omml,
    add_latex_equation, format_inline_chemical_formulas,
    UNICODE_CHEM_MAP
)
from modules.workspace.docx_editor_engine import DocxEditorEngine
from modules.math_chem_pro.math_chem_router import convert_equation, EquationConvertRequest

passed = 0
failed = 0
failures = []

def check(condition, desc, detail=''):
    global passed, failed
    if condition:
        print(f'  [PASS] {desc}')
        passed += 1
    else:
        print(f'  [FAIL] {desc}: {detail}')
        failed += 1
        failures.append(f'{desc}: {detail}')

print('=' * 75)
print('  EMPIRICAL ADVERSARIAL STRESS TEST SUITE (M2 DOM and MATH/CHEM)')
print('=' * 75)

# --- SUITE 1: Extreme Vietnamese Numbers and Disambiguation ---
print('\n[SUITE 1] Vietnamese Localization, Decimals, Thousands and Disambiguation')
cases = [
    ('Nồng độ vi lượng đạt 0.0001% và 0.00005 mg/L.', 'Nồng độ vi lượng đạt 0,0001% và 0,00005 mg/L.'),
    ('Lưu lượng dòng chảy 1234567.89 m3/ngày.', 'Lưu lượng dòng chảy 1234567,89 m3/ngày.'),
    ('Tổng khối lượng 1,234,567.89 kg vật liệu.', 'Tổng khối lượng 1.234.567,89 kg vật liệu.'),
    ('Nhiệt độ đáy hồ giảm xuống -15.75 °C hoặc -0.005 K.', 'Nhiệt độ đáy hồ giảm xuống -15,75 °C hoặc -0,005 K.'),
    ('Chỉ số p-value < 0.001 và R2 = 0.985 trong mô hình.', 'Chỉ số p-value < 0,001 và R2 = 0,985 trong mô hình.'),
    ('Độ nhạy đạt 99.999% với sai số MAPE <= 1.25%.', 'Độ nhạy đạt 99,999% với sai số MAPE <= 1,25%.'),
    ('Tham khảo DOI: 10.1000/182 và 10.1016/j.envres.2023.116500.', 'Tham khảo DOI: 10.1000/182 và 10.1016/j.envres.2023.116500.'),
    ('Nghiên cứu tại https://doi.org/10.1007/s11356-021-14321-4.', 'Nghiên cứu tại https://doi.org/10.1007/s11356-021-14321-4.'),
    ('Truy cập https://example.com/api/v2.1?query=1.5 and limit=10.0', 'Truy cập https://example.com/api/v2.1?query=1.5 and limit=10.0'),
    ('Hệ thống chạy trên Python 3.11.4, Gemini 1.5 Pro và YOLO v8.2.1.', 'Hệ thống chạy trên Python 3.11.4, Gemini 1.5 Pro và YOLO v8.2.1.'),
    ('Bản nâng cấp v3.2.1-beta tương thích với Windows 11 và CUDA 12.1.', 'Bản nâng cấp v3.2.1-beta tương thích với Windows 11 và CUDA 12.1.'),
    ('Xem chi tiết tại Mục 1.2.3.4 và Bảng 3.2 trong Điều 5.1.', 'Xem chi tiết tại Mục 1.2.3.4 và Bảng 3.2 trong Điều 5.1.'),
    ('Theo quy chuẩn QCVN 08-MT:2015/BTNMT và TCVN 5945:2005.', 'Theo quy chuẩn QCVN 08-MT:2015/BTNMT và TCVN 5945:2005.'),
    ('Kết quả tại (Mục 2.4.1) cho thấy tăng 15.8% so với (Hình 1.3).', 'Kết quả tại (Mục 2.4.1) cho thấy tăng 15,8% so với (Hình 1.3).'),
    ('Ngân sách tài trợ là 500,000 USD tương đương 12,500,000,000 VNĐ.', 'Ngân sách tài trợ là 500.000 USD tương đương 12.500.000.000 VNĐ.'),
    ('Sản lượng đạt 1,000 tấn và 50,000 sản phẩm.', 'Sản lượng đạt 1.000 tấn và 50.000 sản phẩm.')
]
for idx, (inp, exp) in enumerate(cases, 1):
    act = DocxStyler.convert_decimals_preserve_sections(inp)
    check(act == exp, f'Suite 1.{idx}: {inp[:40]}...', f'Expected: \"{exp}\", Got: \"{act}\"')

# --- SUITE 2: Multi-Run Paragraph and Style Preservation ---
print('\n[SUITE 2] Deep Nested Multi-Run Paragraph and Style Preservation')
doc_runs = Document()
p = doc_runs.add_paragraph()
r0 = p.add_run('Nghiên cứu tại trạm ')
r0.font.name = 'Times New Roman'
r0.font.size = Pt(13)

r1 = p.add_run('Đồng Tháp Mười')
r1.font.name = 'Arial'
r1.font.size = Pt(14)
r1.bold = True
r1.font.color.rgb = RGBColor(30, 58, 138)

r2 = p.add_run(' trong đợt khảo sát ')
r2.font.name = 'Times New Roman'
r2.font.size = Pt(13)
r2.italic = True

r3 = p.add_run('Mùa Lũ 2023')
r3.font.name = 'Courier New'
r3.font.size = Pt(12)
r3.underline = True
r3.font.color.rgb = RGBColor(220, 38, 38)

r4 = p.add_run(' cho thấy nồng độ ')
r4.font.name = 'Times New Roman'
r4.font.size = Pt(13)

r5 = p.add_run('FeS2 vượt ngưỡng 28.5%')
r5.font.name = 'Calibri'
r5.font.size = Pt(13.5)
r5.bold = True
r5.italic = True
r5.font.color.rgb = RGBColor(16, 185, 129)

# 2.1 Single-run replacement inside Run 1
replace_text_in_paragraph_runs(p, 'Đồng Tháp Mười', 'Tứ Giác Long Xuyên')
check(r1.text == 'Tứ Giác Long Xuyên', 'Suite 2.1: Single-run text replaced')
check(r1.bold is True and r1.font.color.rgb == RGBColor(30, 58, 138), 'Suite 2.1: Run 1 style preserved (Bold Navy)')
check(r0.text == 'Nghiên cứu tại trạm ', 'Suite 2.1: Run 0 intact')
check(r3.underline is True and r3.font.color.rgb == RGBColor(220, 38, 38), 'Suite 2.1: Run 3 style preserved (Underline Red)')
check(r5.bold is True and r5.italic is True and r5.font.color.rgb == RGBColor(16, 185, 129), 'Suite 2.1: Run 5 style preserved (Bold/Italic Green)')

# 2.2 Cross-run replacement spanning Run 0 and Run 1
replace_text_in_paragraph_runs(p, 'tại trạm Tứ Giác', 'điểm đo Vùng')
check(r0.text == 'Nghiên cứu điểm đo Vùng', 'Suite 2.2: Cross-run replacement in Run 0')
check(r1.text == ' Long Xuyên', 'Suite 2.2: Remnant in Run 1')
check(r1.bold is True and r1.font.color.rgb == RGBColor(30, 58, 138), 'Suite 2.2: Run 1 remnant style preserved')

# 2.3 Multiple occurrences across paragraph
p2 = doc_runs.add_paragraph()
ra = p2.add_run('Chỉ số BOD5 là 15.5 mg/L. ')
ra.bold = True
rb = p2.add_run('Chỉ số BOD5 sau xử lý là 2.5 mg/L. ')
rb.italic = True
rc = p2.add_run('Kết luận: BOD5 giảm.')
rc.underline = True
cnt = replace_text_in_paragraph_runs(p2, 'BOD5', 'BOD₅')
check(cnt == 3, f'Suite 2.3: Replaced all 3 occurrences (count={cnt})')
check(ra.bold is True and 'BOD₅' in ra.text, 'Suite 2.3: Run A bold preserved')
check(rb.italic is True and 'BOD₅' in rb.text, 'Suite 2.3: Run B italic preserved')
check(rc.underline is True and 'BOD₅' in rc.text, 'Suite 2.3: Run C underline preserved')

# --- SUITE 3: Chemical Formulas and Collision Resistance ---
print('\n[SUITE 3] Chemical Formulas, Subscripts, Ion Charges and Collision Resistance')
doc_chem = Document()
chem_text = (
    'Hỗn hợp gồm Ca(OH)2, FeS2, H2SO4, HNO3, H3PO4 và KMnO4 phản ứng với '
    'các ion NH4+, NO3-, Cr6+, As3+, Al3+, Cu2+, Pb2+, Cd2+, SO4 2-, PO4 3-. '
    'Chỉ số không khí PM2.5, PM10, CO2, SO2, NOx, O3, VOCs. '
    'Nước thải BOD5, COD, TOC, TSS, DO trong C6H12O6 và CH3COOH.'
)
formatted_chem = DocxStyler.clean_inline_latex_math(chem_text)
expected_chems = [
    'Ca(OH)₂', 'FeS₂', 'H₂SO₄', 'HNO₃', 'H₃PO₄', 'KMnO₄',
    'NH₄⁺', 'NO₃⁻', 'Cr⁶⁺', 'As³⁺', 'Al³⁺', 'Cu²⁺', 'Pb²⁺', 'Cd²⁺', 'SO₄²⁻', 'PO₄³⁻',
    'PM₂.₅', 'PM₁₀', 'CO₂', 'SO₂', 'NOₓ', 'O₃', 'VOCs',
    'BOD₅', 'COD', 'TOC', 'TSS', 'DO', 'C₆H₁₂O₆', 'CH₃COOH'
]
for ch in expected_chems:
    check(ch in formatted_chem, f'Suite 3 Token: {ch}', f'Missing in: {formatted_chem}')

# Substring collision test
p_col = doc_chem.add_paragraph('Đo nồng độ COD và DO trong phòng thí nghiệm. Không làm đổ (DO NOT SPILL) dung dịch.')
format_inline_chemical_formulas(p_col)
check('COD' in p_col.text, 'Suite 3 Collision: COD preserved')
check('DO' in p_col.text, 'Suite 3 Collision: DO preserved')

# Zotero field safety test
p_zot = doc_chem.add_paragraph()
p_zot.add_run('Phân tích FeS2 và H2SO4 ')
fld_xml = parse_xml(
    '<w:fldSimple %s w:instr=\"ADDIN ZOTERO_ITEM CSL_CITATION {\'id\':\'FeS2\'}\"><w:r><w:t>(Nguyen, 2023)</w:t></w:r></w:fldSimple>' % docx.oxml.ns.nsdecls('w')
)
p_zot._p.append(fld_xml)
p_zot.add_run(' cần xử lý bằng Ca(OH)2.')
format_inline_chemical_formulas(p_zot)
check('FeS₂' in p_zot.runs[0].text, 'Suite 3 Zotero: FeS₂ in Run 0 converted')
check('Ca(OH)₂' in p_zot.runs[1].text, 'Suite 3 Zotero: Ca(OH)₂ in Run 1 converted')
flds = p_zot._p.xpath('.//w:fldSimple')
check(len(flds) == 1, 'Suite 3 Zotero: w:fldSimple field intact')

# --- SUITE 4: Extreme OMML LaTeX Math Conversions ---
print('\n[SUITE 4] Extreme OMML LaTeX Math Conversions')
extreme_equations = [
    (r'\int_{0}^{\infty} \frac{x^3}{e^x - 1} dx = \frac{\pi^4}{15}', '4.1 Mission Master Equation'),
    (r'\rho \left( \frac{\partial \mathbf{u}}{\partial t} + \mathbf{u} \cdot \nabla \mathbf{u} \right) = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f}', '4.2 Navier-Stokes'),
    (r'i\hbar \frac{\partial}{\partial t}\Psi(\mathbf{r},t) = \left[ -\frac{\hbar^2}{2m}\nabla^2 + V(\mathbf{r},t) \right] \Psi(\mathbf{r},t)', '4.3 Schrodinger Equation'),
    (r'x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}', '4.4 Quadratic Formula'),
    (r'\lim_{n \to \infty} \sum_{k=1}^{n} \frac{1}{k^2} = \frac{\pi^2}{6}', '4.5 Basel Problem')
]
doc_math = Document()
for latex_code, label in extreme_equations:
    req = EquationConvertRequest(latex=latex_code, equation_number='1.1')
    res = convert_equation(req)
    check(res['success'] is True, f'Suite {label}: Router converted')
    omml = latex_to_omml(latex_code)
    check('<m:oMath' in omml, f'Suite {label}: OMML root tag present')
    pm = doc_math.add_paragraph()
    add_latex_equation(pm, latex_code, equation_number='1.1')
    omml_elems = pm._p.xpath('.//m:oMathPara | .//m:oMath')
    check(len(omml_elems) >= 1, f'Suite {label}: Paragraph contains OMML math element')

# --- SUITE 5: Word DOM XML Schema and Document Integrity Stress ---
print('\n[SUITE 5] Word DOM XML Schema and Document Integrity Stress')
engine = DocxEditorEngine()
sample_paras = [
    {'heading_level': 1, 'text': '1. TỔNG QUAN NGHIÊN CỨU MÔI TRƯỜNG ĐỒNG THÁP'},
    {'heading_level': 0, 'text': 'Nghiên cứu chất lượng nước tại trạm ĐT-01 tháng 08/2023. Nồng độ FeS2 và H2SO4 tạo pH = 3.5 và DO = 1.2 mg/L. Phục hồi 28.5% so với mức chuẩn 1.5 lần.'},
    {'heading_level': 2, 'text': '1.1. Phương Pháp Phân Tích and Chỉ Tiêu'},
    {'heading_level': 0, 'text': 'Đo Cr6+, As3+, Pb2+, Cd2+ và BOD5, COD theo QCVN 08-MT:2015/BTNMT giới hạn 0.05 mg/L.'}
]
sample_tbls = [
    {
        'title': 'Bảng 1.1. Chỉ số chất lượng nước',
        'rows': [
            ['Chỉ tiêu', 'Đơn vị', 'Mẫu ĐT-01', 'QCVN 08-MT:2015'],
            ['pH', '-', '3.5', '6.5 - 8.5'],
            ['DO', 'mg/L', '1.2', '>= 4.0'],
            ['BOD5', 'mg/L', '28.5', '<= 15.0'],
            ['COD', 'mg/L', '85.0', '<= 30.0'],
            ['Cr6+', 'mg/L', '0.045', '<= 0.02'],
            ['As3+', 'mg/L', '0.015', '<= 0.01']
        ]
    }
]
stress_path = 'Tai_Lieu/adversarial_stress_doc.docx'
s_res = engine.save_edited_docx(rel_path=stress_path, paragraphs=sample_paras, tables=sample_tbls)
check(s_res['success'] is True, 'Suite 5.1: save_edited_docx completed')

parsed = engine.parse_docx(stress_path)
check(parsed['success'] is True, 'Suite 5.2: parse_docx completed')
check(parsed['metadata']['paragraph_count'] >= 4, 'Suite 5.2: Paragraphs parsed')
check(parsed['metadata']['table_count'] == 1, 'Suite 5.2: Table parsed')

rep_res = engine.batch_replace_in_docx(
    rel_path=stress_path,
    replacements=[
        {'find': '28,5', 'replace': '32,4'},
        {'find': '1,5', 'replace': '2,0'},
        {'find': '0,05', 'replace': '0,02'},
        {'find': 'FeS₂', 'replace': 'FeS₂ (Pyrit)'},
        {'find': 'ĐT-01', 'replace': 'TRẠM-A1'}
    ],
    output_rel_path='Tai_Lieu/adversarial_stress_rep.docx'
)
tot_rep = rep_res.get('total_replacements', 0)
check(rep_res['success'] is True, 'Suite 5.3: batch_replace_in_docx completed')
check(tot_rep >= 5, f'Suite 5.3: Total replacements: {tot_rep}')

out_fpath = engine.workspace / 'Tai_Lieu/adversarial_stress_rep.docx'
check(out_fpath.exists(), 'Suite 5.4: Output file exists on disk')

with zipfile.ZipFile(out_fpath, 'r') as zf:
    xml_files = [n for n in zf.namelist() if n.endswith('.xml')]
    check('word/document.xml' in xml_files, 'Suite 5.4: word/document.xml found')
    all_valid = True
    for xf in xml_files:
        try:
            ET.fromstring(zf.read(xf))
        except Exception as e:
            all_valid = False
            failures.append(f'XML error in {xf}: {e}')
            break
    check(all_valid, 'Suite 5.5: 100% of OpenXML parts are well-formed XML')

print('=' * 75)
print(f'  ADVERSARIAL TEST SUMMARY: {passed} PASSED, {failed} FAILED')
print('=' * 75)
if failed == 0:
    print('\n>>> EMPIRICAL VERDICT: APPROVE (ALL 5 ADVERSARIAL VECTORS 100% PASS)')
    sys.exit(0)
else:
    print(f'\n>>> EMPIRICAL VERDICT: REQUEST_CHANGES ({failed} failures)')
    for f in failures:
        print(f'  - {f}')
    sys.exit(1)
