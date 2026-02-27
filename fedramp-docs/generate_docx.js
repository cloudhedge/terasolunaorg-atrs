#!/usr/bin/env node
/**
 * Generate a combined Word (.docx) document from all ATRS FedRAMP markdown docs.
 *
 * Key advantage over PDF: Courier New is a true monospace font in Word,
 * so ASCII-art diagrams (box-drawing characters ┌│─▶) render with correct alignment.
 *
 * Usage: node generate_docx.js
 * Output: docs/pdf/ATRS_FedRAMP_Documentation_Package.docx
 */

const fs = require("fs");
const path = require("path");
const {
  Document,
  Packer,
  Paragraph,
  TextRun,
  HeadingLevel,
  Table,
  TableRow,
  TableCell,
  WidthType,
  AlignmentType,
  BorderStyle,
  ShadingType,
  PageBreak,
  Header,
  Footer,
  TabStopType,
  TabStopPosition,
  TableOfContents,
  LevelFormat,
  NumberFormat,
  convertInchesToTwip,
  ExternalHyperlink,
} = require("docx");

// ---------------------------------------------------------------------------
// Colour palette (matches PDF generator)
// ---------------------------------------------------------------------------
const NAVY = "1B2A4A";
const DARK_BLUE = "2C3E6B";
const MEDIUM_BLUE = "3D5A99";
const LIGHT_BLUE = "E8EDF5";
const ACCENT = "D4A843";
const DARK_GRAY = "333333";
const MEDIUM_GRAY = "666666";
const LIGHT_GRAY = "F5F5F5";
const TABLE_HEADER_BG = "2C3E6B";
const TABLE_ALT_ROW = "F0F3F8";
const BORDER_COLOR = "CBD5E1";
const CODE_BG = "F1F5F9";
const CODE_FG = "1E293B";
const WHITE = "FFFFFF";

// ---------------------------------------------------------------------------
// Document order (same as combined PDF)
// ---------------------------------------------------------------------------
const DOCS_DIR = path.join(__dirname, "docs");

const DOC_ORDER = [
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
];

const TOC_LABELS = [
  ["1", "Document Index", "Overview"],
  ["2", "Architecture & Design", "Core"],
  ["3", "API Reference", "Core"],
  ["4", "Database Schema", "Core"],
  ["5", "Deployment Guide", "Core"],
  ["6", "System Security Plan (SSP)", "FedRAMP"],
  ["7", "Access Control (AC)", "FedRAMP"],
  ["8", "Audit & Accountability (AU)", "FedRAMP"],
  ["9", "Configuration Management (CM)", "FedRAMP"],
  ["10", "Contingency Plan (CP)", "FedRAMP"],
  ["11", "Continuous Monitoring (CA)", "FedRAMP"],
  ["12", "Identification & Authentication (IA)", "FedRAMP"],
  ["13", "Incident Response (IR)", "FedRAMP"],
  ["14", "Personnel Security (PS)", "FedRAMP"],
  ["15", "Privacy Impact Assessment (PIA)", "FedRAMP"],
  ["16", "Risk Assessment (RA)", "FedRAMP"],
  ["17", "Supply Chain Risk (SR)", "FedRAMP"],
  ["18", "System & Communications Protection (SC)", "FedRAMP"],
  ["19", "System & Information Integrity (SI)", "FedRAMP"],
];

