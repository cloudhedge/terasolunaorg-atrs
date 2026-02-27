#!/usr/bin/env python3
"""Generate professional Word-like PDFs from ATRS markdown documentation."""

import re
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.colors import HexColor, black, white, Color
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Flowable, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ---------------------------------------------------------------------------
# Colour palette (professional navy/slate theme)
# ---------------------------------------------------------------------------
NAVY = HexColor("#1B2A4A")
DARK_BLUE = HexColor("#2C3E6B")
MEDIUM_BLUE = HexColor("#3D5A99")
LIGHT_BLUE = HexColor("#E8EDF5")
ACCENT = HexColor("#D4A843")  # Gold accent
DARK_GRAY = HexColor("#333333")
MEDIUM_GRAY = HexColor("#666666")
LIGHT_GRAY = HexColor("#F5F5F5")
TABLE_HEADER_BG = HexColor("#2C3E6B")
TABLE_ALT_ROW = HexColor("#F0F3F8")
BORDER_COLOR = HexColor("#CBD5E1")

# ---------------------------------------------------------------------------
# Custom styles
# ---------------------------------------------------------------------------
def get_custom_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='DocTitle',
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=28,
        textColor=NAVY,
        spaceAfter=6,
        alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name='DocSubtitle',
        fontName='Helvetica',
        fontSize=11,
        leading=16,
        textColor=MEDIUM_GRAY,
        spaceAfter=4,
        alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name='H1',
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=22,
        textColor=NAVY,
        spaceBefore=18,
        spaceAfter=8,
        borderWidth=0,
    ))
    styles.add(ParagraphStyle(
        name='H2',
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=18,
        textColor=DARK_BLUE,
        spaceBefore=14,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name='H3',
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=MEDIUM_BLUE,
        spaceBefore=10,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name='BodyText2',
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=DARK_GRAY,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
    ))
    styles.add(ParagraphStyle(
        name='BulletItem',
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=DARK_GRAY,
        leftIndent=20,
        spaceAfter=3,
        bulletIndent=8,
    ))
    styles.add(ParagraphStyle(
        name='CodeBlock',
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=HexColor("#1E293B"),
        backColor=HexColor("#F1F5F9"),
        leftIndent=12,
        rightIndent=12,
        spaceBefore=6,
        spaceAfter=6,
        borderWidth=0.5,
        borderColor=BORDER_COLOR,
        borderPadding=6,
    ))
    styles.add(ParagraphStyle(
        name='TableHeader',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=white,
        alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name='TableCell',
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=DARK_GRAY,
        alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name='Footer',
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=MEDIUM_GRAY,
        alignment=TA_CENTER,
    ))
    return styles


# ---------------------------------------------------------------------------
# Horizontal rule flowable
# ---------------------------------------------------------------------------
class HRFlowable(Flowable):
    def __init__(self, width, color=BORDER_COLOR, thickness=1):
        Flowable.__init__(self)
        self.width = width
        self.color = color
        self.thickness = thickness
        self.height = 8

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 4, self.width, 4)


# ---------------------------------------------------------------------------
# Section heading with coloured left bar
# ---------------------------------------------------------------------------
class SectionHeading(Flowable):
    def __init__(self, text, level=1, width=468):
        Flowable.__init__(self)
        self.text = text
        self.level = level
        self._width = width
        if level == 1:
            self.fontSize = 16
            self.color = NAVY
            self.barColor = ACCENT
            self.barWidth = 4
            self.height = 30
        elif level == 2:
            self.fontSize = 13
            self.color = DARK_BLUE
            self.barColor = MEDIUM_BLUE
            self.barWidth = 3
            self.height = 24
        else:
            self.fontSize = 11
            self.color = MEDIUM_BLUE
            self.barColor = None
            self.barWidth = 0
            self.height = 20

    def draw(self):
        if self.barColor:
            self.canv.setFillColor(self.barColor)
            self.canv.rect(0, 0, self.barWidth, self.height, fill=1, stroke=0)
        self.canv.setFillColor(self.color)
        self.canv.setFont("Helvetica-Bold", self.fontSize)
        x = self.barWidth + 8 if self.barColor else 0
        self.canv.drawString(x, 6, self.text)


