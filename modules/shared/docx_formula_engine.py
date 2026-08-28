"""
docx_formula_engine.py
======================
Engine chuyển đổi công thức Toán học & Hóa học (LaTeX / MathML) sang OMML (Office Math Markup Language)
và chèn trực tiếp vào tài liệu Word (.docx) hỗ trợ Equation Editor gốc của Microsoft Word.
Bảo toàn 100% mã trường trích dẫn Zotero (w:fldChar, w:instrText) khi chuẩn hóa hóa học inline.
"""

import os
import re
from typing import Optional, Union, List, Tuple
import docx
from docx.document import Document
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.text.paragraph import Paragraph

try:
    import latex2mathml.commands
    import latex2mathml.converter
    import lxml.etree as ET
except ImportError:
    pass

MML2OMML_XSL = """<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"
    xmlns:mml="http://www.w3.org/1998/Math/MathML"
    exclude-result-prefixes="mml">

    <xsl:output method="xml" encoding="UTF-8" indent="no"/>

    <xsl:template match="mml:math">
        <m:oMath>
            <xsl:apply-templates/>
        </m:oMath>
    </xsl:template>

    <xsl:template match="mml:mi">
        <m:r>
            <m:rPr>
                <m:sty m:val="i"/>
            </m:rPr>
            <m:t><xsl:value-of select="."/></m:t>
        </m:r>
    </xsl:template>

    <xsl:template match="mml:mn">
        <m:r>
            <m:rPr>
                <m:sty m:val="p"/>
            </m:rPr>
            <m:t><xsl:value-of select="."/></m:t>
        </m:r>
    </xsl:template>

    <xsl:template match="mml:mo">
        <m:r>
            <m:rPr>
                <m:sty m:val="p"/>
            </m:rPr>
            <m:t><xsl:value-of select="."/></m:t>
        </m:r>
    </xsl:template>

    <xsl:template match="mml:mtext">
        <m:r>
            <m:rPr>
                <m:nor/>
            </m:rPr>
            <m:t><xsl:value-of select="."/></m:t>
        </m:r>
    </xsl:template>

    <xsl:template match="mml:mfrac">
        <m:f>
            <m:fPr/>
            <m:num>
                <xsl:apply-templates select="*[1]"/>
            </m:num>
            <m:den>
                <xsl:apply-templates select="*[2]"/>
            </m:den>
        </m:f>
    </xsl:template>

    <xsl:template match="mml:msup">
        <m:sSup>
            <m:sSupPr/>
            <m:e>
                <xsl:apply-templates select="*[1]"/>
            </m:e>
            <m:sup>
                <xsl:apply-templates select="*[2]"/>
            </m:sup>
        </m:sSup>
    </xsl:template>

    <xsl:template match="mml:msub">
        <m:sSub>
            <m:sSubPr/>
            <m:e>
                <xsl:apply-templates select="*[1]"/>
            </m:e>
            <m:sub>
                <xsl:apply-templates select="*[2]"/>
            </m:sub>
        </m:sSub>
    </xsl:template>

    <xsl:template match="mml:msubsup">
        <m:sSubSup>
            <m:sSubSupPr/>
            <m:e>
                <xsl:apply-templates select="*[1]"/>
            </m:e>
            <m:sub>
                <xsl:apply-templates select="*[2]"/>
            </m:sub>
            <m:sup>
                <xsl:apply-templates select="*[3]"/>
            </m:sup>
        </m:sSubSup>
    </xsl:template>

    <xsl:template match="mml:msqrt">
        <m:rad>
            <m:radPr>
                <m:deg m:val="none"/>
            </m:radPr>
            <m:e>
                <xsl:apply-templates/>
            </m:e>
        </m:rad>
    </xsl:template>

    <xsl:template match="mml:mroot">
        <m:rad>
            <m:radPr/>
            <m:deg>
                <xsl:apply-templates select="*[2]"/>
            </m:deg>
            <m:e>
                <xsl:apply-templates select="*[1]"/>
            </m:e>
        </m:rad>
    </xsl:template>

    <xsl:template match="mml:mrow">
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="mml:mover">
        <m:limUpp>
            <m:limUppPr/>
            <m:e>
                <xsl:apply-templates select="*[1]"/>
            </m:e>
            <m:lim>
                <xsl:apply-templates select="*[2]"/>
            </m:lim>
        </m:limUpp>
    </xsl:template>

    <xsl:template match="mml:munder">
        <m:limLow>
            <m:limLowPr/>
            <m:e>
                <xsl:apply-templates select="*[1]"/>
            </m:e>
            <m:lim>
                <xsl:apply-templates select="*[2]"/>
            </m:lim>
        </m:limLow>
    </xsl:template>

    <xsl:template match="mml:munderover">
        <m:nary>
            <m:naryPr/>
            <m:sub>
                <xsl:apply-templates select="*[2]"/>
            </m:sub>
            <m:sup>
                <xsl:apply-templates select="*[3]"/>
            </m:sup>
            <m:e>
                <xsl:apply-templates select="*[1]"/>
            </m:e>
        </m:nary>
    </xsl:template>

    <xsl:template match="*">
        <xsl:apply-templates/>
    </xsl:template>

</xsl:stylesheet>
"""

