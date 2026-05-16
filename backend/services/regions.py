from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

RegionId = Literal['eu_uk', 'india', 'us', 'australia', 'remote_global']


@dataclass(slots=True)
class RegionOption:
    id: RegionId
    label: str
    countries: list[str]
    source_terms: list[str] = field(default_factory=list)


_REGIONS: dict[str, RegionOption] = {
    'eu_uk': RegionOption('eu_uk', 'EU + UK', ['Germany', 'Netherlands', 'Ireland', 'France', 'Spain', 'Sweden', 'Denmark', 'United Kingdom'], ['Europe', 'EU', 'UK']),
    'india': RegionOption('india', 'India', ['India'], ['India', 'Bengaluru', 'Hyderabad', 'Remote India']),
    'us': RegionOption('us', 'United States', ['United States'], ['United States', 'USA', 'Remote US']),
    'australia': RegionOption('australia', 'Australia', ['Australia'], ['Australia', 'Remote Australia']),
    'remote_global': RegionOption('remote_global', 'Remote / Global', [], ['Remote', 'Worldwide', 'Global']),
}


def region_options() -> list[RegionOption]:
    return list(_REGIONS.values())


def normalize_region(payload: dict | None) -> RegionOption:
    raw = (payload or {}).get('region') or (payload or {}).get('regionId') or 'eu_uk'
    return _REGIONS.get(str(raw), _REGIONS['eu_uk'])
