import io
import unittest
import zipfile

from backend.services.resume_file_parser import parse_resume_file


def make_docx(paragraphs: list[str]) -> bytes:
    body = ''.join(f'<w:p><w:r><w:t>{paragraph}</w:t></w:r></w:p>' for paragraph in paragraphs)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as archive:
        archive.writestr('[Content_Types].xml', '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
        archive.writestr('word/document.xml', f'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>{body}</w:body></w:document>')
    return buffer.getvalue()


def make_text_pdf(text: str) -> bytes:
    from pypdf import PdfWriter
    from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

    safe_text = text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    font = DictionaryObject({
        NameObject('/Type'): NameObject('/Font'),
        NameObject('/Subtype'): NameObject('/Type1'),
        NameObject('/BaseFont'): NameObject('/Helvetica'),
    })
    font_ref = writer._add_object(font)
    page[NameObject('/Resources')] = DictionaryObject({
        NameObject('/Font'): DictionaryObject({NameObject('/F1'): font_ref}),
    })
    stream = DecodedStreamObject()
    stream.set_data(f'BT /F1 12 Tf 72 720 Td ({safe_text}) Tj ET'.encode('utf-8'))
    page[NameObject('/Contents')] = writer._add_object(stream)
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


class ResumeFileParserTest(unittest.TestCase):
    def test_parses_txt_resume(self):
        parsed = parse_resume_file('resume.txt', b'Maya Rao\nTypeScript React Node.js')

        self.assertIn('TypeScript', parsed.text)
        self.assertEqual(parsed.file_type, 'txt')

    def test_parses_docx_document_text(self):
        parsed = parse_resume_file('resume.docx', make_docx(['Maya Rao', 'React APIs']))

        self.assertIn('Maya Rao', parsed.text)
        self.assertIn('React APIs', parsed.text)
        self.assertEqual(parsed.file_type, 'docx')

    def test_parses_text_pdf_resume(self):
        parsed = parse_resume_file('resume.pdf', make_text_pdf('Maya Rao TypeScript React Node APIs'))

        self.assertIn('Maya Rao', parsed.text)
        self.assertIn('TypeScript', parsed.text)
        self.assertEqual(parsed.file_type, 'pdf')
        self.assertEqual(parsed.warnings, [])

    def test_rejects_empty_extraction(self):
        with self.assertRaises(ValueError):
            parse_resume_file('resume.txt', b'   ')

    def test_rejects_unsupported_files(self):
        with self.assertRaises(ValueError):
            parse_resume_file('resume.png', b'not supported')


if __name__ == '__main__':
    unittest.main()