UNICODE_CHEM_MAP = {
    # 1. Bazơ, Muối & Hợp chất vô cơ
    "Ca(OH)2": "Ca(OH)₂",
    "Ba(OH)2": "Ba(OH)₂",
    "Mg(OH)2": "Mg(OH)₂",
    "Al(OH)3": "Al(OH)₃",
    "Fe(OH)2": "Fe(OH)₂",
    "Fe(OH)3": "Fe(OH)₃",
    "Na2CO3": "Na₂CO₃",
    "NaHCO3": "NaHCO₃",
    "KMnO4": "KMnO₄",
    "K2Cr2O7": "K₂Cr₂O₇",
    "CaCO3": "CaCO₃",
    "FeS2": "FeS₂",
    "P2O5": "P₂O₅",
    "K2O": "K₂O",
    "SiO2": "SiO₂",
    "Al2O3": "Al₂O₃",
    "Fe2O3": "Fe₂O₃",
    "CaCl2": "CaCl₂",
    "MgCl2": "MgCl₂",
    "NaCl": "NaCl",
    "KCl": "KCl",
    "MgSO4": "MgSO₄",
    "CaSO4": "CaSO₄",
    "FeSO4": "FeSO₄",
    "BaSO4": "BaSO₄",
    "Na2SO4": "Na₂SO₄",
    "K2SO4": "K₂SO₄",
    "NH4Cl": "NH₄Cl",
    "NaNO3": "NaNO₃",
    "KNO3": "KNO₃",
    "AgNO3": "AgNO₃",

    # 2. Axit vô cơ
    "H2SO4": "H₂SO₄",
    "H2SO3": "H₂SO₃",
    "HNO3": "HNO₃",
    "HNO2": "HNO₂",
    "H3PO4": "H₃PO₄",
    "H2S": "H₂S",
    "H2CO3": "H₂CO₃",
    "HClO4": "HClO₄",
    "HCl": "HCl",
    "HF": "HF",
    "HBr": "HBr",
    "HI": "HI",

    # 3. Khí & Chỉ số chất lượng không khí / Môi trường
    "PM2.5": "PM₂.₅",
    "PM10": "PM₁₀",
    "PM1.0": "PM₁.₀",
    "CO2-eq": "CO₂-eq",
    "CO2eq": "CO₂eq",
    "CO2": "CO₂",
    "SO2": "SO₂",
    "NOx": "NOₓ",
    "NO2": "NO₂",
    "NO3": "NO₃",
    "N2O": "N₂O",
    "NH3": "NH₃",
    "CH4": "CH₄",
    "O3": "O₃",
    "O2": "O₂",
    "N2": "N₂",
    "H2": "H₂",
    "H2O": "H₂O",
    "CO": "CO",
    "VOCs": "VOCs",

    # 4. Chỉ số môi trường & Nước thải
    "BOD5": "BOD₅",
    "BOD": "BOD",
    "COD": "COD",
    "TOC": "TOC",
    "TSS": "TSS",
    "DO": "DO",

    # 5. Ion vô cơ & Kim loại nặng
    "SO4 2-": "SO₄²⁻",
    "SO42-": "SO₄²⁻",
    "PO4 3-": "PO₄³⁻",
    "PO43-": "PO₄³⁻",
    "CO3 2-": "CO₃²⁻",
    "CO32-": "CO₃²⁻",
    "HCO3-": "HCO₃⁻",
    "NH4+": "NH₄⁺",
    "NO3-": "NO₃⁻",
    "NO2-": "NO₂⁻",
    "Al3+": "Al³⁺",
    "Fe2+": "Fe²⁺",
    "Fe3+": "Fe³⁺",
    "Mg2+": "Mg²⁺",
    "Ca2+": "Ca²⁺",
    "Cu2+": "Cu²⁺",
    "Zn2+": "Zn²⁺",
    "Pb2+": "Pb²⁺",
    "Cd2+": "Cd²⁺",
    "Cr6+": "Cr⁶⁺",
    "Cr3+": "Cr³⁺",
    "As3+": "As³⁺",
    "As5+": "As⁵⁺",
    "Hg2+": "Hg²⁺",
    "Ni2+": "Ni²⁺",
    "Mn2+": "Mn²⁺",
    "Co2+": "Co²⁺",
    "Ba2+": "Ba²⁺",
    "H+": "H⁺",
    "OH-": "OH⁻",
    "Cl-": "Cl⁻",
    "Na+": "Na⁺",
    "K+": "K⁺",

    # 6. Hợp chất hữu cơ
    "C6H12O6": "C₆H₁₂O₆",
    "C2H5OH": "C₂H₅OH",
    "CH3COOH": "CH₃COOH",
    "CH3OH": "CH₃OH",
    "C3H8": "C₃H₈",
    "C4H10": "C₄H₁₀",
    "C6H6": "C₆H₆"
}


