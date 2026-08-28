import io
from docx import Document
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn

doc = Document()
p = doc.add_paragraph('Mo dau ')

# Add complex field
r_begin = parse_xml(f'<w:r {nsdecls("w")}><w:fldChar w:fldCharType="begin"/></w:r>')
r_instr = parse_xml(f'<w:r {nsdecls("w")}><w:instrText xml:space="preserve"> ADDIN ZOTERO_ITEM CSL_CITATION </w:instrText></w:r>')
r_sep = parse_xml(f'<w:r {nsdecls("w")}><w:fldChar w:fldCharType="separate"/></w:r>')
r_disp = parse_xml(f'<w:r {nsdecls("w")}><w:t>(Tran, 2024)</w:t></w:r>')
r_end = parse_xml(f'<w:r {nsdecls("w")}><w:fldChar w:fldCharType="end"/></w:r>')

for elem in [r_begin, r_instr, r_sep, r_disp, r_end]:
    p._p.append(elem)

r_tail = parse_xml(f'<w:r {nsdecls("w")}><w:t> ket thuc voi so lieu 28.5%.</w:t></w:r>')
p._p.append(r_tail)

print('Full p text before:', p.text)

# Token shielding extractor
token_map = {}
token_idx = 0
shielded_parts = []

in_complex_field = False
complex_group = []

for child in list(p._p):
    if child.tag == qn('w:pPr'):
        continue
    
    # Check complex field begin
    fldChars = child.xpath('.//w:fldChar')
    if fldChars:
        charType = fldChars[0].get(qn('w:fldCharType'))
        if charType == 'begin':
            in_complex_field = True
            complex_group = [child]
            continue
        elif charType == 'end':
            complex_group.append(child)
            in_complex_field = False
            token = f"{{{{ZOTERO_REF_{token_idx}}}}}"
            token_idx += 1
            token_map[token] = complex_group
            shielded_parts.append(token)
            complex_group = []
            continue
        else:
            if in_complex_field:
                complex_group.append(child)
                continue
    
    if in_complex_field:
        complex_group.append(child)
        continue
        
    if child.tag == qn('w:fldSimple'):
        token = f"{{{{ZOTERO_REF_{token_idx}}}}}"
        token_idx += 1
        token_map[token] = [child]
        shielded_parts.append(token)
        continue
        
    # Regular run
    t_nodes = child.xpath('.//w:t')
    text_content = "".join([t.text or "" for t in t_nodes])
    if text_content:
        shielded_parts.append(text_content)

full_shielded = "".join(shielded_parts)
print("Shielded text for LLM:", full_shielded)
print("Token map keys:", list(token_map.keys()))

# Simulate LLM humanization:
# "Mo dau {{ZOTERO_REF_0}} ket thuc voi so lieu 28.5%."
# -> "Khao sat thuc te tu {{ZOTERO_REF_0}} cho thay hieu qua vuot troi voi so lieu 28,5%."
rewritten = f"Khao sat thuc te tu {list(token_map.keys())[0]} cho thay hieu qua vuot troi voi so lieu 28,5%."

# Rebuild DOM
for child in list(p._p):
    if child.tag != qn('w:pPr'):
        p._p.remove(child)

import re
parts = re.split(r'(\{\{ZOTERO_REF_\d+\}\})', rewritten)
for part in parts:
    if part in token_map:
        for elem in token_map[part]:
            p._p.append(elem)
    elif part:
        r_new = parse_xml(f'<w:r {nsdecls("w")}><w:t xml:space="preserve">{part}</w:t></w:r>')
        p._p.append(r_new)

print('Full p text after:', p.text)
buf = io.BytesIO()
doc.save(buf)
doc2 = Document(io.BytesIO(buf.getvalue()))
p2 = doc2.paragraphs[0]
print('Reloaded text:', p2.text)
print('Reloaded complex fldChar count:', len(p2._p.xpath('.//w:fldChar')))
