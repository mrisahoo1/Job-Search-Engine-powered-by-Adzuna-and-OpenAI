import unittest

from backend.services.matching import evaluate_job_match
from backend.services.resume import extract_resume_profile
from backend.tests.fixtures import BASE_PREFERENCES, FIXTURE_RESUME, MATCHING_JOB, SPARSE_RESUME, STRETCH_JOB


class MatchingTest(unittest.TestCase):
    def test_scores_strong_matches_above_stretch_jobs(self):
        profile = extract_resume_profile(FIXTURE_RESUME)

        strong = evaluate_job_match(profile, MATCHING_JOB, BASE_PREFERENCES)
        stretch = evaluate_job_match(profile, STRETCH_JOB, BASE_PREFERENCES)

        self.assertGreater(strong.score, stretch.score)
        self.assertEqual(strong.recommendation, 'strong-fit')
        self.assertIn('TypeScript', strong.matched_skills)
        self.assertRegex(' '.join(strong.signal_notes), r'Visa sponsorship')
        self.assertRegex(' '.join(stretch.risks), r'sponsorship|Missing|gap')

    def test_lowers_confidence_for_sparse_resumes(self):
        profile = extract_resume_profile(SPARSE_RESUME)
        result = evaluate_job_match(profile, MATCHING_JOB, BASE_PREFERENCES)

        self.assertEqual(result.confidence, 'low')
        self.assertGreater(len(result.risks), 0)


if __name__ == '__main__':
    unittest.main()
