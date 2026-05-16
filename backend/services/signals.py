from __future__ import annotations

import re

from backend.services.models import Signal

EU_COUNTRIES = [
    'Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Denmark', 'Estonia', 'Finland',
    'France', 'Germany', 'Greece', 'Hungary', 'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta',
    'Netherlands', 'Poland', 'Portugal', 'Romania', 'Slovakia', 'Slovenia', 'Spain', 'Sweden',
]

UK_LOCATION_HINTS = {
    'uk', 'u.k.', 'united kingdom', 'england', 'scotland', 'wales', 'northern ireland',
    'london', 'manchester', 'birmingham', 'liverpool', 'bristol', 'leeds', 'glasgow', 'edinburgh', 'cardiff', 'belfast',
    'hampshire', 'gloucestershire', 'dorchester', 'fareham', 'farnborough', 'south east england', 'south west england',
    'east knighton', 'stanley', 'widnes', 'cheshire', 'oxfordshire', 'cambridgeshire', 'berkshire', 'surrey', 'kent', 'essex', 'yorkshire',
}

COUNTRY_HINTS = {
    'India': {'india', 'bengaluru', 'bangalore', 'delhi', 'gurugram', 'gurgaon', 'mumbai', 'pune', 'hyderabad', 'chennai'},
    'United States': {'united states', 'usa', 'u.s.', 'us', 'nyc', 'new york', 'san francisco', 'california', 'seattle', 'washington', 'austin', 'texas', 'boston', 'massachusetts'},
    'Australia': {'australia', 'sydney', 'melbourne', 'brisbane', 'perth', 'adelaide', 'canberra'},
}


def detect_remote_signal(text: str) -> Signal:
    haystack = text.lower()
    if re.search(r'onsite only|on-site only|must be onsite|office only', haystack):
        return 'no'
    if re.search(r'remote|work from home|home-office|home office|distributed|anywhere', haystack):
        return 'yes'
    return 'unknown'


def detect_visa_signal(text: str) -> Signal:
    haystack = text.lower()
    if re.search(r'no visa sponsorship|cannot sponsor|must already have work authorization|must have work authorisation|no sponsorship', haystack):
        return 'no'
    if re.search(r'visa sponsorship|sponsor visa|relocation support|work permit support|blue card|visa support', haystack):
        return 'yes'
    return 'unknown'


def detect_country(text: str) -> str:
    haystack = text.lower()
    if _contains_uk_hint(haystack):
        return 'United Kingdom'
    for country, hints in COUNTRY_HINTS.items():
        if _contains_any_hint(haystack, hints):
            return country
    return next((country for country in EU_COUNTRIES if country.lower() in haystack), '')


def is_eu_country(country: str) -> bool:
    return country.lower() in {item.lower() for item in EU_COUNTRIES} | {'united kingdom'}


def _contains_uk_hint(haystack: str) -> bool:
    return _contains_any_hint(haystack, UK_LOCATION_HINTS)


def _contains_any_hint(haystack: str, hints: set[str]) -> bool:
    padded = f' {haystack} '
    return any(re.search(rf'(?<![a-z]){re.escape(hint)}(?![a-z])', padded) for hint in hints)
