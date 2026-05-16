import unittest

from backend.services.outreach import create_outreach_drafts
from backend.services.resume_tailor import create_resume_draft
from backend.tests.fixtures import FIXTURE_EVALUATION, FIXTURE_RESUME, MATCHING_JOB, STRETCH_JOB


class PersonalizationTest(unittest.TestCase):
    def test_outreach_drafts_differ_for_different_jobs(self):
        first = create_outreach_drafts('Maya Rao', 'Senior full stack engineer', MATCHING_JOB, FIXTURE_EVALUATION)[0]
        second = create_outreach_drafts('Maya Rao', 'Senior full stack engineer', STRETCH_JOB, FIXTURE_EVALUATION)[0]

        self.assertIn(MATCHING_JOB.company, first.message)
        self.assertIn(STRETCH_JOB.company, second.message)
        self.assertNotEqual(first.message, second.message)

    def test_tailored_resume_uses_job_description_and_gap_warnings(self):
        draft = create_resume_draft(FIXTURE_RESUME, STRETCH_JOB, FIXTURE_EVALUATION)

        self.assertIn(STRETCH_JOB.title, draft.draft_text)
        self.assertTrue(any('AWS' in warning for warning in draft.warnings))
        self.assertIn('CloudForge', ' '.join(draft.change_summary))


if __name__ == '__main__':
    unittest.main()