def latex_to_mathml(latex_str: str) -> str:
    """Chuyển đổi chuỗi công thức LaTeX sang MathML XML."""
    clean_latex = latex_str.strip()
    if clean_latex.startswith("$$") and clean_latex.endswith("$$"):
        clean_latex = clean_latex[2:-2].strip()
    elif clean_latex.startswith("$") and clean_latex.endswith("$"):
        clean_latex = clean_latex[1:-1].strip()
        
    try:
        import latex2mathml.converter
        return latex2mathml.converter.convert(clean_latex)
    except Exception as e:
        return f'<math xmlns="http://www.w3.org/1998/Math/MathML"><mtext>{clean_latex}</mtext></math>'


def mathml_to_omml(mathml_str: str) -> str:
    """Chuyển đổi MathML sang OMML (Office Math Markup Language) sử dụng XSLT chuẩn."""
    try:
        import lxml.etree as ET
        xslt_doc = ET.fromstring(MML2OMML_XSL.encode('utf-8'))
        transform = ET.XSLT(xslt_doc)
        mml_tree = ET.fromstring(mathml_str.encode('utf-8'))
        omml_tree = transform(mml_tree)
        return ET.tostring(omml_tree, encoding='unicode')
    except Exception as e:
        text_content = re.sub(r'<[^>]+>', '', mathml_str)
        return (
            f'<m:oMath xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">'
            f'<m:r><m:t>{text_content}</m:t></m:r>'
            f'</m:oMath>'
        )


def latex_to_omml(latex_str: str) -> str:
    """Chuyển đổi trực tiếp LaTeX sang OMML XML string."""
    mml = latex_to_mathml(latex_str)
    return mathml_to_omml(mml)


def add_latex_equation(
    paragraph: Paragraph,
    latex_str: str,
    equation_number: Optional[str] = None
) -> Paragraph:
    """
    Chèn một công thức Toán/Hóa học dạng khối OMML vào paragraph của python-docx.
    Cho phép hiển thị như đối tượng Equation Editor gốc trong Microsoft Word.
    """
    try:
        omml_str = latex_to_omml(latex_str)
        omml_elem = parse_xml(omml_str.encode('utf-8'))
        
        omml_para = parse_xml(
            f'<m:oMathPara xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"/>'
        )
        omml_para.append(omml_elem)
        paragraph._p.append(omml_para)
        
        if equation_number:
            run_num = paragraph.add_run(f"\t({equation_number})")
            run_num.font.name = "Times New Roman"
            run_num.font.size = docx.shared.Pt(11)
            run_num.font.italic = True
            
        return paragraph
    except Exception as e:
        run = paragraph.add_run(latex_str)
        run.font.name = "Times New Roman"
        run.font.size = docx.shared.Pt(11)
        run.font.italic = True
        if equation_number:
            paragraph.add_run(f"\t({equation_number})")
        return paragraph