// ---------------------------------------------------------------------------
// Markdown inline parsing → TextRun[]
// ---------------------------------------------------------------------------
function parseInline(text) {
  const runs = [];
  // Tokenize: split on bold, italic, inline code, links
  // Order: code first (protect from bold/italic), then bold+italic, bold, italic, links
  const pattern =
    /(`[^`]+`)|(\*\*\*[^*]+?\*\*\*)|(\*\*[^*]+?\*\*)|(\*[^*]+?\*)|(\[[^\]]+\]\([^)]+\))/g;

  let lastIndex = 0;
  let match;
  while ((match = pattern.exec(text)) !== null) {
    // Plain text before this match
    if (match.index > lastIndex) {
      runs.push(new TextRun({ text: text.slice(lastIndex, match.index), size: 19, font: "Calibri" }));
    }

    if (match[1]) {
      // Inline code
      const code = match[1].slice(1, -1);
      runs.push(
        new TextRun({
          text: code,
          font: "Courier New",
          size: 17,
          color: CODE_FG,
          shading: { type: ShadingType.CLEAR, fill: CODE_BG },
        })
      );
    } else if (match[2]) {
      // Bold + italic
      runs.push(
        new TextRun({
          text: match[2].slice(3, -3),
          bold: true,
          italics: true,
          size: 19,
          font: "Calibri",
        })
      );
    } else if (match[3]) {
      // Bold
      runs.push(
        new TextRun({
          text: match[3].slice(2, -2),
          bold: true,
          size: 19,
          font: "Calibri",
        })
      );
    } else if (match[4]) {
      // Italic
      runs.push(
        new TextRun({
          text: match[4].slice(1, -1),
          italics: true,
          size: 19,
          font: "Calibri",
        })
      );
    } else if (match[5]) {
      // Link [text](url) → just the text
      const linkMatch = match[5].match(/\[([^\]]+)\]\(([^)]+)\)/);
      if (linkMatch) {
        runs.push(
          new TextRun({
            text: linkMatch[1],
            color: MEDIUM_BLUE,
            size: 19,
            font: "Calibri",
          })
        );
      }
    }
    lastIndex = match.index + match[0].length;
  }
  // Trailing plain text
  if (lastIndex < text.length) {
    runs.push(new TextRun({ text: text.slice(lastIndex), size: 19, font: "Calibri" }));
  }
  if (runs.length === 0) {
    runs.push(new TextRun({ text: text, size: 19, font: "Calibri" }));
  }
  return runs;
}

// ---------------------------------------------------------------------------
// Metadata extraction (mirrors Python version)
// ---------------------------------------------------------------------------
function extractMetadata(mdText) {
  const lines = mdText.split("\n").slice(0, 15);
  let title = "";
  let docId = "";
  let version = "";
  let date = "";
  const subtitleLines = [];

  for (const line of lines) {
    const s = line.trim();
    let m;
    if (!title && (m = s.match(/^#\s+(.+)$/))) {
      title = m[1];
      continue;
    }
    if ((m = s.match(/\*\*Document ID:\*\*\s*(.+)/))) {
      docId = m[1].trim();
      continue;
    }
    if (
      (m = s.match(
        /\*\*Version:\*\*\s*(.+?)\s*\|\s*\*\*Date:\*\*\s*(.+)/
      ))
    ) {
      version = m[1].trim();
      date = m[2].trim();
      continue;
    }
    if (s.match(/\*\*FedRAMP Control/)) {
      subtitleLines.push(s.replace(/\*\*/g, "").trim());
      continue;
    }
    if ((m = s.match(/\*\*Classification:\*\*\s*(.+)/))) {
      subtitleLines.push(`Classification: ${m[1].trim()}`);
      continue;
    }
    if (s.match(/\*\*FIPS/)) {
      subtitleLines.push(s.replace(/\*\*/g, "").trim());
      continue;
    }
    if (s.match(/\*\*Information System/)) {
      subtitleLines.push(s.replace(/\*\*/g, "").trim());
      continue;
    }
  }
  return { title, subtitleLines, docId, version, date };
}

// ---------------------------------------------------------------------------
// Table border helper
// ---------------------------------------------------------------------------
const thinBorder = {
  style: BorderStyle.SINGLE,
  size: 1,
  color: BORDER_COLOR,
};
const noBorder = { style: BorderStyle.NONE, size: 0 };

function tableCellBorders() {
  return {
    top: thinBorder,
    bottom: thinBorder,
    left: thinBorder,
    right: thinBorder,
  };
}

// ---------------------------------------------------------------------------
// Parse markdown table lines → docx Table
// ---------------------------------------------------------------------------
function parseTable(tableLines) {
  const rows = [];
  for (const line of tableLines) {
    let l = line.trim();
    if (l.startsWith("|")) l = l.slice(1);
    if (l.endsWith("|")) l = l.slice(0, -1);
    rows.push(l.split("|").map((c) => c.trim()));
  }
  if (rows.length < 2) return null;

  // Check separator row
  const isSep = rows[1].every((c) => /^[\s:\-]+$/.test(c));
  const header = rows[0];
  const dataRows = isSep ? rows.slice(2) : rows.slice(1);

  const numCols = header.length;
  const colWidth = Math.floor(9000 / numCols); // distribute ~9000 twips

  const docxRows = [];

  // Header row
  docxRows.push(
    new TableRow({
      tableHeader: true,
      children: header.map(
        (h) =>
          new TableCell({
            shading: { fill: TABLE_HEADER_BG, type: ShadingType.CLEAR },
            borders: tableCellBorders(),
            width: { size: colWidth, type: WidthType.DXA },
            children: [
              new Paragraph({
                children: [
                  new TextRun({
                    text: h.replace(/\*\*/g, ""),
                    bold: true,
                    color: WHITE,
                    size: 17,
                    font: "Calibri",
                  }),
                ],
                spacing: { before: 40, after: 40 },
              }),
            ],
          })
      ),
    })
  );

  // Data rows
  dataRows.forEach((row, idx) => {
    // Pad short rows
    while (row.length < numCols) row.push("");
    const cells = row.slice(0, numCols);
    const fill = idx % 2 === 1 ? TABLE_ALT_ROW : WHITE;
    docxRows.push(
      new TableRow({
        children: cells.map(
          (c) =>
            new TableCell({
              shading: { fill, type: ShadingType.CLEAR },
              borders: tableCellBorders(),
              width: { size: colWidth, type: WidthType.DXA },
              children: [
                new Paragraph({
                  children: parseInline(c),
                  spacing: { before: 30, after: 30 },
                }),
              ],
            })
        ),
      })
    );
  });

  return new Table({
    rows: docxRows,
    width: { size: 100, type: WidthType.PERCENTAGE },
  });
}

// ---------------------------------------------------------------------------
// Code block → Paragraph[] (one per line, Courier New 8pt, gray bg)
// ---------------------------------------------------------------------------
function codeBlockToParagraphs(codeLines) {
  return codeLines.map(
    (line) =>
      new Paragraph({
        children: [
          new TextRun({
            text: line || " ", // preserve empty lines
            font: "Courier New",
            size: 16, // 8pt
            color: CODE_FG,
          }),
        ],
        shading: { type: ShadingType.CLEAR, fill: CODE_BG },
        spacing: { before: 0, after: 0, line: 220 },
        indent: { left: convertInchesToTwip(0.15) },
      })
  );
}

// ---------------------------------------------------------------------------
// Horizontal rule paragraph
// ---------------------------------------------------------------------------
function horizontalRule() {
  return new Paragraph({
    children: [],
    border: {
      bottom: { style: BorderStyle.SINGLE, size: 1, color: BORDER_COLOR },
    },
    spacing: { before: 120, after: 120 },
  });
}

// ---------------------------------------------------------------------------
// Markdown body → Paragraph[] (main converter)
// ---------------------------------------------------------------------------
function mdToChildren(mdText) {
  const children = [];
  const lines = mdText.split("\n");
  let i = 0;
  let titleExtracted = false;
  let inCodeBlock = false;
  let codeLines = [];

  while (i < lines.length) {
    const line = lines[i];

    // Code block toggle
    if (line.trim().startsWith("```")) {
      if (inCodeBlock) {
        // Add a small spacer before code block
        children.push(
          new Paragraph({ children: [], spacing: { before: 60, after: 0 } })
        );
        children.push(...codeBlockToParagraphs(codeLines));
        children.push(
          new Paragraph({ children: [], spacing: { before: 0, after: 60 } })
        );
        codeLines = [];
        inCodeBlock = false;
      } else {
        inCodeBlock = true;
        codeLines = [];
      }
      i++;
      continue;
    }

    if (inCodeBlock) {
      codeLines.push(line);
      i++;
      continue;
    }

    const stripped = line.trim();

    // Skip empty lines
    if (!stripped) {
      i++;
      continue;
    }

    // Horizontal rule
    if (/^---+$/.test(stripped) || /^\*\*\*+$/.test(stripped)) {
      children.push(horizontalRule());
      i++;
      continue;
    }

    // Headings
    const headingMatch = stripped.match(/^(#{1,4})\s+(.+)$/);
    if (headingMatch) {
      const level = headingMatch[1].length;
      const text = headingMatch[2].trim();

      if (level === 1 && !titleExtracted) {
        titleExtracted = true;
        children.push(
          new Paragraph({
            children: [
              new TextRun({
                text,
                bold: true,
                size: 32,
                color: NAVY,
                font: "Calibri",
              }),
            ],
            heading: HeadingLevel.HEADING_1,
            spacing: { before: 80, after: 160 },
          })
        );
        i++;
        continue;
      }

      const headingConfig = {
        1: { heading: HeadingLevel.HEADING_1, size: 32, color: NAVY },
        2: { heading: HeadingLevel.HEADING_2, size: 26, color: DARK_BLUE },
        3: { heading: HeadingLevel.HEADING_3, size: 22, color: MEDIUM_BLUE },
        4: { heading: HeadingLevel.HEADING_3, size: 20, color: MEDIUM_BLUE },
      };
      const cfg = headingConfig[level] || headingConfig[4];
      children.push(
        new Paragraph({
          children: [
            new TextRun({
              text,
              bold: true,
              size: cfg.size,
              color: cfg.color,
              font: "Calibri",
            }),
          ],
          heading: cfg.heading,
          spacing: { before: 240, after: 80 },
        })
      );
      i++;
      continue;
    }

    // Table detection
    if (stripped.startsWith("|") && stripped.indexOf("|", 1) > 0) {
      const tableLines = [];
      while (i < lines.length && lines[i].trim().startsWith("|")) {
        tableLines.push(lines[i]);
        i++;
      }
      const tbl = parseTable(tableLines);
      if (tbl) {
        children.push(
          new Paragraph({ children: [], spacing: { before: 60, after: 0 } })
        );
        children.push(tbl);
        children.push(
          new Paragraph({ children: [], spacing: { before: 0, after: 60 } })
        );
      }
      continue;
    }

    // Bullet point
    const bulletMatch = stripped.match(/^[-*]\s+(.+)$/);
    if (bulletMatch) {
      let text = bulletMatch[1];
      // Handle checkboxes
      text = text.replace(/^\[x\]\s*/, "\u2713 ");
      text = text.replace(/^\[\s*\]\s*/, "\u25CB ");
      children.push(
        new Paragraph({
          children: parseInline(text),
          numbering: { reference: "bullets", level: 0 },
          spacing: { before: 20, after: 20 },
        })
      );
      i++;
      continue;
    }

    // Nested bullet (2+ spaces)
    const nestedBulletMatch = line.match(/^(\s{2,})[-*]\s+(.+)$/);
    if (nestedBulletMatch) {
      const indent = nestedBulletMatch[1].length;
      const level = Math.min(Math.floor(indent / 2), 2);
      children.push(
        new Paragraph({
          children: parseInline(nestedBulletMatch[2]),
          numbering: { reference: "bullets", level },
          spacing: { before: 20, after: 20 },
        })
      );
      i++;
      continue;
    }

    // Numbered list
    const numMatch = stripped.match(/^(\d+)\.\s+(.+)$/);
    if (numMatch) {
      children.push(
        new Paragraph({
          children: parseInline(numMatch[2]),
          numbering: { reference: "numbering", level: 0 },
          spacing: { before: 20, after: 20 },
        })
      );
      i++;
      continue;
    }

    // Blockquote
    if (stripped.startsWith(">")) {
      const text = stripped.replace(/^>\s*/, "");
      children.push(
        new Paragraph({
          children: [
            new TextRun({
              text,
              italics: true,
              color: MEDIUM_GRAY,
              size: 18,
              font: "Calibri",
            }),
          ],
          indent: { left: convertInchesToTwip(0.3) },
          spacing: { before: 60, after: 60 },
          border: {
            left: {
              style: BorderStyle.SINGLE,
              size: 3,
              color: BORDER_COLOR,
            },
          },
        })
      );
      i++;
      continue;
    }

    // Metadata lines (bold key: value pattern in first few lines)
    const metaMatch = stripped.match(/^\*\*(.+?)\*\*\s*(.+)$/);
    if (metaMatch && !titleExtracted) {
      i++;
      continue;
    }

    // Regular paragraph — collect continuation lines
    let paraText = stripped;
    while (
      i + 1 < lines.length &&
      lines[i + 1].trim() &&
      !lines[i + 1].trim().startsWith("#") &&
      !lines[i + 1].trim().startsWith("|") &&
      !lines[i + 1].trim().startsWith("```") &&
      !lines[i + 1].trim().startsWith("---") &&
      !lines[i + 1].trim().startsWith(">") &&
      !/^[-*]\s+/.test(lines[i + 1].trim()) &&
      !/^\d+\.\s+/.test(lines[i + 1].trim())
    ) {
      i++;
      paraText += " " + lines[i].trim();
    }

    children.push(
      new Paragraph({
        children: parseInline(paraText),
        spacing: { before: 40, after: 60 },
      })
    );
    i++;
  }

  return children;
}