# ---------------------------------------------------------------------------
# Markdown → flowable parser
# ---------------------------------------------------------------------------
def escape_xml(text):
    """Escape XML special characters for ReportLab paragraphs."""
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text


def parse_inline(text):
    """Convert markdown inline formatting to ReportLab XML."""
    # Links [text](url) → text (do this first to avoid interference)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Inline code (do before bold/italic to protect code content)
    # Replace backtick code with placeholder to avoid bold/italic parsing inside
    code_segments = {}
    counter = [0]
    def replace_code(m):
        key = f"__CODE{counter[0]}__"
        code_segments[key] = f'<font face="Courier" size="8">{m.group(1)}</font>'
        counter[0] += 1
        return key
    text = re.sub(r'`([^`]+)`', replace_code, text)
    # Bold + italic
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<b><i>\1</i></b>', text)
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Italic (only match single * not inside words with *)
    text = re.sub(r'(?<!\w)\*([^\*]+?)\*(?!\w)', r'<i>\1</i>', text)
    # Restore code segments
    for key, val in code_segments.items():
        text = text.replace(key, val)
    return text


def parse_table(lines, styles):
    """Parse markdown table lines into a ReportLab Table."""
    rows = []
    for line in lines:
        line = line.strip()
        if line.startswith('|'):
            line = line[1:]
        if line.endswith('|'):
            line = line[:-1]
        cells = [c.strip() for c in line.split('|')]
        rows.append(cells)

    if len(rows) < 2:
        return None

    # Check if row 2 is separator (----)
    is_sep = all(re.match(r'^[\s:\-]+$', c) for c in rows[1])
    if is_sep:
        header = rows[0]
        data_rows = rows[2:]
    else:
        header = rows[0]
        data_rows = rows[1:]

    # Build table data with Paragraphs
    table_data = []
    header_paras = [Paragraph(parse_inline(escape_xml(h)), styles['TableHeader']) for h in header]
    table_data.append(header_paras)

    for row in data_rows:
        while len(row) < len(header):
            row.append('')
        row_paras = [Paragraph(parse_inline(escape_xml(c)), styles['TableCell']) for c in row[:len(header)]]
        table_data.append(row_paras)

    if not table_data:
        return None

    num_cols = len(header)
    avail_width = 468  # letter width - margins
    col_width = avail_width / num_cols
    col_widths = [col_width] * num_cols

    style_commands = [
        ('BACKGROUND', (0, 0), (-1, 0), TABLE_HEADER_BG),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8.5),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8.5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
    ]

    # Alternating row colours
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            style_commands.append(('BACKGROUND', (0, i), (-1, i), TABLE_ALT_ROW))

    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle(style_commands))
    return t


