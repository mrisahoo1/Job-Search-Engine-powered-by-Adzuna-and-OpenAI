import unittest

from backend.services.resume import extract_resume_profile
from backend.tests.fixtures import FIXTURE_RESUME, SPARSE_RESUME


class ResumeParsingTest(unittest.TestCase):
    def test_extracts_normalized_skills_and_seniority(self):
        profile = extract_resume_profile(FIXTURE_RESUME)

        self.assertIn('TypeScript', profile.extracted_skills)
        self.assertIn('React', profile.extracted_skills)
        self.assertIn('Node.js', profile.extracted_skills)
        self.assertIn('PostgreSQL', profile.extracted_skills)
        self.assertIn('Senior Full Stack Engineer', profile.experience_signals)
        self.assertEqual(profile.confidence, 'high')

    def test_marks_sparse_resumes_low_confidence(self):
        profile = extract_resume_profile(SPARSE_RESUME)

        self.assertEqual(profile.confidence, 'low')
        self.assertLess(len(profile.extracted_skills), 2)


if __name__ == '__main__':
    unittest.main()