def format_chemical_text(text: str) -> str:
    """
    Chuẩn hóa văn bản chứa công thức hóa học, ion và mũi tên phản ứng.
    Bảo toàn định dạng văn bản gốc.
    """
    if not text:
        return text

    t = text
    # 1. Bảng tra cứu 109 hợp chất tĩnh (sắp xếp theo độ dài giảm dần)
    sorted_chem = sorted(UNICODE_CHEM_MAP.items(), key=lambda x: len(x[0]), reverse=True)
    for raw_term, uni_term in sorted_chem:
        if raw_term in t:
            t = t.replace(raw_term, uni_term)

    # 2. Chuẩn hóa mũi tên phản ứng hóa học
    arrow_replacements = [
        (r'\s*\\longrightarrow\s*', ' ⟶ '),
        (r'\s*\\rightarrow\s*', ' → '),
        (r'\s*\\leftarrow\s*', ' ← '),
        (r'\s*\\leftrightarrow\s*', ' ↔ '),
        (r'\s*<=>\s*', ' ⇌ '),
        (r'\s*<->\s*', ' ↔ '),
        (r'\s*->\s*', ' → ')
    ]
    for pattern, repl in arrow_replacements:
        t = re.sub(pattern, repl, t)

    # 3. Chuẩn hóa phân tử ngậm nước (Hydrates)
    t = re.sub(r'([A-Za-z0-9\(\)\u2080-\u2089\u00B2\u00B3\u2074-\u2079\u207A\u207B]+)\.(\d*H[₂2]O)', r'\1·\2', t)

    return t


def format_inline_chemical_formulas(paragraph: Paragraph) -> bool:
    """
    Chuẩn hóa các ký hiệu hóa học trong một paragraph bằng bảng ánh xạ Unicode.
    Bảo toàn 100% các run chứa mã trường Zotero (w:fldChar, w:instrText).
    """
    text = paragraph.text
    if not text.strip():
        return False

    has_match = False
    sorted_chem = sorted(UNICODE_CHEM_MAP.items(), key=lambda x: len(x[0]), reverse=True)
    for raw_term, _ in sorted_chem:
        if raw_term in text:
            has_match = True
            break

    if not has_match and not any(arrow in text for arrow in ["->", "<=>", "<->", "\\longrightarrow"]):
        return False

    changed = False
    for run in paragraph.runs:
        if not run.text:
            continue
        new_text = format_chemical_text(run.text)
        if new_text != run.text:
            run.text = new_text
            changed = True
                
    return changed