def md_to_flowables(md_text, styles, page_width=468):
    """Convert markdown text to a list of ReportLab flowables."""
    flowables = []
    lines = md_text.split('\n')
    i = 0
    title_extracted = False
    in_code_block = False
    code_lines = []

    while i < len(lines):
        line = lines[i]

        # Code block handling
        if line.strip().startswith('```'):
            if in_code_block:
                code_text = escape_xml('\n'.join(code_lines))
                code_text = code_text.replace('\n', '<br/>')
                code_text = code_text.replace(' ', '&nbsp;')
                flowables.append(Paragraph(code_text, styles['CodeBlock']))
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
                code_lines = []
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            i += 1
            continue

        # Horizontal rule
        if re.match(r'^---+$', stripped) or re.match(r'^\*\*\*+$', stripped):
            flowables.append(HRFlowable(page_width))
            i += 1
            continue

        # Headings
        heading_match = re.match(r'^(#{1,4})\s+(.+)$', stripped)
        if heading_match:
            level = len(heading_match.group(1))
            text = heading_match.group(2).strip()

            if level == 1 and not title_extracted:
                # Document title
                title_extracted = True
                # Title with accent bar
                flowables.append(Spacer(1, 4))
                flowables.append(SectionHeading(text, level=0, width=page_width))
                flowables.append(Spacer(1, 8))
                i += 1
                continue

            if level == 1:
                flowables.append(Spacer(1, 10))
                flowables.append(SectionHeading(text, level=1, width=page_width))
                flowables.append(Spacer(1, 6))
            elif level == 2:
                flowables.append(Spacer(1, 8))
                flowables.append(SectionHeading(text, level=2, width=page_width))
                flowables.append(Spacer(1, 4))
            elif level == 3:
                flowables.append(Spacer(1, 6))
                flowables.append(SectionHeading(text, level=3, width=page_width))
                flowables.append(Spacer(1, 3))
            else:
                flowables.append(Paragraph(
                    parse_inline(escape_xml(text)),
                    styles['H3']
                ))
            i += 1
            continue

        # Table detection
        if stripped.startswith('|') and '|' in stripped[1:]:
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i])
                i += 1
            tbl = parse_table(table_lines, styles)
            if tbl:
                flowables.append(Spacer(1, 4))
                flowables.append(tbl)
                flowables.append(Spacer(1, 4))
            continue

        # Bullet points
        bullet_match = re.match(r'^(\s*)[-*]\s+(.+)$', stripped)
        if bullet_match:
            text = bullet_match.group(2)
            # Check for checkbox
            text = re.sub(r'^\[x\]\s*', '<font color="#22C55E">&#x2713;</font> ', text)
            text = re.sub(r'^\[\s*\]\s*', '<font color="#999999">&#x25CB;</font> ', text)
            flowables.append(Paragraph(
                '<bullet>&bull;</bullet> ' + parse_inline(escape_xml(text)) if not text.startswith('<font') else '<bullet>&bull;</bullet> ' + text,
                styles['BulletItem']
            ))
            i += 1
            continue

        # Numbered list
        num_match = re.match(r'^(\d+)\.\s+(.+)$', stripped)
        if num_match:
            num = num_match.group(1)
            text = num_match.group(2)
            flowables.append(Paragraph(
                f'<bullet>{num}.</bullet> ' + parse_inline(escape_xml(text)),
                styles['BulletItem']
            ))
            i += 1
            continue

        # Blockquote
        if stripped.startswith('>'):
            text = stripped.lstrip('>').strip()
            bq_style = ParagraphStyle(
                'BlockQuote',
                parent=styles['BodyText2'],
                leftIndent=16,
                borderWidth=0,
                textColor=MEDIUM_GRAY,
                fontName='Helvetica-Oblique',
                fontSize=9,
            )
            flowables.append(Paragraph(parse_inline(escape_xml(text)), bq_style))
            i += 1
            continue

        # Metadata lines (bold key: value)
        meta_match = re.match(r'^\*\*(.+?)\*\*\s*(.+)$', stripped)
        if meta_match and not title_extracted:
            i += 1
            continue

        # Regular paragraph
        para_text = stripped
        # Collect continuation lines
        while (i + 1 < len(lines) and lines[i + 1].strip()
               and not lines[i + 1].strip().startswith('#')
               and not lines[i + 1].strip().startswith('|')
               and not lines[i + 1].strip().startswith('```')
               and not lines[i + 1].strip().startswith('---')
               and not lines[i + 1].strip().startswith('>')
               and not re.match(r'^[-*]\s+', lines[i + 1].strip())
               and not re.match(r'^\d+\.\s+', lines[i + 1].strip())
               and not re.match(r'^\*\*', lines[i + 1].strip())):
            i += 1
            para_text += ' ' + lines[i].strip()

        flowables.append(Paragraph(parse_inline(escape_xml(para_text)), styles['BodyText2']))
        i += 1

    return flowables


