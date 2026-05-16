import unittest

import backend.services.outreach as outreach
from backend.services.outreach import create_outreach_drafts, infer_candidate_context
from backend.tests.fixtures import FIXTURE_EVALUATION, FIXTURE_RESUME, MATCHING_JOB


class OutreachTest(unittest.TestCase):
    def setUp(self):
        self.original_personalize_json = outreach.personalize_json

    def tearDown(self):
        outreach.personalize_json = self.original_personalize_json

    def test_creates_linkedin_and_email_drafts_with_review_status(self):
        drafts = create_outreach_drafts(
            candidate_name='Maya Rao',
            candidate_headline='Senior full stack engineer',
            job=MATCHING_JOB,
            evaluation=FIXTURE_EVALUATION,
        )

        self.assertIn('linkedin', [draft.channel for draft in drafts])
        self.assertIn('email', [draft.channel for draft in drafts])
        self.assertRegex(drafts[0].message, r'Senior Full Stack Engineer|Northstar Labs')
        self.assertTrue(all(draft.review_status == 'draft' for draft in drafts))
        self.assertTrue(any('linkedin.com/search' in draft.contact_hint for draft in drafts))

    def test_infers_candidate_context_from_resume(self):
        name, headline = infer_candidate_context(FIXTURE_RESUME)

        self.assertEqual(name, 'Maya Rao')
        self.assertEqual(headline, 'Senior Full Stack Engineer')

    def test_llm_outreach_payload_includes_resume_context(self):
        captured = {}

        def fake_personalize(_prompt, payload):
            captured.update(payload)
            return {'drafts': [{'channel': 'linkedin', 'message': 'Hi Northstar Labs, Maya has React and Node.js overlap.'}]}

        outreach.personalize_json = fake_personalize

        drafts = create_outreach_drafts(
            candidate_name='Maya Rao',
            candidate_headline='Senior Full Stack Engineer',
            job=MATCHING_JOB,
            evaluation=FIXTURE_EVALUATION,
            resume_text=FIXTURE_RESUME,
        )

        self.assertIn('Senior Full Stack Engineer', captured['resume'])
        self.assertIn('Maya', drafts[0].message)


if __name__ == '__main__':
    unittest.main()
