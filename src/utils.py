# Filename: src/utils.py
import re
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar

def parse_pdf_to_sections(pdf_path):
    """
    Parse a PDF into a list of sections.
    Returns list of dicts: { 'page': int, 'heading': str, 'text': str }
    """
    sections = []
    current = None

    for page_layout in extract_pages(pdf_path):
        page_no = page_layout.pageid
        for element in page_layout:
            if not isinstance(element, LTTextContainer):
                continue
            text = element.get_text().strip()
            # detect heading by average font size
            sizes = [c.size for c in element if isinstance(c, LTChar)]
            avg_size = sum(sizes)/len(sizes) if sizes else 0
            if avg_size > 12:  # threshold for heading
                # start new section
                if current:
                    sections.append(current)
                current = { 'page': page_no, 'heading': text, 'text': '' }
            else:
                if current:
                    current['text'] += text + "\n"
    # append last
    if current:
        sections.append(current)
    return sections