# ---------------------------------------------------------------------------
# Title page generation
# ---------------------------------------------------------------------------
def make_title_page(title, subtitle_lines, doc_id, version, date, styles):
    """Create a professional title/cover section."""
    flowables = []
    flowables.append(Spacer(1, 60))

    # Accent line
    flowables.append(HRFlowable(468, ACCENT, 3))
    flowables.append(Spacer(1, 16))

    # Title
    flowables.append(Paragraph(escape_xml(title), styles['DocTitle']))
    flowables.append(Spacer(1, 8))

    # Subtitle lines
    for line in subtitle_lines:
        flowables.append(Paragraph(escape_xml(line), styles['DocSubtitle']))

    flowables.append(Spacer(1, 16))
    flowables.append(HRFlowable(468, ACCENT, 3))
    flowables.append(Spacer(1, 24))

    # Metadata table
    meta_data = []
    if doc_id:
        meta_data.append(['Document ID', doc_id])
    if version:
        meta_data.append(['Version', version])
    if date:
        meta_data.append(['Date', date])
    meta_data.append(['Classification', 'Controlled Unclassified Information (CUI)'])
    meta_data.append(['System', 'Airline Ticket Reservation System (ATRS)'])

    if meta_data:
        meta_table = Table(meta_data, colWidths=[120, 348])
        meta_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), NAVY),
            ('TEXTCOLOR', (1, 0), (1, -1), DARK_GRAY),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('LINEBELOW', (0, 0), (-1, -2), 0.5, BORDER_COLOR),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        flowables.append(meta_table)

    flowables.append(Spacer(1, 30))
    flowables.append(HRFlowable(468, BORDER_COLOR, 0.5))
    flowables.append(Spacer(1, 12))

    return flowables


# ---------------------------------------------------------------------------
# Page templates (header/footer)
# ---------------------------------------------------------------------------
def header_footer(canvas, doc, title="ATRS Documentation"):
    canvas.saveState()
    # Header line
    canvas.setStrokeColor(NAVY)
    canvas.setLineWidth(1.5)
    canvas.line(72, letter[1] - 50, letter[0] - 72, letter[1] - 50)
    # Header text
    canvas.setFont('Helvetica', 7.5)
    canvas.setFillColor(MEDIUM_GRAY)
    canvas.drawString(72, letter[1] - 45, "ATRS — Airline Ticket Reservation System")
    canvas.drawRightString(letter[0] - 72, letter[1] - 45, "FedRAMP Moderate | CUI")

    # Footer
    canvas.setStrokeColor(BORDER_COLOR)
    canvas.setLineWidth(0.5)
    canvas.line(72, 50, letter[0] - 72, 50)
    canvas.setFont('Helvetica', 7.5)
    canvas.setFillColor(MEDIUM_GRAY)
    canvas.drawString(72, 38, f"v1.0 — 2026-02-24")
    canvas.drawCentredString(letter[0] / 2, 38, title)
    canvas.drawRightString(letter[0] - 72, 38, f"Page {doc.page}")
    canvas.restoreState()


# ---------------------------------------------------------------------------
# Extract metadata from markdown
# ---------------------------------------------------------------------------
def extract_metadata(md_text):
    """Extract title, doc_id, version, date from markdown."""
    title = ""
    doc_id = ""
    version = ""
    date = ""
    subtitle_lines = []

    lines = md_text.split('\n')
    for line in lines[:15]:
        stripped = line.strip()
        # Title
        m = re.match(r'^#\s+(.+)$', stripped)
        if m and not title:
            title = m.group(1)
            # Clean title: remove "ATRS — " prefix for cleaner display
            continue

        # Doc ID
        m = re.search(r'\*\*Document ID:\*\*\s*(.+)', stripped)
        if m:
            doc_id = m.group(1).strip()
            continue

        # Version/Date
        m = re.search(r'\*\*Version:\*\*\s*(.+?)\s*\|\s*\*\*Date:\*\*\s*(.+)', stripped)
        if m:
            version = m.group(1).strip()
            date = m.group(2).strip()
            continue

        # FedRAMP control mapping
        m = re.search(r'\*\*FedRAMP Control', stripped)
        if m:
            subtitle_lines.append(stripped.replace('**', '').strip())
            continue

        # Classification
        m = re.search(r'\*\*Classification:\*\*\s*(.+)', stripped)
        if m:
            subtitle_lines.append(f"Classification: {m.group(1).strip()}")
            continue

        m = re.search(r'\*\*FIPS', stripped)
        if m:
            subtitle_lines.append(stripped.replace('**', '').strip())
            continue

        m = re.search(r'\*\*Information System', stripped)
        if m:
            subtitle_lines.append(stripped.replace('**', '').strip())
            continue

    return title, subtitle_lines, doc_id, version, date


