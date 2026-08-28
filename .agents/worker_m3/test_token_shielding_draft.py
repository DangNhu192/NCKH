import io
from docx import Document
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn

doc = Document()
p = doc.add_paragraph('Test start ')
fld_xml = f'<w:fldSimple {nsdecls("w")} w:instr=" ADDIN ZOTERO_ITEM CSL_CITATION "><w:r><w:t>(Nguyen, 2023)</w:t></w:r></w:fldSimple>'
fld = parse_xml(fld_xml)
p._p.append(fld)
r = p.add_run(' test end.')

print('Initial p text:', p.text)
print('Children count:', len(list(p._p)))

children = list(p._p)
for c in children:
    if c.tag != qn('w:pPr'):
        p._p.remove(c)

r1 = parse_xml(f'<w:r {nsdecls("w")}><w:t>Rewritten start </w:t></w:r>')
p._p.append(r1)
p._p.append(fld)
r2 = parse_xml(f'<w:r {nsdecls("w")}><w:t> rewritten end.</w:t></w:r>')
p._p.append(r2)

print('After update p text:', p.text)
print('Children after:', [c.tag for c in p._p])

buf = io.BytesIO()
doc.save(buf)
doc2 = Document(io.BytesIO(buf.getvalue()))
print('Reloaded doc text:', doc2.paragraphs[0].text)
print('Reloaded children:', [c.tag for c in doc2.paragraphs[0]._p])
print('Reloaded fldSimple tag:', [c.tag for c in doc2.paragraphs[0]._p if c.tag.endswith('fldSimple')])