// ---------------------------------------------------------------------------
// Build cover page children
// ---------------------------------------------------------------------------
function buildCoverPage() {
  const children = [];

  // Spacer
  children.push(new Paragraph({ children: [], spacing: { before: 1200 } }));

  // Gold accent line
  children.push(
    new Paragraph({
      children: [],
      border: {
        bottom: { style: BorderStyle.SINGLE, size: 6, color: ACCENT },
      },
      spacing: { after: 300 },
    })
  );

  // Title
  children.push(
    new Paragraph({
      children: [
        new TextRun({
          text: "Airline Ticket Reservation System",
          bold: true,
          size: 44,
          color: NAVY,
          font: "Calibri",
        }),
      ],
      spacing: { after: 120 },
    })
  );

  // Subtitle
  children.push(
    new Paragraph({
      children: [
        new TextRun({
          text: "FedRAMP Documentation Package",
          size: 28,
          color: DARK_BLUE,
          font: "Calibri",
        }),
      ],
      spacing: { after: 300 },
    })
  );

  // Gold accent line
  children.push(
    new Paragraph({
      children: [],
      border: {
        bottom: { style: BorderStyle.SINGLE, size: 6, color: ACCENT },
      },
      spacing: { after: 500 },
    })
  );

  // Metadata table
  const metaData = [
    ["FedRAMP Level", "Moderate (NIST SP 800-53 Rev. 5)"],
    ["FIPS 199 Category", "Moderate"],
    ["System Version", "1.11.0.RELEASE"],
    ["Framework", "TERASOLUNA GFW 5.10.0.RELEASE"],
    ["Date", "2026-02-25"],
    ["Documents Included", `${DOC_ORDER.length}`],
    ["Prepared By", "ATRS Security Team"],
    ["Classification", "Controlled Unclassified Information (CUI)"],
  ];

  const metaRows = metaData.map(
    ([key, val]) =>
      new TableRow({
        children: [
          new TableCell({
            width: { size: 3000, type: WidthType.DXA },
            borders: {
              top: noBorder,
              left: noBorder,
              right: noBorder,
              bottom: thinBorder,
            },
            children: [
              new Paragraph({
                children: [
                  new TextRun({
                    text: key,
                    bold: true,
                    size: 20,
                    color: NAVY,
                    font: "Calibri",
                  }),
                ],
                spacing: { before: 60, after: 60 },
              }),
            ],
          }),
          new TableCell({
            width: { size: 6000, type: WidthType.DXA },
            borders: {
              top: noBorder,
              left: noBorder,
              right: noBorder,
              bottom: thinBorder,
            },
            children: [
              new Paragraph({
                children: [
                  new TextRun({
                    text: val,
                    size: 20,
                    color: DARK_GRAY,
                    font: "Calibri",
                  }),
                ],
                spacing: { before: 60, after: 60 },
              }),
            ],
          }),
        ],
      })
  );

  children.push(
    new Table({
      rows: metaRows,
      width: { size: 100, type: WidthType.PERCENTAGE },
    })
  );

  // Page break
  children.push(
    new Paragraph({ children: [new PageBreak()] })
  );

  return children;
}