# ---------------------------------------------------------------------------
# Generate a single PDF
# ---------------------------------------------------------------------------
def generate_pdf(md_path, output_path):
    """Generate a professional PDF from a markdown file."""
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    title, subtitle_lines, doc_id, version, date = extract_metadata(md_text)
    short_title = title.replace("ATRS — ", "").replace("ATRS —", "").strip()

    styles = get_custom_styles()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        topMargin=65,
        bottomMargin=65,
        leftMargin=72,
        rightMargin=72,
        title=title,
        author="ATRS Security Team",
        subject=short_title,
    )

    story = []

    # Title page section
    story.extend(make_title_page(
        title, subtitle_lines, doc_id, version, date, styles
    ))

    # Convert markdown body to flowables (skip metadata lines at top)
    # Find where the body starts (after the first ---)
    body_start = md_text.find('\n---\n')
    if body_start > 0:
        body_text = md_text[body_start + 5:]
    else:
        body_text = md_text

    story.extend(md_to_flowables(body_text, styles))

    # Build with header/footer
    def _hf(canvas, doc):
        header_footer(canvas, doc, short_title)

    doc.build(story, onFirstPage=_hf, onLaterPages=_hf)
    print(f"  ✓ {os.path.basename(output_path)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def generate_combined_pdf(output_path):
    """Generate a single combined PDF with all ATRS documentation."""
    docs_dir = "/Users/sandipwane/workspace/atrs/docs"

    doc_order = [
        "README.md",
        "ARCHITECTURE.md",
        "API_REFERENCE.md",
        "DATABASE_SCHEMA.md",
        "DEPLOYMENT.md",
        "fedramp/SYSTEM_SECURITY_PLAN.md",
        "fedramp/ACCESS_CONTROL.md",
        "fedramp/AUDIT_ACCOUNTABILITY.md",
        "fedramp/CONFIGURATION_MANAGEMENT.md",
        "fedramp/CONTINGENCY_PLAN.md",
        "fedramp/CONTINUOUS_MONITORING.md",
        "fedramp/IDENTIFICATION_AUTHENTICATION.md",
        "fedramp/INCIDENT_RESPONSE.md",
        "fedramp/PERSONNEL_SECURITY.md",
        "fedramp/PRIVACY_IMPACT_ASSESSMENT.md",
        "fedramp/RISK_ASSESSMENT.md",
        "fedramp/SUPPLY_CHAIN_RISK.md",
        "fedramp/SYSTEM_COMMUNICATIONS_PROTECTION.md",
        "fedramp/SYSTEM_INFORMATION_INTEGRITY.md",
    ]

    styles = get_custom_styles()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        topMargin=65,
        bottomMargin=65,
        leftMargin=72,
        rightMargin=72,
        title="ATRS — FedRAMP Documentation Package",
        author="ATRS Security Team",
        subject="Complete FedRAMP Moderate Documentation",
    )

    story = []

    # ── Cover page ──
    story.append(Spacer(1, 120))
    story.append(HRFlowable(468, ACCENT, 4))
    story.append(Spacer(1, 24))
    story.append(Paragraph("Airline Ticket Reservation System", styles['DocTitle']))
    story.append(Spacer(1, 6))

    cover_subtitle = ParagraphStyle(
        'CoverSub', parent=styles['DocSubtitle'],
        fontSize=14, leading=20, textColor=DARK_BLUE,
    )
    story.append(Paragraph("FedRAMP Documentation Package", cover_subtitle))
    story.append(Spacer(1, 24))
    story.append(HRFlowable(468, ACCENT, 4))
    story.append(Spacer(1, 40))

    # Cover metadata
    cover_meta = [
        ['FedRAMP Level', 'Moderate (NIST SP 800-53 Rev. 5)'],
        ['FIPS 199 Category', 'Moderate'],
        ['System Version', '1.11.0.RELEASE'],
        ['Framework', 'TERASOLUNA GFW 5.10.0.RELEASE'],
        ['Date', '2026-02-24'],
        ['Documents Included', f'{len(doc_order)}'],
        ['Prepared By', 'ATRS Security Team'],
        ['Classification', 'Controlled Unclassified Information (CUI)'],
    ]
    meta_table = Table(cover_meta, colWidths=[160, 308])
    meta_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), NAVY),
        ('TEXTCOLOR', (1, 0), (1, -1), DARK_GRAY),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, BORDER_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(meta_table)
    story.append(PageBreak())

    # ── Table of contents ──
    story.append(Spacer(1, 20))
    story.append(SectionHeading("Table of Contents", level=1, width=468))
    story.append(Spacer(1, 16))

    toc_data = [['#', 'Document', 'Section']]
    toc_labels = [
        ("1", "Document Index", "Overview"),
        ("2", "Architecture & Design", "Core"),
        ("3", "API Reference", "Core"),
        ("4", "Database Schema", "Core"),
        ("5", "Deployment Guide", "Core"),
        ("6", "System Security Plan (SSP)", "FedRAMP"),
        ("7", "Access Control (AC)", "FedRAMP"),
        ("8", "Audit & Accountability (AU)", "FedRAMP"),
        ("9", "Configuration Management (CM)", "FedRAMP"),
        ("10", "Contingency Plan (CP)", "FedRAMP"),
        ("11", "Continuous Monitoring (CA)", "FedRAMP"),
        ("12", "Identification & Authentication (IA)", "FedRAMP"),
        ("13", "Incident Response (IR)", "FedRAMP"),
        ("14", "Personnel Security (PS)", "FedRAMP"),
        ("15", "Privacy Impact Assessment (PIA)", "FedRAMP"),
        ("16", "Risk Assessment (RA)", "FedRAMP"),
        ("17", "Supply Chain Risk (SR)", "FedRAMP"),
        ("18", "System & Communications Protection (SC)", "FedRAMP"),
        ("19", "System & Information Integrity (SI)", "FedRAMP"),
    ]
    for row in toc_labels:
        toc_data.append(list(row))

    toc_table = Table(toc_data, colWidths=[30, 320, 118])
    toc_style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), TABLE_HEADER_BG),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('TEXTCOLOR', (0, 1), (-1, -1), DARK_GRAY),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]
    for i in range(1, len(toc_data)):
        if i % 2 == 0:
            toc_style_cmds.append(('BACKGROUND', (0, i), (-1, i), TABLE_ALT_ROW))
    toc_table.setStyle(TableStyle(toc_style_cmds))
    story.append(toc_table)
    story.append(PageBreak())

    # ── Each document ──
    for idx, md_file in enumerate(doc_order):
        md_path = os.path.join(docs_dir, md_file)
        with open(md_path, 'r', encoding='utf-8') as f:
            md_text = f.read()

        title, subtitle_lines, doc_id, version, date = extract_metadata(md_text)

        # Document divider page / section header
        story.extend(make_title_page(title, subtitle_lines, doc_id, version, date, styles))

        # Body content
        body_start = md_text.find('\n---\n')
        body_text = md_text[body_start + 5:] if body_start > 0 else md_text
        story.extend(md_to_flowables(body_text, styles))

        # Page break between documents (except last)
        if idx < len(doc_order) - 1:
            story.append(PageBreak())

        print(f"  ✓ [{idx+1}/{len(doc_order)}] {md_file}")

    # Build
    def _hf(canvas, doc):
        header_footer(canvas, doc, "ATRS FedRAMP Documentation Package")

    doc.build(story, onFirstPage=_hf, onLaterPages=_hf)


