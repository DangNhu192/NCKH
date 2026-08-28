# test_dom_preservation_edge_cases.py
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import docx
from docx import Document
from docx.shared import Pt, RGBColor
from modules.shared.docx_styler import DocxStyler

print("=" * 70)
print("  TESTING DOM PRESERVATION & EDGE CASES")
print("=" * 70)

# Test 1: Multi-run styling preservation during update_docx_content_preserving_styles
doc = Document()
p = doc.add_paragraph()
r1 = p.add_run("Đoạn văn có phần in đậm: ")
r1.bold = True
r2 = p.add_run("và phần chữ nghiêng: ")
r2.italic = True
r3 = p.add_run("giá trị 25.0% tăng lên 30.0%.")
r3.font.color.rgb = RGBColor(220, 38, 38)

import io
buf = io.BytesIO()
doc.save(buf)
orig_bytes = buf.getvalue()

print(f"Original paragraph runs: count={len(p.runs)}")
for idx, r in enumerate(p.runs):
    print(f"  Run {idx}: text='{r.text}', bold={r.bold}, italic={r.italic}, color={r.font.color.rgb if r.font.color else None}")

# Apply replacement on run 3
mod_bytes = DocxStyler.update_docx_content_preserving_styles(orig_bytes, {"25.0%": "25,0%"})

doc_mod = Document(io.BytesIO(mod_bytes))
p_mod = doc_mod.paragraphs[0]
print(f"\nAfter DocxStyler.update_docx_content_preserving_styles runs: count={len(p_mod.runs)}")
for idx, r in enumerate(p_mod.runs):
    print(f"  Run {idx}: text='{r.text}', bold={r.bold}, italic={r.italic}, color={r.font.color.rgb if r.font.color else None}")

# Test 2: Chemical Formula Coverage
from modules.shared.docx_formula_engine import UNICODE_CHEM_MAP
print(f"\nTotal chemical terms in UNICODE_CHEM_MAP: {len(UNICODE_CHEM_MAP)}")
sample_environmental_chemicals = [
    "Ca(OH)2", "HNO3", "H3PO4", "Na2CO3", "NaHCO3", "KMnO4", "C6H12O6",
    "SO2", "NOx", "PM2.5", "PM10", "Cu2+", "Zn2+", "Pb2+", "Cd2+", "Cr6+", "Cr3+", "As3+", "As5+"
]
missing = [c for c in sample_environmental_chemicals if c not in UNICODE_CHEM_MAP]
print(f"Missing environmental chemicals from map ({len(missing)}): {missing}")
