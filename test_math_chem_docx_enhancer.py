from pathlib import Path
import docx
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from modules.shared.file_manager import file_mgr
from modules.shared.docx_formula_engine import scan_and_enhance_document_formulas, format_chemical_text

file_mgr.drafts_dir.mkdir(parents=True, exist_ok=True)

# 1. Create a raw sample docx file
doc = Document()
doc.add_heading('BÁO CÁO NGHIÊN CỨU THỬ NGHIỆM HÓA - TOÁN HỌC', level=1)

p1 = doc.add_paragraph('Quá trình oxy hóa phèn trong đất diễn ra theo phương trình phản ứng hóa học sau:')

# Block equation with LaTeX
p_eq = doc.add_paragraph('$$2FeS_2 + 7O_2 + 2H_2O \\longrightarrow 2Fe^{2+} + 4SO_4^{2-} + 4H^+$$ (1.1)')

p2 = doc.add_paragraph('Đồng thời các hợp chất H2SO4, Ca(OH)2, KMnO4 và các ion NH4+, NO3-, Al3+ được kiểm định với chỉ số BOD5 đạt 10.25 mg/L và nồng độ PM2.5 là 28.5%.')

p3 = doc.add_paragraph('Theo định luật năng lượng $E = mc^2$ và động học $L_t = L_0 (1 - 10^{-kt})$, quy mô mẫu gồm 10,000 cá thể với mức sai số 0.05.')

# Add a table
tbl = doc.add_table(rows=3, cols=3)
tbl.rows[0].cells[0].paragraphs[0].text = 'Thông số'
tbl.rows[0].cells[1].paragraphs[0].text = 'Công thức hóa học'
tbl.rows[0].cells[2].paragraphs[0].text = 'Giá trị đo đạc'

tbl.rows[1].cells[0].paragraphs[0].text = 'Axit Sunfuric'
tbl.rows[1].cells[1].paragraphs[0].text = 'H2SO4'
tbl.rows[1].cells[2].paragraphs[0].text = '10.5%'

tbl.rows[2].cells[0].paragraphs[0].text = 'Chỉ số WQI'
tbl.rows[2].cells[1].paragraphs[0].text = '$WQI = \\frac{A}{B}$'
tbl.rows[2].cells[2].paragraphs[0].text = '85.5%'

test_raw_path = file_mgr.drafts_dir / 'test_mathchem_raw.docx'
doc.save(str(test_raw_path))
print('Saved raw test docx:', test_raw_path)

# 2. Run scan and enhance
doc_to_enhance = Document(str(test_raw_path))
stats = scan_and_enhance_document_formulas(
    doc_to_enhance,
    normalize_chem=True,
    normalize_decimals=True,
    convert_latex_blocks=True,
    convert_inline_math=True
)

test_out_path = file_mgr.drafts_dir / 'test_mathchem_enhanced.docx'
doc_to_enhance.save(str(test_out_path))
print('Scan & Enhance Stats:', stats)

# 3. Verify output
doc_check = Document(str(test_out_path))
full_text = '\n'.join([p.text for p in doc_check.paragraphs])
for tbl in doc_check.tables:
    for row in tbl.rows:
        for cell in row.cells:
            full_text += '\n' + '\n'.join([p.text for p in cell.paragraphs])

print('Enhanced Text Preview:\n', full_text[:600])

assert 'H₂SO₄' in full_text, 'H2SO4 not converted'
assert 'Ca(OH)₂' in full_text, 'Ca(OH)2 not converted'
assert 'NH₄⁺' in full_text, 'NH4+ not converted'
assert 'NO₃⁻' in full_text, 'NO3- not converted'
assert 'Al³⁺' in full_text, 'Al3+ not converted'
assert 'BOD₅' in full_text, 'BOD5 not converted'
assert 'PM₂.₅' in full_text, 'PM2.5 not converted'
assert '10,5%' in full_text, '10.5% decimal not converted'
assert '28,5%' in full_text, '28.5% decimal not converted'
assert '0,05' in full_text, '0.05 decimal not converted'
assert '10.000' in full_text, '10,000 thousands separator not converted'
assert stats['block_equations'] >= 1, 'Block equation not counted'
assert stats['inline_equations'] >= 2, 'Inline equations not counted'
assert stats['chem_fixes'] >= 2, 'Chem fixes not counted'
assert stats['tables_scanned'] >= 1, 'Table not scanned'

print('\n>>> ALL 16 MATH-CHEM ENHANCER ASSERTIONS PASSED 100%! <<<')
