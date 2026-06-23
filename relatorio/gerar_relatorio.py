# -*- coding: utf-8 -*-
"""Gera o relatório técnico DevSecOps do MercadoLeve em PDF (reportlab)."""
import textwrap

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate, Frame, HRFlowable, KeepTogether, NextPageTemplate,
    PageBreak, PageTemplate, Paragraph, Preformatted, Spacer, Table, TableStyle,
)

INK = colors.HexColor("#1a1a2e")
ACCENT = colors.HexColor("#0f3460")
ACCENT2 = colors.HexColor("#16213e")
RED = colors.HexColor("#b00020")
ORANGE = colors.HexColor("#c25e00")
GREEN = colors.HexColor("#1b5e20")
GREY = colors.HexColor("#555555")
LIGHT = colors.HexColor("#eef1f6")
CODEBG = colors.HexColor("#f4f5f7")
LINE = colors.HexColor("#cfd6e4")

styles = getSampleStyleSheet()


def S(name, **kw):
    base = kw.pop("parent", styles["Normal"])
    if name in styles.byName:
        del styles.byName[name]
    styles.add(ParagraphStyle(name, parent=base, **kw))


S("Body", fontName="Helvetica", fontSize=10, leading=15, alignment=TA_JUSTIFY, spaceAfter=6, textColor=INK)
S("BodyL", parent=styles["Body"], alignment=TA_LEFT)
S("H1", fontName="Helvetica-Bold", fontSize=16, leading=20, textColor=ACCENT, spaceBefore=4, spaceAfter=6)
S("H2", fontName="Helvetica-Bold", fontSize=12.5, leading=16, textColor=ACCENT2, spaceBefore=10, spaceAfter=5)
S("H3", fontName="Helvetica-Bold", fontSize=10.5, leading=14, textColor=INK, spaceBefore=7, spaceAfter=3)
S("Small", fontName="Helvetica", fontSize=8.5, leading=12, textColor=GREY)
S("Code", fontName="Courier", fontSize=7.3, leading=9.3, textColor=INK)
S("Tbl", fontName="Helvetica", fontSize=8.3, leading=10.5, textColor=INK)
S("TblS", fontName="Helvetica", fontSize=7.5, leading=9.6, textColor=INK)
S("TblH", fontName="Helvetica-Bold", fontSize=8.3, leading=11, textColor=colors.white)
S("Cover1", fontName="Helvetica-Bold", fontSize=27, leading=32, textColor=colors.white, alignment=TA_CENTER)
S("Cover2", fontName="Helvetica", fontSize=14, leading=20, textColor=colors.white, alignment=TA_CENTER)
S("CoverS", fontName="Helvetica", fontSize=10.5, leading=16, textColor=colors.HexColor("#c9d3e6"), alignment=TA_CENTER)

story = []


def h1(t):
    story.append(PageBreak())
    story.append(Paragraph(t, styles["H1"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=ACCENT, spaceAfter=8))


def h2(t): story.append(Paragraph(t, styles["H2"]))
def h3(t): story.append(Paragraph(t, styles["H3"]))
def p(t): story.append(Paragraph(t, styles["Body"]))
def pl(t): story.append(Paragraph(t, styles["BodyL"]))
def small(t): story.append(Paragraph(t, styles["Small"]))
def sp(h=6): story.append(Spacer(1, h))


def bullets(items):
    for it in items:
        story.append(Paragraph("•&nbsp;&nbsp;" + it, styles["BodyL"]))
    sp(4)


def code(text_block, title=None, wrap=120):
    flow = []
    if title:
        flow.append(Paragraph(title, styles["Small"]))
        flow.append(Spacer(1, 2))
    lines = []
    for ln in text_block.rstrip("\n").split("\n"):
        if len(ln) > wrap:
            lines += textwrap.wrap(ln, wrap, subsequent_indent="    ",
                                   break_long_words=True, break_on_hyphens=False) or [""]
        else:
            lines.append(ln)
    pre = Preformatted("\n".join(lines), styles["Code"])
    t = Table([[pre]], colWidths=[17.0 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CODEBG),
        ("BOX", (0, 0), (-1, -1), 0.5, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBEFORE", (0, 0), (0, -1), 2.5, ACCENT),
    ]))
    flow.append(t)
    flow.append(Spacer(1, 7))
    story.append(KeepTogether(flow))


