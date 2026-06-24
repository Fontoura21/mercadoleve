# -*- coding: utf-8 -*-
"""Gerador do Relatório Técnico DevSecOps — MercadoLeve.

Estilo acadêmico formal (mesmo layout do relatório de CTF): capa UFSC,
sumário, cabeçalho corrido, código monoespaçado em estilo acadêmico e
tabelas com cabeçalho destacado.
"""
import os
import textwrap

from fpdf import FPDF
from fpdf.enums import XPos, YPos

SUPP = "/System/Library/Fonts/Supplemental/"
SYS = "/System/Library/Fonts/"
ARIAL = SUPP + "Arial.ttf"
ARIAL_B = SUPP + "Arial Bold.ttf"
ARIAL_I = SUPP + "Arial Italic.ttf"
ARIAL_BI = SUPP + "Arial Bold Italic.ttf"
MONO = SYS + "SFNSMono.ttf"
MONO_I = SYS + "SFNSMonoItalic.ttf"

UFSC_LOGO = os.path.join(os.path.dirname(__file__), "ufsc_logo.png")
if not os.path.exists(UFSC_LOGO):
    UFSC_LOGO = "/tmp/ufsc_logo.png"

HEADER_TXT = "DevSecOps — Pipeline CI/CD | UFSC INE5429 | Pedro Augusto da Fontoura"
CODE_WRAP = 96


