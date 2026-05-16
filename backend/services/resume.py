from __future__ import annotations

import re

from backend.services.models import CandidateProfile

_SKILL_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ('TypeScript', re.compile(r'\btypescript\b|\bts\b', re.I)),
    ('JavaScript', re.compile(r'\bjavascript\b|\bjs\b', re.I)),
    ('React', re.compile(r'\breact(?:\.js)?\b', re.I)),
    ('Node.js', re.compile(r'\bnode(?:\.js)?\b', re.I)),
    ('PostgreSQL', re.compile(r'\bpostgres(?:ql)?\b', re.I)),
    ('Vercel', re.compile(r'\bvercel\b', re.I)),
    ('AWS', re.compile(r'\baws\b|amazon web services', re.I)),
    ('Kubernetes', re.compile(r'\bkubernetes\b|\bk8s\b', re.I)),
    ('Terraform', re.compile(r'\bterraform\b', re.I)),
    ('APIs', re.compile(r'\bapi\b|\bapis\b|rest|graphql', re.I)),
    ('CI/CD', re.compile(r'\bci/cd\b|continuous integration|deployment pipeline', re.I)),
    ('Accessibility', re.compile(r'\baccessibility\b|\ba11y\b', re.I)),
    ('Testing', re.compile(r'\btesting\b|\btest automation\b|\bpytest\b|\bvitest\b|\bjest\b', re.I)),
    ('Product Analytics', re.compile(r'product analytics|analytics', re.I)),
]

_TITLE_PATTERNS = [
    re.compile(r'senior full stack engineer', re.I),
    re.compile(r'full stack engineer', re.I),
    re.compile(r'software engineer', re.I),
    re.compile(r'backend engineer', re.I),
    re.compile(r'frontend engineer', re.I),
    re.compile(r'platform engineer', re.I),
]


def extract_resume_profile(resume_text: str) -> CandidateProfile:
    normalized = resume_text.strip()
    skills = extract_known_skills(normalized)
    experience_signals = _unique([
        *[_title_case(match.group(0)) for pattern in _TITLE_PATTERNS if (match := pattern.search(normalized))],
        *[label for label, pattern in [('APIs', re.compile(r'\bapi\b|\bapis\b', re.I)), ('CI/CD', re.compile(r'ci/cd', re.I))] if pattern.search(normalized)],
    ])
    confidence = 'high' if len(normalized) > 180 and len(skills) >= 3 else 'medium' if len(skills) >= 2 else 'low'
    return CandidateProfile(
        resume_text=normalized,
        extracted_skills=skills,
        experience_signals=experience_signals,
        target_titles=_unique([_title_case(match.group(0)) for pattern in _TITLE_PATTERNS if (match := pattern.search(normalized))]),
        preferred_countries=['Germany', 'Netherlands', 'Ireland', 'France', 'Spain'],
        remote_preference='remote',
        visa_preference='preferred',
        confidence=confidence,
    )


def extract_known_skills(text: str) -> list[str]:
    return _unique([skill for skill, pattern in _SKILL_PATTERNS if pattern.search(text)])


def _unique(values: list[str]) -> list[str]:
    seen: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.append(value)
    return seen


def _title_case(value: str) -> str:
    return ' '.join(part.capitalize() for part in value.split())