// ---------------------------------------------------------------------------
// Build TOC page children
// ---------------------------------------------------------------------------
function buildTocPage() {
  const children = [];

  children.push(
    new Paragraph({
      children: [
        new TextRun({
          text: "Table of Contents",
          bold: true,
          size: 32,
          color: NAVY,
          font: "Calibri",
        }),
      ],
      heading: HeadingLevel.HEADING_1,
      spacing: { before: 200, after: 300 },
    })
  );

  // TOC table
  const numCols = 3;
  const headerRow = new TableRow({
    tableHeader: true,
    children: ["#", "Document", "Section"].map(
      (h) =>
        new TableCell({
          shading: { fill: TABLE_HEADER_BG, type: ShadingType.CLEAR },
          borders: tableCellBorders(),
          children: [
            new Paragraph({
              children: [
                new TextRun({
                  text: h,
                  bold: true,
                  color: WHITE,
                  size: 18,
                  font: "Calibri",
                }),
              ],
              spacing: { before: 50, after: 50 },
            }),
          ],
        })
    ),
  });

  const dataRows = TOC_LABELS.map(
    ([num, doc, section], idx) =>
      new TableRow({
        children: [num, doc, section].map(
          (text) =>
            new TableCell({
              shading: {
                fill: idx % 2 === 1 ? TABLE_ALT_ROW : WHITE,
                type: ShadingType.CLEAR,
              },
              borders: tableCellBorders(),
              children: [
                new Paragraph({
                  children: [
                    new TextRun({
                      text,
                      size: 18,
                      color: DARK_GRAY,
                      font: "Calibri",
                    }),
                  ],
                  spacing: { before: 40, after: 40 },
                }),
              ],
            })
        ),
      })
  );

  children.push(
    new Table({
      rows: [headerRow, ...dataRows],
      width: { size: 100, type: WidthType.PERCENTAGE },
    })
  );

  children.push(
    new Paragraph({ children: [new PageBreak()] })
  );

  return children;
}

