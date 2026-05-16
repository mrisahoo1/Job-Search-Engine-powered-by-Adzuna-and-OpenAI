from backend.services.models import FitEvaluation, JobPosting, SearchPreference

FIXTURE_RESUME = """
Maya Rao
Senior Full Stack Engineer
Built TypeScript and React product dashboards, Node.js APIs, PostgreSQL data models, and CI/CD deployments on Vercel.
Led migration work across distributed teams and improved API response times by 35%.
Experience with accessibility, testing, product analytics, and stakeholder communication.
"""

SPARSE_RESUME = 'Maya Rao - developer'

BASE_PREFERENCES = SearchPreference(
    query='software engineer',
    countries=['Germany', 'Netherlands'],
    remote_only=False,
    visa_sponsorship='preferred',
    sources=['fixture'],
)

MATCHING_JOB = JobPosting(
    id='fixture:1',
    source_id='fixture',
    source_name='Fixture Jobs',
    title='Senior Full Stack Engineer',
    company='Northstar Labs',
    location='Berlin, Germany',
    country='Germany',
    remote='yes',
    visa_sponsorship='yes',
    description='We need TypeScript, React, Node.js, APIs, PostgreSQL, accessibility, testing, and product-minded engineering. Visa sponsorship and remote work available in Germany.',
    tags=['TypeScript', 'React', 'Node.js', 'PostgreSQL'],
    posted_at='2026-05-12T00:00:00.000Z',
    apply_url='https://example.com/apply/1',
    fetched_at='2026-05-12T00:00:00.000Z',
)

STRETCH_JOB = JobPosting(
    id='fixture:2',
    source_id='fixture',
    source_name='Fixture Jobs',
    title='Cloud Infrastructure Engineer',
    company='CloudForge',
    location='Berlin, Germany',
    country='Germany',
    remote='unknown',
    visa_sponsorship='no',
    description='AWS, Kubernetes, Terraform, incident response, SRE, observability, platform engineering. No visa sponsorship.',
    tags=['AWS', 'Kubernetes', 'Terraform', 'SRE'],
    posted_at='2026-05-12T00:00:00.000Z',
    apply_url='https://example.com/apply/2',
    fetched_at='2026-05-12T00:00:00.000Z',
)

FIXTURE_EVALUATION = FitEvaluation(
    job_id=MATCHING_JOB.id,
    score=87,
    confidence='high',
    recommendation='strong-fit',
    matched_skills=['TypeScript', 'React', 'Node.js'],
    missing_skills=['AWS'],
    strengths=['Strong product engineering overlap'],
    risks=['Cloud evidence is lighter'],
    signal_notes=['Remote signal found', 'Visa sponsorship signal found'],
)
