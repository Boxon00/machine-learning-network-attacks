"""Mali pomocni sloj iznad python-docx: blokovi sadrzaja -> akademski formatiran DOCX.

Blokovi: ("h1"|"h2"|"h3", txt) ("p", txt) ("bul", [..]) ("num", [..]) ("eq", txt) ("code", txt)
         ("fig", key, path, caption, width_cm) ("tab", key, caption, header, rows, widths_cm, note)
Oznake u tekstu: [[cite:kljuc]] -> [n];  [[fig:kljuc]] -> "Slika n";  [[tab:kljuc]] -> "Tabela n";
**podebljano**, __kurziv__.
"""
from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

FONT = "Times New Roman"


def _set_cell_bg(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def _cell_margins(table, top=40, bottom=40, left=70, right=70):
    tblPr = table._tbl.tblPr
    m = OxmlElement("w:tblCellMar")
    for k, v in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        e = OxmlElement(f"w:{k}"); e.set(qn("w:w"), str(v)); e.set(qn("w:type"), "dxa"); m.append(e)
    tblPr.append(m)


def _add_field(run, instr):
    for t, txt in (("begin", None), (None, instr), ("end", None)):
        if t:
            fc = OxmlElement("w:fldChar"); fc.set(qn("w:fldCharType"), t); run._r.append(fc)
        else:
            it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = txt; run._r.append(it)


class Builder:
    def __init__(self, line_spacing=1.3, chapter_page_break=True):
        self.doc = Document()
        self.line_spacing = line_spacing
        self.chapter_page_break = chapter_page_break
        self.cite_order, self.refs = [], {}
        self.fig_no, self.tab_no = {}, {}
        self._setup()

    # ---------------------------------------------------------------- setup
    def _setup(self):
        d = self.doc
        s = d.sections[0]
        s.page_height, s.page_width = Cm(29.7), Cm(21.0)
        s.left_margin, s.right_margin = Cm(3.0), Cm(2.5)
        s.top_margin, s.bottom_margin = Cm(2.5), Cm(2.5)
        st = d.styles
        n = st["Normal"]; n.font.name = FONT; n.font.size = Pt(12)
        n.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
        n.paragraph_format.space_after = Pt(6)
        n.paragraph_format.line_spacing = self.line_spacing
        for name, size, before, after in (("Heading 1", 16, 0, 12), ("Heading 2", 13.5, 14, 6), ("Heading 3", 12, 10, 4)):
            h = st[name]; h.font.name = FONT; h.font.size = Pt(size); h.font.bold = True
            h.font.color.rgb = RGBColor(0, 0, 0); h.font.italic = (name == "Heading 3")
            h.element.rPr.rFonts.set(qn("w:eastAsia"), FONT); h.element.rPr.rFonts.set(qn("w:ascii"), FONT)
            h.element.rPr.rFonts.set(qn("w:hAnsi"), FONT)
            for att in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
                if h.element.rPr.rFonts.get(qn(att)) is not None:
                    del h.element.rPr.rFonts.attrib[qn(att)]
            h.paragraph_format.space_before = Pt(before); h.paragraph_format.space_after = Pt(after)
            h.paragraph_format.keep_with_next = True; h.paragraph_format.line_spacing = 1.1
        cap = st["Caption"]; cap.font.name = FONT; cap.font.size = Pt(10.5); cap.font.bold = False
        cap.font.italic = False; cap.font.color.rgb = RGBColor(0, 0, 0)

    # ---------------------------------------------------------------- numeracija
    def register(self, blocks):
        f = t = 0
        for b in blocks:
            if b[0] == "fig":
                f += 1; self.fig_no[b[1]] = f
            elif b[0] == "tab":
                t += 1; self.tab_no[b[1]] = t

    def _resolve(self, text):
        def sub(m):
            kind, key = m.group(1), m.group(2)
            if kind == "cite":
                if key not in self.refs:
                    raise KeyError(f"Nepoznata referenca: {key}")
                if key not in self.cite_order:
                    self.cite_order.append(key)
                return f"[{self.cite_order.index(key) + 1}]"
            if kind == "fig":
                return f"Slika {self.fig_no[key]}"
            if kind == "tab":
                return f"Tabela {self.tab_no[key]}"
            return m.group(0)
        return re.sub(r"\[\[(cite|fig|tab):([A-Za-z0-9_]+)\]\]", sub, text)

    def _runs(self, par, text, size=None, font=None):
        text = self._resolve(text)
        for part in re.split(r"(\*\*.+?\*\*|__.+?__)", text):
            if not part:
                continue
            if part.startswith("**"):
                r = par.add_run(part[2:-2]); r.bold = True
            elif part.startswith("__"):
                r = par.add_run(part[2:-2]); r.italic = True
            else:
                r = par.add_run(part)
            if size: r.font.size = Pt(size)
            if font:
                r.font.name = font; r._element.rPr.rFonts.set(qn("w:eastAsia"), font)

    # ---------------------------------------------------------------- blokovi
    def render(self, blocks):
        d = self.doc
        for b in blocks:
            k = b[0]
            if k == "h1":
                if self.chapter_page_break and getattr(self, "_h1_count", 0) > 0:
                    d.add_page_break()
                self._h1_count = getattr(self, "_h1_count", 0) + 1
                d.add_heading(self._resolve(b[1]), level=1)
            elif k in ("h2", "h3"):
                d.add_heading(self._resolve(b[1]), level=int(k[1]))
            elif k == "p":
                p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p.paragraph_format.first_line_indent = Cm(1.0)
                self._runs(p, b[1])
            elif k == "pn":  # paragraf bez uvlacenja
                p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                self._runs(p, b[1])
            elif k in ("bul", "num"):
                for it in b[1]:
                    p = d.add_paragraph(style="List Bullet" if k == "bul" else "List Number")
                    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    p.paragraph_format.space_after = Pt(3)
                    self._runs(p, it)
            elif k == "eq":
                p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(4)
                self._runs(p, b[1], size=12, font="Cambria Math")
            elif k == "code":
                for line in b[1].strip("\n").split("\n"):
                    p = d.add_paragraph(); p.paragraph_format.space_after = Pt(0)
                    p.paragraph_format.line_spacing = 1.0
                    p.paragraph_format.left_indent = Cm(0.5)
                    r = p.add_run(line if line else " "); r.font.name = "Courier New"; r.font.size = Pt(9)
                    r._element.rPr.rFonts.set(qn("w:eastAsia"), "Courier New")
                d.add_paragraph().paragraph_format.space_after = Pt(2)
            elif k == "fig":
                _, key, path, cap, width = b
                p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.keep_with_next = True; p.paragraph_format.space_after = Pt(2)
                p.add_run().add_picture(str(path), width=Cm(width))
                c = d.add_paragraph(style="Caption"); c.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r = c.add_run(f"Slika {self.fig_no[key]}. "); r.bold = True
                self._runs(c, cap)
            elif k == "tab":
                self._table(*b[1:])
            elif k == "pb":
                d.add_page_break()
            elif k == "raw":
                b[1](d)

    def _table(self, key, caption, header, rows, widths=None, note=None):
        d = self.doc
        c = d.add_paragraph(style="Caption"); c.alignment = WD_ALIGN_PARAGRAPH.CENTER
        c.paragraph_format.keep_with_next = True; c.paragraph_format.space_after = Pt(3)
        r = c.add_run(f"Tabela {self.tab_no[key]}. "); r.bold = True
        self._runs(c, caption)
        t = d.add_table(rows=1, cols=len(header)); t.style = "Table Grid"
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        _cell_margins(t)
        total = 15.5
        widths = widths or [total / len(header)] * len(header)
        t.autofit = False
        for i, w in enumerate(widths):
            t.columns[i].width = Cm(w)
        for i, h in enumerate(header):
            cell = t.rows[0].cells[i]; cell.width = Cm(widths[i]); _set_cell_bg(cell, "D9E2F3")
            p = cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.0
            rr = p.add_run(str(h)); rr.bold = True; rr.font.size = Pt(9)
        for row in rows:
            cells = t.add_row().cells
            for i, v in enumerate(row):
                cells[i].width = Cm(widths[i])
                p = cells[i].paragraphs[0]; p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.0
                self._runs(p, str(v), size=9.5)
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT if i == 0 else WD_ALIGN_PARAGRAPH.CENTER
        # tabela ostaje na jednoj strani (osim ako je duza od strane)
        if len(t.rows) <= 14:
            for row in t.rows[:-1]:
                for cell in row.cells:
                    for par in cell.paragraphs:
                        par.paragraph_format.keep_with_next = True
        # zaglavlje se ponavlja, redovi se ne dele
        trPr = t.rows[0]._tr.get_or_add_trPr(); th = OxmlElement("w:tblHeader"); th.set(qn("w:val"), "true"); trPr.append(th)
        for row in t.rows:
            trPr = row._tr.get_or_add_trPr(); cs = OxmlElement("w:cantSplit"); cs.set(qn("w:val"), "true"); trPr.append(cs)
        if note:
            p = d.add_paragraph(); p.paragraph_format.space_before = Pt(2)
            self._runs(p, note, size=9.5)
        else:
            d.add_paragraph().paragraph_format.space_after = Pt(2)

    # ---------------------------------------------------------------- footer
    def add_page_numbers(self):
        s = self.doc.sections[0]
        s.different_first_page_header_footer = True
        p = s.footer.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(); r.font.size = Pt(10); _add_field(r, "PAGE")