// ---------------------------------------------------------------------------
// Build document section title page
// ---------------------------------------------------------------------------
function buildDocTitleSection(metadata) {
  const { title, subtitleLines, docId, version, date } = metadata;
  const children = [];

  // Accent bar
  children.push(
    new Paragraph({
      children: [],
      border: {
        bottom: { style: BorderStyle.SINGLE, size: 4, color: ACCENT },
      },
      spacing: { before: 200, after: 200 },
    })
  );

  // Title
  children.push(
    new Paragraph({
      children: [
        new TextRun({
          text: title,
          bold: true,
          size: 36,
          color: NAVY,
          font: "Calibri",
        }),
      ],
      spacing: { after: 100 },
    })
  );

  // Subtitle lines
  for (const sub of subtitleLines) {
    children.push(
      new Paragraph({
        children: [
          new TextRun({
            text: sub,
            size: 18,
            color: MEDIUM_GRAY,
            font: "Calibri",
          }),
        ],
        spacing: { after: 40 },
      })
    );
  }

  // Accent bar
  children.push(
    new Paragraph({
      children: [],
      border: {
        bottom: { style: BorderStyle.SINGLE, size: 4, color: ACCENT },
      },
      spacing: { before: 200, after: 200 },
    })
  );

  // Metadata mini-table
  const metaEntries = [];
  if (docId) metaEntries.push(["Document ID", docId]);
  if (version) metaEntries.push(["Version", version]);
  if (date) metaEntries.push(["Date", date]);
  metaEntries.push(["Classification", "CUI"]);
  metaEntries.push(["System", "ATRS"]);

  const metaRows = metaEntries.map(
    ([key, val]) =>
      new TableRow({
        children: [
          new TableCell({
            width: { size: 2500, type: WidthType.DXA },
            borders: {
              top: noBorder,
              left: noBorder,
              right: noBorder,
              bottom: thinBorder,
            },
            children: [
              new Paragraph({
                children: [
                  new TextRun({
                    text: key,
                    bold: true,
                    size: 18,
                    color: NAVY,
                    font: "Calibri",
                  }),
                ],
                spacing: { before: 40, after: 40 },
              }),
            ],
          }),
          new TableCell({
            width: { size: 6500, type: WidthType.DXA },
            borders: {
              top: noBorder,
              left: noBorder,
              right: noBorder,
              bottom: thinBorder,
            },
            children: [
              new Paragraph({
                children: [
                  new TextRun({
                    text: val,
                    size: 18,
                    color: DARK_GRAY,
                    font: "Calibri",
                  }),
                ],
                spacing: { before: 40, after: 40 },
              }),
            ],
          }),
        ],
      })
  );

  if (metaRows.length > 0) {
    children.push(
      new Table({
        rows: metaRows,
        width: { size: 100, type: WidthType.PERCENTAGE },
      })
    );
  }

  children.push(
    new Paragraph({ children: [], spacing: { before: 200, after: 200 } })
  );

  return children;
}

