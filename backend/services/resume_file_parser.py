from __future__ import annotations

import re
import zipfile
from dataclasses import dataclass, field
from io import BytesIO
import xml.etree.ElementTree as ET


@dataclass(slots=True)
class ParsedResume:
    text: str
    file_name: str
    file_type: str
    warnings: list[str] = field(default_factory=list)


def parse_resume_file(file_name: str, content: bytes) -> ParsedResume:
    if not content:
        raise ValueError('Resume upload was empty. Upload a PDF, DOCX, or TXT resume.')

    extension = file_name.rsplit('.', 1)[-1].lower() if '.' in file_name else ''
    if extension == 'txt':
        text = _clean_text(_decode_text(content))
        _ensure_extractable(text, 'TXT')
        return ParsedResume(text, file_name, 'txt')
    if extension == 'docx':
        text = _clean_text(_parse_docx(content))
        _ensure_extractable(text, 'DOCX')
        return ParsedResume(text, file_name, 'docx')
    if extension == 'pdf':
        text, warnings = _parse_pdf(content)
        text = _clean_text(text)
        _ensure_extractable(text, 'PDF')
        return ParsedResume(text, file_name, 'pdf', warnings)
    raise ValueError('Unsupported resume file type. Upload PDF, DOCX, or TXT.')


def _decode_text(content: bytes) -> str:
    for encoding in ('utf-8-sig', 'utf-16', 'latin-1'):
        try:
            return content.decode(encoding).strip()
        except UnicodeDecodeError:
            continue
    return content.decode('utf-8', errors='ignore').strip()


def _parse_docx(content: bytes) -> str:
    try:
        with zipfile.ZipFile(BytesIO(content)) as archive:
            xml = archive.read('word/document.xml')
    except (KeyError, zipfile.BadZipFile) as exc:
        raise ValueError('Could not parse DOCX resume. Upload a valid .docx file.') from exc

    try:
        root = ET.fromstring(xml)
    except ET.ParseError as exc:
        raise ValueError('Could not parse DOCX resume text.') from exc

    namespace = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    paragraphs: list[str] = []
    for paragraph in root.findall('.//w:p', namespace):
        runs = [node.text or '' for node in paragraph.findall('.//w:t', namespace)]
        text = ''.join(runs).strip()
        if text:
            paragraphs.append(text)
    return '\n'.join(paragraphs)


def _parse_pdf(content: bytes) -> tuple[str, list[str]]:
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        text = _parse_pdf_without_dependency(content)
        return text, ['PDF parser dependency is unavailable. Used limited fallback extraction.']

    try:
        reader = PdfReader(BytesIO(content))
        text = '\n'.join(page.extract_text() or '' for page in reader.pages)
    except Exception as exc:
        raise ValueError('Could not parse PDF resume. Upload a valid text-based PDF, DOCX, or TXT file.') from exc

    warnings = []
    if not text.strip():
        warnings.append('PDF text extraction returned no text. Scanned PDFs need OCR, which is not enabled.')
    return text, warnings


def _parse_pdf_without_dependency(content: bytes) -> str:
    decoded = _decode_text(content)
    stream_text = ' '.join(re.findall(r'\(([^()]{3,})\)\s*Tj', decoded))
    if stream_text.strip():
        return stream_text
    tokens = re.findall(r'[A-Za-z][A-Za-z0-9+#./ -]{2,}', decoded)
    filtered = [token.strip() for token in tokens if token.strip().lower() not in {'pdf', 'obj', 'endobj', 'xref', 'trailer'}]
    return '\n'.join(filtered[:200])


def _clean_text(text: str) -> str:
    text = text.replace('\xa0', ' ')
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\r\n?', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def _ensure_extractable(text: str, label: str) -> None:
    if not text.strip():
        raise ValueError(f'No resume text could be extracted from the {label} file.')
    compact = re.sub(r'\s+', '', text)
    if len(compact) < 12:
        raise ValueError(f'Extracted resume text from the {label} file was too short to use.')
