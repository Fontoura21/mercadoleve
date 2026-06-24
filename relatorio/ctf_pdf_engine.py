# -*- coding: utf-8 -*-
"""Motor de geração de PDF — reaproveitado VERBATIM do gerador do relatório de
CTF (gerar_relatorio_v2.py), para manter o mesmo padrão visual entre os
relatórios. Apenas o conteúdo específico (capa, sumário, cabeçalho) é
sobrescrito pela subclasse no script de conteúdo.
"""
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from PIL import Image, ImageDraw, ImageFont
import os, io, textwrap

# ── Fontes ──────────────────────────────────────────────────────────────────
SUPP = "/System/Library/Fonts/Supplemental/"
SYS  = "/System/Library/Fonts/"
USR  = "/Users/fontoura/Library/Fonts/"

ARIAL    = SUPP + "Arial.ttf"
ARIAL_B  = SUPP + "Arial Bold.ttf"
ARIAL_I  = SUPP + "Arial Italic.ttf"
ARIAL_BI = SUPP + "Arial Bold Italic.ttf"
PDF_MONO = SYS  + "SFNSMono.ttf"
PDF_MONO_I = SYS + "SFNSMonoItalic.ttf"

TERM_FONT     = SYS + "SFNSMono.ttf"
TERM_FONT_ALT = USR + "Anonymous Pro.ttf"

UFSC_LOGO = "/tmp/ufsc_logo.png"

# ── Paleta macOS Terminal (Dark) ─────────────────────────────────────────────
T_BG       = (30,  30,  30)
T_FG       = (220, 220, 220)
T_PROMPT   = (80,  200, 120)   # verde — prompt $
T_CMD      = (140, 200, 255)   # azul claro — comandos
T_OUTPUT   = (210, 210, 210)   # cinza claro — saída normal
T_SUCCESS  = (100, 220, 100)   # verde — [SUCESSO]
T_INFO     = (100, 180, 255)   # azul — [INFO]
T_FLAG     = (255, 230,  80)   # amarelo — destaque
T_WARN     = (255, 170,  70)   # laranja — WARN / HIGH
T_CRIT     = (255, 105, 100)   # vermelho — FAIL / CRITICAL
T_BANNER   = (180, 180, 180)   # cinza — linhas de banner
T_TITLEBAR = (50,  50,  50)
T_BTN_R    = (255,  95,  87)
T_BTN_Y    = (255, 189,  46)
T_BTN_G    = ( 39, 201,  63)