def table(data, col_widths, font="Tbl", align_left_cols=None):
    align_left_cols = align_left_cols or []
    rows = []
    for r, row in enumerate(data):
        cells = []
        for cell in row:
            st = styles["TblH"] if r == 0 else styles[font]
            cells.append(Paragraph(str(cell), st))
        rows.append(cells)
    t = Table(rows, colWidths=col_widths, repeatRows=1)
    ts = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT), ("ALIGN", (0, 0), (-1, 0), "CENTER"),
    ]
    for c in range(len(data[0])):
        if c not in align_left_cols:
            ts.append(("ALIGN", (c, 1), (c, -1), "CENTER"))
    for i in range(1, len(data)):
        if i % 2 == 0:
            ts.append(("BACKGROUND", (0, i), (-1, i), LIGHT))
    t.setStyle(TableStyle(ts))
    story.append(t)
    sp(8)


def callout(title, body, color=ACCENT):
    inner = [Paragraph(f'<b>{title}</b>', styles["BodyL"]),
             Paragraph(body, styles["BodyL"])]
    t = Table([[inner]], colWidths=[17.0 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f7f9fc")),
        ("BOX", (0, 0), (-1, -1), 0.5, color),
        ("LINEBEFORE", (0, 0), (0, -1), 3, color),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    sp(8)


def R(t): return f'<font color="#b00020"><b>{t}</b></font>'
def O(t): return f'<font color="#c25e00"><b>{t}</b></font>'
def G(t): return f'<font color="#1b5e20"><b>{t}</b></font>'


# ============================ CAPA / PÁGINAS ================================
def cover_bg(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(ACCENT2); canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    canvas.setFillColor(ACCENT); canvas.rect(0, A4[1] - 6 * cm, A4[0], 6 * cm, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#e94560")); canvas.rect(0, A4[1] - 6.18 * cm, A4[0], 0.18 * cm, fill=1, stroke=0)
    canvas.restoreState()


def later_pages(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE); canvas.setLineWidth(0.5)
    canvas.line(2.2 * cm, A4[1] - 1.5 * cm, A4[0] - 2.2 * cm, A4[1] - 1.5 * cm)
    canvas.setFont("Helvetica", 8); canvas.setFillColor(GREY)
    canvas.drawString(2.2 * cm, A4[1] - 1.35 * cm, "Relatório Técnico DevSecOps — MercadoLeve")
    canvas.drawRightString(A4[0] - 2.2 * cm, A4[1] - 1.35 * cm, "CI/CD Security Pipeline")
    canvas.line(2.2 * cm, 1.3 * cm, A4[0] - 2.2 * cm, 1.3 * cm)
    canvas.drawString(2.2 * cm, 1.0 * cm, "Pedro Fontoura")
    canvas.drawCentredString(A4[0] / 2, 1.0 * cm, "Segurança de Sistemas")
    canvas.drawRightString(A4[0] - 2.2 * cm, 1.0 * cm, "Página %d" % (doc.page - 1))
    canvas.restoreState()


def cover_page():
    story.append(Spacer(1, 5.4 * cm))
    story.append(Paragraph("Pipeline DevSecOps", styles["Cover1"]))
    story.append(Paragraph("Automação e Auditoria de Segurança em CI/CD", styles["Cover2"]))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("Relatório Técnico", styles["Cover2"]))
    story.append(Spacer(1, 4.6 * cm))
    story.append(Paragraph("Sistema auditado: <b>MercadoLeve</b> — API de marketplace (FastAPI + PostgreSQL)", styles["CoverS"]))
    story.append(Spacer(1, 0.25 * cm))
    story.append(Paragraph("Esteira: GitHub Actions&nbsp;&nbsp;|&nbsp;&nbsp;Secret · SCA · SAST · IaC · DAST", styles["CoverS"]))
    story.append(Spacer(1, 1.6 * cm))
    story.append(Paragraph("Pedro Fontoura", styles["CoverS"]))
    story.append(Paragraph("Disciplina de Segurança de Sistemas", styles["CoverS"]))
    story.append(Paragraph("Junho de 2026", styles["CoverS"]))


def render(filename="Relatorio_DevSecOps_MercadoLeve.pdf"):
    doc = BaseDocTemplate(
        filename, pagesize=A4,
        title="Relatório Técnico DevSecOps - MercadoLeve", author="Pedro Fontoura",
        leftMargin=2.2 * cm, rightMargin=2.2 * cm, topMargin=2.0 * cm, bottomMargin=1.6 * cm,
    )
    cover_frame = Frame(0, 0, A4[0], A4[1], id="cover", leftPadding=2.2 * cm,
                        rightPadding=2.2 * cm, topPadding=2 * cm, bottomPadding=2 * cm)
    content_frame = Frame(2.2 * cm, 1.5 * cm, A4[0] - 4.4 * cm, A4[1] - 3.2 * cm, id="content")
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[cover_frame], onPage=cover_bg),
        PageTemplate(id="content", frames=[content_frame], onPage=later_pages),
    ])
    doc.build(story)
    print("PDF gerado:", filename)