// ---------------------------------------------------------------------------
// Main: assemble document
// ---------------------------------------------------------------------------
async function main() {
  console.log("=".repeat(60));
  console.log("  ATRS FedRAMP Documentation — DOCX Generator");
  console.log("=".repeat(60));

  const allChildren = [];

  // Cover page
  allChildren.push(...buildCoverPage());

  // TOC
  allChildren.push(...buildTocPage());

  // Each document
  DOC_ORDER.forEach((mdFile, idx) => {
    const mdPath = path.join(DOCS_DIR, mdFile);
    const mdText = fs.readFileSync(mdPath, "utf-8");

    const metadata = extractMetadata(mdText);

    // Title section
    allChildren.push(...buildDocTitleSection(metadata));

    // Body (skip metadata header — find first ---)
    const bodyStart = mdText.indexOf("\n---\n");
    const bodyText = bodyStart > 0 ? mdText.slice(bodyStart + 5) : mdText;
    allChildren.push(...mdToChildren(bodyText));

    // Page break between documents (except last)
    if (idx < DOC_ORDER.length - 1) {
      allChildren.push(
        new Paragraph({ children: [new PageBreak()] })
      );
    }

    console.log(`  \u2713 [${idx + 1}/${DOC_ORDER.length}] ${mdFile}`);
  });

  // Build document
  const doc = new Document({
    creator: "ATRS Security Team",
    title: "ATRS — FedRAMP Documentation Package",
    description: "Complete FedRAMP Moderate Documentation for ATRS",
    styles: {
      default: {
        document: {
          run: {
            font: "Calibri",
            size: 19,
            color: DARK_GRAY,
          },
        },
        heading1: {
          run: {
            font: "Calibri",
            size: 32,
            bold: true,
            color: NAVY,
          },
          paragraph: {
            spacing: { before: 360, after: 120 },
          },
        },
        heading2: {
          run: {
            font: "Calibri",
            size: 26,
            bold: true,
            color: DARK_BLUE,
          },
          paragraph: {
            spacing: { before: 280, after: 80 },
          },
        },
        heading3: {
          run: {
            font: "Calibri",
            size: 22,
            bold: true,
            color: MEDIUM_BLUE,
          },
          paragraph: {
            spacing: { before: 200, after: 60 },
          },
        },
      },
    },
    numbering: {
      config: [
        {
          reference: "bullets",
          levels: [
            {
              level: 0,
              format: LevelFormat.BULLET,
              text: "\u2022",
              alignment: AlignmentType.LEFT,
              style: { paragraph: { indent: { left: convertInchesToTwip(0.5), hanging: convertInchesToTwip(0.25) } } },
            },
            {
              level: 1,
              format: LevelFormat.BULLET,
              text: "\u25E6",
              alignment: AlignmentType.LEFT,
              style: { paragraph: { indent: { left: convertInchesToTwip(1.0), hanging: convertInchesToTwip(0.25) } } },
            },
            {
              level: 2,
              format: LevelFormat.BULLET,
              text: "\u25AA",
              alignment: AlignmentType.LEFT,
              style: { paragraph: { indent: { left: convertInchesToTwip(1.5), hanging: convertInchesToTwip(0.25) } } },
            },
          ],
        },
        {
          reference: "numbering",
          levels: [
            {
              level: 0,
              format: LevelFormat.DECIMAL,
              text: "%1.",
              alignment: AlignmentType.LEFT,
              style: { paragraph: { indent: { left: convertInchesToTwip(0.5), hanging: convertInchesToTwip(0.25) } } },
            },
          ],
        },
      ],
    },
    sections: [
      {
        properties: {
          page: {
            margin: {
              top: convertInchesToTwip(0.9),
              bottom: convertInchesToTwip(0.9),
              left: convertInchesToTwip(1),
              right: convertInchesToTwip(1),
            },
          },
        },
        headers: {
          default: new Header({
            children: [
              new Paragraph({
                children: [
                  new TextRun({
                    text: "ATRS \u2014 Airline Ticket Reservation System",
                    size: 15,
                    color: MEDIUM_GRAY,
                    font: "Calibri",
                  }),
                  new TextRun({
                    text: "\t",
                  }),
                  new TextRun({
                    text: "FedRAMP Moderate | CUI",
                    size: 15,
                    color: MEDIUM_GRAY,
                    font: "Calibri",
                  }),
                ],
                tabStops: [
                  {
                    type: TabStopType.RIGHT,
                    position: TabStopPosition.MAX,
                  },
                ],
                border: {
                  bottom: {
                    style: BorderStyle.SINGLE,
                    size: 2,
                    color: NAVY,
                  },
                },
                spacing: { after: 200 },
              }),
            ],
          }),
        },
        footers: {
          default: new Footer({
            children: [
              new Paragraph({
                children: [
                  new TextRun({
                    text: "v1.0 \u2014 2026-02-25",
                    size: 15,
                    color: MEDIUM_GRAY,
                    font: "Calibri",
                  }),
                  new TextRun({
                    text: "\t",
                  }),
                  new TextRun({
                    text: "ATRS FedRAMP Documentation Package",
                    size: 15,
                    color: MEDIUM_GRAY,
                    font: "Calibri",
                  }),
                ],
                tabStops: [
                  {
                    type: TabStopType.RIGHT,
                    position: TabStopPosition.MAX,
                  },
                ],
                border: {
                  top: {
                    style: BorderStyle.SINGLE,
                    size: 1,
                    color: BORDER_COLOR,
                  },
                },
                spacing: { before: 200 },
              }),
            ],
          }),
        },
        children: allChildren,
      },
    ],
  });

  // Write file
  const outDir = path.join(__dirname, "docs", "pdf");
  if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
  }
  const outPath = path.join(outDir, "ATRS_FedRAMP_Documentation_Package.docx");

  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(outPath, buffer);

  console.log("\n" + "=".repeat(60));
  console.log(`  \u2713 Generated: ${outPath}`);
  console.log(`  \u2713 Size: ${(buffer.length / 1024).toFixed(0)} KB`);
  console.log("=".repeat(60) + "\n");
}

main().catch((err) => {
  console.error("Failed to generate DOCX:", err);
  process.exit(1);
});
