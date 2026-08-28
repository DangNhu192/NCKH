import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path: sys.path.insert(0, str(PROJECT_ROOT))
from docx import Document
from modules.humanizer.humanizer_engine import humanizer_engine
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
import io

doc = Document()
h1 = doc.add_heading("1. TỔNG QUAN TÌNH HÌNH NGHIÊN CỨU", level=1)
h2 = doc.add_paragraph("1.1. Cơ sở lý thuyết và mô hình tính toán", style="Heading 2")
p_vn_head = doc.add_paragraph("1.2. Phân tích thực nghiệm đa kênh")
pPr = p_vn_head._p.get_or_add_pPr()
outline_elem = parse_xml(f'<w:outlineLvl {nsdecls("w")} w:val="1"/>')
pPr.append(outline_elem)

p_body1 = doc.add_paragraph("Theo nghiên cứu tiên phong của tác giả ")
zotero_csl_payload = '{"citationID":"csl1","citationItems":[{"id":123,"uris":["http://zotero.org/users/123/items/ABC"]}],"properties":{"formattedCitation":"(Nguyen & Tran, 2023)","plainCitation":"(Nguyen & Tran, 2023)"}}'
escaped_csl = zotero_csl_payload.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
fld_simple_xml = f'''
<w:fldSimple {nsdecls('w')} w:instr=" ADDIN ZOTERO_ITEM CSL_CITATION {escaped_csl} ">
    <w:r>
        <w:rPr>
            <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>
            <w:sz w:val="26"/>
        </w:rPr>
        <w:t>(Nguyen &amp; Tran, 2023)</w:t>
    </w:r>
</w:fldSimple>
'''
p_body1._p.append(parse_xml(fld_simple_xml))
p_body1.add_run(" cho thấy trong bối cảnh hiện nay hiệu suất quang điện của FeS2 kết hợp H2SO4 đạt 28.5% với chi phí 50,000 USD.")

buf = io.BytesIO()
doc.save(buf)
orig_bytes = buf.getvalue()

# Now reload as in humanize_docx_bytes
doc_loaded = Document(io.BytesIO(orig_bytes))
for idx, paragraph in enumerate(doc_loaded.paragraphs):
    raw_p = paragraph.text.strip()
    print(f"--- Paragraph {idx} ---")
    print(f"raw_p: {repr(raw_p[:40])}")
    is_head = humanizer_engine.is_heading_or_protected_paragraph(paragraph)
    print(f"is_head: {is_head}")
    if is_head:
        continue
    sh_text, t_map, base = humanizer_engine.shield_paragraph_dom(paragraph)
    print(f"sh_text: {repr(sh_text[:40])}")
    print(f"t_map: {t_map.keys()}")
    an = humanizer_engine.analyze(sh_text)
    cond = an["ai_probability"] > 15 or an["cliches_count"] > 0 or an["similarity_index"] > 8 or an["burstiness_score"] < 8.0
    print(f"cond: {cond}, an: burstiness={an['burstiness_score']}, cliches={an['cliches_count']}, ai={an['ai_probability']}")
    if cond:
        u = humanizer_engine.process_unified(sh_text)
        print(f"unified: {repr(u[:60])}")
        humanizer_engine.restore_paragraph_dom(paragraph, u, t_map, base)
        print(f"after text: {repr(paragraph.text[:60])}")
