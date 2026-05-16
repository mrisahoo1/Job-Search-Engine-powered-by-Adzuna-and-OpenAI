import base64
import unittest

from api.parse_resume import parse_resume_payload


class ParseResumeApiTest(unittest.TestCase):
    def test_parse_resume_payload_accepts_base64_data_url(self):
        encoded = base64.b64encode(b'Maya Rao\nPython FastAPI React').decode('ascii')
        parsed = parse_resume_payload({
            'fileName': 'maya_resume.txt',
            'data': f'data:text/plain;base64,{encoded}',
        })

        self.assertEqual(parsed['fileName'], 'maya_resume.txt')
        self.assertEqual(parsed['fileType'], 'txt')
        self.assertIn('Python', parsed['text'])

    def test_parse_resume_payload_rejects_missing_data(self):
        with self.assertRaises(ValueError):
            parse_resume_payload({'fileName': 'resume.pdf', 'data': ''})


if __name__ == '__main__':
    unittest.main()