def scan_and_enhance_paragraph_math_chem(
    paragraph: Paragraph,
    normalize_chem: bool = True,
    convert_latex_blocks: bool = True,
    convert_inline_math: bool = True
) -> dict:
    """
    Quét và nâng cấp một paragraph Word:
    1. Nhận diện khối công thức Block LaTeX ($$...$$ hoặc \\[...\\]) -> chuyển thành Word Equation OMML centered.
    2. Nhận diện công thức Inline LaTeX ($...$ hoặc \\(...\\)) -> chuyển thành inline <m:oMath> không tràn dòng.
    3. Chuẩn hóa ký hiệu hóa học Unicode và phản ứng.
    """
    stats = {"block_eq": 0, "inline_eq": 0, "chem_fixed": False}
    p_txt = paragraph.text.strip()
    if not p_txt:
        return stats

    # 1. Kiểm tra Block Equation ($$...$$ hoặc \[...\])
    if convert_latex_blocks:
        match_block = re.match(r'^\s*(?:\$\$|\\\[)([\s\S]+?)(?:\$\$|\\\])\s*(?:\((\d+(?:\.\d+)*)\))?\s*$', p_txt)
        if match_block:
            latex_code = match_block.group(1).strip()
            eq_num = match_block.group(2)
            paragraph.text = ""
            paragraph.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER
            paragraph.paragraph_format.space_before = docx.shared.Pt(6)
            paragraph.paragraph_format.space_after = docx.shared.Pt(6)
            add_latex_equation(paragraph, latex_code, eq_num)
            stats["block_eq"] += 1
            return stats

    # 2. Kiểm tra Inline Math ($...$ hoặc \(...\))
    if convert_inline_math and (("$" in p_txt and not p_txt.startswith("$$")) or r"\(" in p_txt):
        # Tách chuỗi theo các khối inline math
        tokens = re.split(r'(\$(?:[^\$\n]+?)\$|\\\((?:.+?)\\\))', p_txt)
        if len(tokens) > 1 and any(t.startswith("$") or t.startswith(r"\(") for t in tokens):
            paragraph.text = ""
            for token in tokens:
                if not token:
                    continue
                is_math = (token.startswith("$") and token.endswith("$") and len(token) > 2) or \
                          (token.startswith(r"\(") and token.endswith(r"\)") and len(token) > 4)
                if is_math:
                    raw_latex = token[1:-1] if token.startswith("$") else token[2:-2]
                    try:
                        omml_str = latex_to_omml(raw_latex.strip())
                        omml_elem = parse_xml(omml_str.encode('utf-8'))
                        paragraph._p.append(omml_elem)
                        stats["inline_eq"] += 1
                    except Exception:
                        run = paragraph.add_run(token)
                        run.font.name = "Times New Roman"
                        run.font.size = docx.shared.Pt(12)
                        run.font.italic = True
                else:
                    txt_part = format_chemical_text(token) if normalize_chem else token
                    run = paragraph.add_run(txt_part)
                    run.font.name = "Times New Roman"
                    run.font.size = docx.shared.Pt(12)
            return stats

    # 3. Chuẩn hóa hóa học trong paragraph văn bản thông thường
    if normalize_chem:
        if format_inline_chemical_formulas(paragraph):
            stats["chem_fixed"] = True

    return stats


def scan_and_enhance_document_formulas(
    doc: Document,
    normalize_chem: bool = True,
    normalize_decimals: bool = True,
    convert_latex_blocks: bool = True,
    convert_inline_math: bool = True
) -> dict:
    """
    Quét toàn bộ tài liệu Word (đoạn văn và tất cả bảng biểu):
    - Chuyển đổi toàn diện công thức toán LaTeX (Block & Inline) sang Word Equation OMML.
    - Chuẩn hóa ký hiệu hóa học (FeS₂, H₂SO₄, NH₄⁺, BOD₅...).
    - Chuẩn hóa số thập phân tiếng Việt (1,5; 28,5%) và phân cách hàng nghìn.
    - Bảo toàn 100% DOM và cấu trúc tài liệu.
    """
    from modules.shared.docx_styler import DocxStyler

    total_blocks = 0
    total_inlines = 0
    total_chem = 0
    total_decimals = 0
    tables_count = len(doc.tables)

    # 1. Quét toàn bộ Đoạn văn trong Thân bài
    for p in doc.paragraphs:
        res = scan_and_enhance_paragraph_math_chem(
            p,
            normalize_chem=normalize_chem,
            convert_latex_blocks=convert_latex_blocks,
            convert_inline_math=convert_inline_math
        )
        total_blocks += res.get("block_eq", 0)
        total_inlines += res.get("inline_eq", 0)
        if res.get("chem_fixed"):
            total_chem += 1

    # 2. Quét toàn bộ Bảng biểu
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    res = scan_and_enhance_paragraph_math_chem(
                        p,
                        normalize_chem=normalize_chem,
                        convert_latex_blocks=convert_latex_blocks,
                        convert_inline_math=convert_inline_math
                    )
                    total_blocks += res.get("block_eq", 0)
                    total_inlines += res.get("inline_eq", 0)
                    if res.get("chem_fixed"):
                        total_chem += 1

    # 3. Chuẩn hóa số thập phân tiếng Việt
    if normalize_decimals:
        total_decimals = DocxStyler.convert_document_decimals(doc)

    return {
        "block_equations": total_blocks,
        "inline_equations": total_inlines,
        "chem_fixes": total_chem,
        "decimal_fixes": total_decimals,
        "tables_scanned": tables_count,
        "total_paragraphs": len(doc.paragraphs)
    }

