"""
CV text extraction service.

Extracts raw text from PDF, DOCX, and DOC files.
"""
import os
import re
import fitz  # PyMuPDF
from docx import Document


# A block whose entire text is just a date range, e.g. "May 2022 – Present"
# or "03/2019 - 08/2021". Used to spot right-aligned date columns (see _page_lines).
_DATE_ONLY_BLOCK = re.compile(
    r"^\s*(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\.?[\s,]*['’]?\d{2,4}"
    r"|\d{1,2}/\d{4}|\d{4})"
    r"\s*(?:to|[-–—])\s*"
    r"(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\.?[\s,]*['’]?\d{2,4}"
    r"|\d{1,2}/\d{4}|\d{4}|present|current)\s*$",
    re.IGNORECASE,
)


def _page_lines(page):
    """Return a page's text lines in reading order.

    PyMuPDF emits blocks in content-stream order, not visual order. Some CV
    templates place employment dates in a right-aligned column that the writer
    emitted first, so those dates surface at the very top of the page — far
    from the experience section, which then parses as having no entries at all
    because section_parser.parse_experience() needs a date to open an entry.

    When a page's blocks already run top-to-bottom they are returned untouched.
    Only when that order is broken do we lift out the date-only blocks and
    reinsert each next to the block sharing its vertical band. This keeps
    left-column date layouts (handled by section_parser._stitch_split_dates)
    on their existing path.
    """
    blocks = [b for b in page.get_text("blocks") if b[6] == 0 and b[4].strip()]
    tops = [b[1] for b in blocks]

    if all(tops[i] <= tops[i + 1] + 2 for i in range(len(tops) - 1)):
        return [b[4].rstrip("\n") for b in blocks]

    floating = [i for i, b in enumerate(blocks) if _DATE_ONLY_BLOCK.match(b[4].strip())]
    placed = set()
    lines = []

    for i, block in enumerate(blocks):
        if i in floating:
            continue
        lines.append(block[4].rstrip("\n"))
        for j in floating:
            if j not in placed and abs(blocks[j][1] - block[1]) < 12:
                lines.append(blocks[j][4].strip())
                placed.add(j)

    # A date block with no matching row is appended rather than dropped
    lines.extend(blocks[j][4].strip() for j in floating if j not in placed)

    return lines


def extract_text_from_pdf(file_path):
    """Extract text from a PDF file using PyMuPDF."""
    lines = []
    try:
        doc = fitz.open(file_path)
        for page in doc:
            lines.extend(_page_lines(page))
        doc.close()
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")

    text = "\n".join(lines)

    # If no text was extracted, the PDF is likely image-based
    if len(text.strip()) < 50:
        raise Exception(
            "This PDF appears to be image-based (no selectable text). "
            "Please upload a text-based PDF created from Word, Google Docs, or similar."
        )

    return text.strip()


# def extract_text_from_docx(file_path):
#     """Extract text from a DOCX file using python-docx."""
#     text = ""
#     try:
#         doc = Document(file_path)
#         for paragraph in doc.paragraphs:
#             if paragraph.text.strip():
#                 text += paragraph.text + "\n"

#         # Also extract text from tables (CVs often use tables for layout)
#         for table in doc.tables:
#             for row in table.rows:
#                 row_text = []
#                 for cell in row.cells:
#                     if cell.text.strip():
#                         row_text.append(cell.text.strip())
#                 if row_text:
#                     text += " | ".join(row_text) + "\n"
#     except Exception as e:
#         raise Exception(f"Failed to extract text from DOCX: {str(e)}")

#     return text.strip()

def extract_text_from_docx(file_path):
    """Extract text from a DOCX file using python-docx."""
    text = ""
    try:
        doc = Document(file_path)
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text += paragraph.text + "\n"

        # Also extract text from tables (CVs often use tables for layout)
        seen = set()
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    cell_text = cell.text.strip()
                    if cell_text and cell_text not in seen:
                        seen.add(cell_text)
                        text += cell_text + "\n"
    except Exception as e:
        raise Exception(f"Failed to extract text from DOCX: {str(e)}")

    return text.strip()


def extract_text_from_doc(file_path):
    """Extract text from a legacy DOC file by converting to DOCX first.
    
    Requires LibreOffice installed on the system.
    Falls back to basic binary text extraction if LibreOffice is not available.
    """
    import subprocess

    # Try converting with LibreOffice
    output_dir = os.path.dirname(file_path)
    try:
        subprocess.run(
            ["soffice", "--headless", "--convert-to", "docx", "--outdir", output_dir, file_path],
            capture_output=True,
            timeout=30,
            check=True,
        )
        # The converted file will have the same name but .docx extension
        docx_path = file_path.rsplit(".", 1)[0] + ".docx"
        if os.path.exists(docx_path):
            text = extract_text_from_docx(docx_path)
            os.remove(docx_path)  # Clean up the converted file
            return text
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Fallback: basic binary text extraction for .doc files
    try:
        with open(file_path, "rb") as f:
            raw = f.read()
        # Extract printable ASCII text chunks from the binary
        text = ""
        current_chunk = ""
        for byte in raw:
            if 32 <= byte <= 126 or byte in (10, 13):
                current_chunk += chr(byte)
            else:
                if len(current_chunk) > 20:  # Only keep meaningful chunks
                    text += current_chunk + "\n"
                current_chunk = ""
        if len(current_chunk) > 20:
            text += current_chunk
        return text.strip()
    except Exception as e:
        raise Exception(f"Failed to extract text from DOC: {str(e)}")


def extract_text(file_path, file_format):
    """Extract text from a CV file based on its format.
    
    Args:
        file_path: Path to the uploaded file
        file_format: File extension (pdf, docx, doc)
    
    Returns:
        Extracted text as a string
    """
    if file_format == "pdf":
        return extract_text_from_pdf(file_path)
    elif file_format == "docx":
        return extract_text_from_docx(file_path)
    elif file_format == "doc":
        return extract_text_from_doc(file_path)
    else:
        raise Exception(f"Unsupported file format: {file_format}")
