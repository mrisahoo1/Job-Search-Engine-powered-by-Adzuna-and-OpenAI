import unittest

import backend.services.resume_tailor as resume_tailor
from backend.services.resume_tailor import create_resume_draft
from backend.tests.fixtures import FIXTURE_EVALUATION, FIXTURE_RESUME, MATCHING_JOB


class ResumeTailorTest(unittest.TestCase):
    def tearDown(self):
        resume_tailor.personalize_json = self.original_personalize_json

    def setUp(self):
        self.original_personalize_json = resume_tailor.personalize_json

    def test_emphasizes_matched_evidence_and_warns_about_unsupported_requirements(self):
        draft = create_resume_draft(FIXTURE_RESUME, MATCHING_JOB, FIXTURE_EVALUATION)

        self.assertRegex(draft.draft_text, r'TypeScript|React|Node\.js')
        self.assertGreater(len(draft.change_summary), 0)
        self.assertRegex(' '.join(draft.warnings), r'AWS|not found|missing')
        self.assertNotIn('Certified AWS Solutions Architect', draft.draft_text)

    def test_llm_string_change_summary_is_not_split_into_characters(self):
        resume_tailor.personalize_json = lambda _prompt, _payload: {
            'draftText': 'Tailored CV for Northstar Labs with React and Node.js evidence.',
            'changeSummary': 'Tailored the resume for the Senior Full Stack Engineer role.',
            'warnings': 'Do not add AWS certification unless it is true.',
        }

        draft = create_resume_draft(FIXTURE_RESUME, MATCHING_JOB, FIXTURE_EVALUATION)

        self.assertEqual(draft.change_summary, ['Tailored the resume for the Senior Full Stack Engineer role.'])
        self.assertEqual(draft.warnings, ['Do not add AWS certification unless it is true.'])


if __name__ == '__main__':
    unittest.main()