class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("Arial", "", ARIAL, uni=True)
        self.add_font("Arial", "B", ARIAL_B, uni=True)
        self.add_font("Arial", "I", ARIAL_I, uni=True)
        self.add_font("Arial", "BI", ARIAL_BI, uni=True)
        self.add_font("Mono", "", MONO, uni=True)
        self.add_font("Mono", "I", MONO_I, uni=True)
        self.set_auto_page_break(auto=True, margin=22)

    # ── cabeçalho / rodapé ────────────────────────────────────────────────
    def header(self):
        if self.page_no() <= 2:
            return
        self.set_font("Arial", "I", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 7, HEADER_TXT, align="C")
        self.set_draw_color(180, 180, 180)
        self.set_line_width(0.2)
        self.line(self.l_margin, self.get_y() + 1, self.w - self.r_margin, self.get_y() + 1)
        self.ln(5)
        self.set_text_color(0, 0, 0)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-14)
        self.set_font("Arial", "", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 8, str(self.page_no() - 1), align="C")
        self.set_text_color(0, 0, 0)

    # ── capa ──────────────────────────────────────────────────────────────
    def cover(self):
        self.add_page()
        if os.path.exists(UFSC_LOGO):
            self.image(UFSC_LOGO, x=(self.w - 30) / 2, y=18, w=30)
        self.ln(52)
        self.set_font("Arial", "B", 11)
        for line in [
            "UNIVERSIDADE FEDERAL DE SANTA CATARINA",
            "CAMPUS TRINDADE",
            "INE — DEPARTAMENTO DE INFORMÁTICA E ESTATÍSTICA",
            "INE5429 — SEGURANÇA EM COMPUTAÇÃO",
        ]:
            self.cell(0, 6, line, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(20)
        self.set_font("Arial", "B", 12)
        self.cell(0, 7, "PEDRO AUGUSTO DA FONTOURA (22215098)", align="C",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(28)
        self.set_font("Arial", "B", 14)
        self.cell(0, 8, "PIPELINE DEVSECOPS", align="C",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Arial", "B", 12)
        self.cell(0, 7, "AUTOMAÇÃO E AUDITORIA DE SEGURANÇA EM CI/CD", align="C",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(6)
        self.set_font("Arial", "", 11)
        self.cell(0, 6, "Sistema auditado: MercadoLeve — API de marketplace (FastAPI + PostgreSQL)",
                  align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_y(-40)
        self.set_font("Arial", "B", 11)
        self.cell(0, 6, "FLORIANÓPOLIS", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(0, 6, "2026", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ── sumário ───────────────────────────────────────────────────────────
    def toc(self, entries):
        self.add_page()
        self.set_font("Arial", "B", 12)
        self.cell(0, 8, "SUMÁRIO", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(4)
        for num, title, indent in entries:
            self.set_font("Arial", "" if indent else "B", 10)
            prefix = "      " if indent else ""
            self.cell(0, 6, f"{prefix}{num}  {title}",
                      new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ── títulos ───────────────────────────────────────────────────────────
    def ch1(self, num, title):
        self.ln(6)
        self.set_font("Arial", "B", 12)
        self.multi_cell(0, 8, f"{num}  {title.upper()}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

    def ch2(self, num, title):
        self.ln(3)
        self.set_font("Arial", "B", 10)
        self.multi_cell(0, 7, f"{num}  {title}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

    def ch3(self, title):
        self.ln(2)
        self.set_font("Arial", "BI", 9.5)
        self.multi_cell(0, 6, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ── corpo ─────────────────────────────────────────────────────────────
    def body(self, text):
        self.set_font("Arial", "", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5.5, text.strip(), align="J")
        self.set_text_color(0, 0, 0)
        self.ln(3)

    def bullet(self, items):
        self.set_font("Arial", "", 10)
        self.set_text_color(30, 30, 30)
        for it in items:
            x = self.get_x()
            self.set_x(self.l_margin + 3)
            self.multi_cell(0, 5.5, "•  " + it, align="J")
            self.ln(0.5)
        self.set_text_color(0, 0, 0)
        self.ln(2.5)

    # ── código (estilo acadêmico: monoespaçado indentado, sem fundo escuro) ─
    def code(self, raw, caption=None):
        lines = []
        for ln in raw.strip("\n").split("\n"):
            if len(ln) > CODE_WRAP:
                lines += textwrap.wrap(ln, CODE_WRAP, subsequent_indent="    ",
                                       break_long_words=True, break_on_hyphens=False) or [""]
            else:
                lines.append(ln)
        line_h = 4.4
        block_h = len(lines) * line_h + (6 if caption else 0) + 3
        # mantém legenda + bloco juntos quando couberem em uma página
        if self.get_y() + block_h > self.h - self.b_margin and block_h < (self.h - 40):
            self.add_page()
        if caption:
            self.set_font("Arial", "I", 8.5)
            self.set_text_color(90, 90, 90)
            self.multi_cell(0, 5, caption, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_text_color(0, 0, 0)
            self.ln(0.5)
        self.set_font("Mono", "", 8.3)
        self.set_text_color(20, 20, 20)
        for ln in lines:
            self.set_x(self.l_margin + 4)
            self.cell(0, line_h, ln, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(0, 0, 0)
        self.ln(3.5)

    # ── tabela genérica ───────────────────────────────────────────────────
    def _table_header(self, headers, widths):
        self.set_font("Arial", "B", 8.7)
        self.set_fill_color(15, 52, 96)
        self.set_text_color(255, 255, 255)
        self.set_draw_color(120, 120, 120)
        self.set_line_width(0.2)
        h = 7
        x0, y0 = self.l_margin, self.get_y()
        for w, head in zip(widths, headers):
            self.rect(x0, y0, w, h, style="DF")
            self.set_xy(x0, y0 + 1.4)
            self.multi_cell(w, 4.2, head, border=0, align="C")
            x0 += w
        self.set_y(y0 + h)
        self.set_text_color(0, 0, 0)

    def table(self, headers, rows, widths, aligns=None, caption=None, fonte=True):
        if caption:
            self.set_font("Arial", "BI", 9.5)
            self.multi_cell(0, 6, caption, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(0.5)
        aligns = aligns or ["L"] * len(headers)
        self._table_header(headers, widths)
        fills = [(245, 248, 255), (255, 255, 255)]
        line_h = 4.3
        for idx, row in enumerate(rows):
            self.set_font("Arial", "", 8.3)
            # mede altura da linha
            maxlines = 1
            for w, cell in zip(widths, row):
                ls = self.multi_cell(w - 2, line_h, str(cell), dry_run=True,
                                     output="LINES", border=0)
                maxlines = max(maxlines, len(ls))
            rh = maxlines * line_h + 2
            if self.get_y() + rh > self.h - self.b_margin:
                self.add_page()
                self._table_header(headers, widths)
            self.set_fill_color(*fills[idx % 2])
            self.set_draw_color(120, 120, 120)
            x0, y0 = self.l_margin, self.get_y()
            for w, cell, al in zip(widths, row, aligns):
                self.rect(x0, y0, w, rh, style="DF")
                self.set_xy(x0 + 1, y0 + 1)
                self.multi_cell(w - 2, line_h, str(cell), border=0, align=al)
                x0 += w
            self.set_y(y0 + rh)
        self.ln(2)
        if fonte:
            self.set_font("Arial", "I", 8.5)
            self.set_text_color(110, 110, 110)
            self.cell(0, 5, "Fonte: elaboração própria.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_text_color(0, 0, 0)
        self.ln(3)