def main():
    docs_dir = "/Users/sandipwane/workspace/atrs/docs"
    pdf_dir = "/Users/sandipwane/workspace/atrs/docs/pdf"

    # Core docs
    core_docs = [
        ("README.md", "00_ATRS_Document_Index.pdf"),
        ("ARCHITECTURE.md", "01_Architecture_Design.pdf"),
        ("API_REFERENCE.md", "02_API_Reference.pdf"),
        ("DATABASE_SCHEMA.md", "03_Database_Schema.pdf"),
        ("DEPLOYMENT.md", "04_Deployment_Guide.pdf"),
    ]

    # FedRAMP docs
    fedramp_docs = [
        ("fedramp/SYSTEM_SECURITY_PLAN.md", "05_System_Security_Plan.pdf"),
        ("fedramp/ACCESS_CONTROL.md", "06_Access_Control.pdf"),
        ("fedramp/AUDIT_ACCOUNTABILITY.md", "07_Audit_Accountability.pdf"),
        ("fedramp/CONFIGURATION_MANAGEMENT.md", "08_Configuration_Management.pdf"),
        ("fedramp/CONTINGENCY_PLAN.md", "09_Contingency_Plan.pdf"),
        ("fedramp/CONTINUOUS_MONITORING.md", "10_Continuous_Monitoring.pdf"),
        ("fedramp/IDENTIFICATION_AUTHENTICATION.md", "11_Identification_Authentication.pdf"),
        ("fedramp/INCIDENT_RESPONSE.md", "12_Incident_Response.pdf"),
        ("fedramp/PERSONNEL_SECURITY.md", "13_Personnel_Security.pdf"),
        ("fedramp/PRIVACY_IMPACT_ASSESSMENT.md", "14_Privacy_Impact_Assessment.pdf"),
        ("fedramp/RISK_ASSESSMENT.md", "15_Risk_Assessment.pdf"),
        ("fedramp/SUPPLY_CHAIN_RISK.md", "16_Supply_Chain_Risk.pdf"),
        ("fedramp/SYSTEM_COMMUNICATIONS_PROTECTION.md", "17_System_Communications_Protection.pdf"),
        ("fedramp/SYSTEM_INFORMATION_INTEGRITY.md", "18_System_Information_Integrity.pdf"),
    ]

    all_docs = core_docs + fedramp_docs

    print(f"\n{'='*60}")
    print(f"  ATRS Documentation PDF Generator")
    print(f"  Generating {len(all_docs)} individual PDFs...")
    print(f"{'='*60}\n")

    for md_file, pdf_file in all_docs:
        md_path = os.path.join(docs_dir, md_file)
        pdf_path = os.path.join(pdf_dir, pdf_file)
        try:
            generate_pdf(md_path, pdf_path)
        except Exception as e:
            print(f"  ✗ {pdf_file}: {e}")

    # Combined PDF
    combined_path = os.path.join(pdf_dir, "ATRS_FedRAMP_Documentation_Package.pdf")
    print(f"\n{'='*60}")
    print(f"  Generating combined PDF...")
    print(f"{'='*60}\n")
    try:
        generate_combined_pdf(combined_path)
        print(f"\n  ✓ Combined PDF: {combined_path}")
    except Exception as e:
        print(f"\n  ✗ Combined PDF failed: {e}")

    print(f"\n{'='*60}")
    print(f"  Done! PDFs saved to: {pdf_dir}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