def make_terminal_image(lines_spec, title="bash — zsh", font_size=14, padding=16):
    """Renderiza uma imagem estilo Terminal macOS.
    lines_spec: lista de (texto, cor) — cor None usa T_OUTPUT.
    """
    try:
        font = ImageFont.truetype(TERM_FONT, font_size)
    except Exception:
        font = ImageFont.truetype(TERM_FONT_ALT, font_size)
    try:
        title_font = ImageFont.truetype(TERM_FONT, 11)
    except Exception:
        title_font = font

    line_h = font_size + 5
    title_bar_h = 32
    total_h = title_bar_h + padding + len(lines_spec) * line_h + padding

    max_chars = max((len(t) for t, _ in lines_spec), default=40)
    width = max(560, min(1100, max_chars * (font_size * 0.62) + padding * 2 + 10))
    width = int(width)
    total_h = int(total_h)

    img = Image.new("RGB", (width, total_h), T_BG)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, width, title_bar_h], fill=T_TITLEBAR)
    for i, color in enumerate([T_BTN_R, T_BTN_Y, T_BTN_G]):
        cx = 18 + i * 22
        draw.ellipse([cx-6, title_bar_h//2-6, cx+6, title_bar_h//2+6], fill=color)
    try:
        tw = draw.textlength(title, font=title_font)
    except Exception:
        tw = len(title) * 7
    draw.text(((width - tw) / 2, 9), title, font=title_font, fill=(180, 180, 180))

    y = title_bar_h + padding
    for text, color in lines_spec:
        c = color if color else T_OUTPUT
        draw.text((padding, y), text, font=font, fill=c)
        y += line_h

    draw.rectangle([0, 0, width-1, total_h-1], outline=(60, 60, 60), width=1)
    return img


def img_to_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


# ── Classe PDF ───────────────────────────────────────────────────────────────
class PDF(FPDF):
    HEADER_TXT = "Relatório Técnico | UFSC INE5429 | Pedro Augusto da Fontoura"

    def __init__(self):
        super().__init__()
        self.add_font("Arial",  "",   ARIAL,      uni=True)
        self.add_font("Arial",  "B",  ARIAL_B,    uni=True)
        self.add_font("Arial",  "I",  ARIAL_I,    uni=True)
        self.add_font("Arial",  "BI", ARIAL_BI,   uni=True)
        self.add_font("Mono",   "",   PDF_MONO,   uni=True)
        self.add_font("Mono",   "I",  PDF_MONO_I, uni=True)
        self.set_auto_page_break(auto=True, margin=22)

    def header(self):
        if self.page_no() <= 2:
            return
        self.set_font("Arial", "I", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 7, self.HEADER_TXT, align="C")
        self.set_draw_color(180, 180, 180)
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

    # ── Helpers de formatação (idênticos ao gerador do CTF) ──────────────────
    def ch1(self, num, title):
        self.ln(6)
        self.set_font("Arial", "B", 12)
        self.multi_cell(0, 8, f"{num}  {title.upper()}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

    def ch2(self, num, title):
        self.ln(4)
        self.set_font("Arial", "B", 10)
        self.multi_cell(0, 7, f"{num}  {title}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

    def ch3(self, title):
        self.ln(2)
        self.set_font("Arial", "BI", 9.5)
        self.multi_cell(0, 6, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

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
            self.set_x(self.l_margin + 3)
            self.multi_cell(0, 5.5, "•  " + it, align="J")
            self.ln(0.5)
        self.set_text_color(0, 0, 0)
        self.ln(2.5)

    def inline_code(self, code):
        """Bloco de código inline simples (sem fundo escuro — estilo acadêmico)."""
        self.set_font("Mono", "", 8.5)
        for line in code.strip("\n").split("\n"):
            if len(line) > 100:
                wrapped = textwrap.wrap(line, 100, subsequent_indent="    ",
                                        break_long_words=True, break_on_hyphens=False) or [""]
            else:
                wrapped = [line]
            for w in wrapped:
                self.set_x(self.l_margin + 4)
                self.cell(0, 5, w, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)

    def terminal_image(self, img_path, caption=""):
        """Insere screenshot do terminal no PDF (idêntico ao gerador do CTF)."""
        if not os.path.exists(img_path):
            self.body(f"[Screenshot não encontrado: {img_path}]")
            return
        img = Image.open(img_path)
        avail_w = self.w - self.l_margin - self.r_margin
        ratio = img.height / img.width
        img_h = avail_w * ratio
        if self.get_y() + img_h + 15 > self.h - self.b_margin:
            self.add_page()
        self.image(img_path, x=self.l_margin, w=avail_w)
        if caption:
            self.ln(1)
            self.set_font("Arial", "I", 8)
            self.set_text_color(100, 100, 100)
            self.multi_cell(0, 5, caption, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_text_color(0, 0, 0)
        self.ln(4)

    def gen_table(self, headers, rows, widths, aligns=None, caption=None, fonte=True):
        """Tabela no mesmo estilo do prim_table do CTF (cabeçalho azul, zebra)."""
        if caption:
            self.set_font("Arial", "BI", 9.5)
            self.multi_cell(0, 6, caption, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(1)
        aligns = aligns or ["L"] * len(headers)

        def draw_header():
            self.set_font("Arial", "B", 8.7)
            self.set_fill_color(30, 60, 100)
            self.set_text_color(255, 255, 255)
            self.set_draw_color(120, 120, 120)
            self.set_line_width(0.2)
            x0, y0 = self.l_margin, self.get_y()
            for w, h in zip(widths, headers):
                self.rect(x0, y0, w, 7, style="DF")
                self.set_xy(x0, y0 + 1.4)
                self.multi_cell(w, 4.2, h, border=0, align="C")
                x0 += w
            self.set_y(y0 + 7)
            self.set_text_color(0, 0, 0)

        draw_header()
        fills = [(245, 248, 255), (255, 255, 255)]
        line_h = 4.3
        for idx, row in enumerate(rows):
            self.set_font("Arial", "", 8.3)
            maxlines = 1
            for w, cell in zip(widths, row):
                ls = self.multi_cell(w - 2, line_h, str(cell), dry_run=True,
                                     output="LINES", border=0)
                maxlines = max(maxlines, len(ls))
            rh = maxlines * line_h + 2
            if self.get_y() + rh > self.h - self.b_margin:
                self.add_page()
                draw_header()
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
