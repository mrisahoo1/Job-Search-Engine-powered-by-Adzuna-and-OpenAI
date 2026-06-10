import { Database, Globe2, Search, SlidersHorizontal } from 'lucide-react';
import type { RegionId, SearchMode, SearchPreference, VisaPreference } from '../lib/types';

const regions: Array<{ id: RegionId; label: string; countries: string[] }> = [
  { id: 'eu_uk', label: 'EU + UK', countries: ['Germany', 'Netherlands', 'Ireland', 'France', 'Spain', 'Sweden', 'Denmark', 'United Kingdom'] },
  { id: 'india', label: 'India', countries: ['India'] },
  { id: 'us', label: 'United States', countries: ['United States'] },
  { id: 'australia', label: 'Australia', countries: ['Australia'] },
  { id: 'remote_global', label: 'Remote / Global', countries: [] },
];
const sourceOptions = [
  { id: 'deep', label: 'Deep web crawl' },
  { id: 'arbeitnow', label: 'Arbeitnow feed' },
  { id: 'remotive', label: 'Remotive feed' },
  { id: 'official', label: 'Official sites' },
  { id: 'seeded', label: 'Seeded examples' },
];
const companyOptions = [
  { id: 'bmw', label: 'BMW careers' },
  { id: 'stripe', label: 'Stripe careers' },
  { id: 'example-greenhouse', label: 'Greenhouse board' },
];

interface PreferencesPanelProps { preferences: SearchPreference; onChange: (preferences: SearchPreference) => void; onSearch: () => void; loading: boolean; }

export function PreferencesPanel({ preferences, onChange, onSearch, loading }: PreferencesPanelProps) {
  function setRegion(region: RegionId) {
    const option = regions.find((item) => item.id === region) ?? regions[0];
    onChange({ ...preferences, region, countries: option.countries });
  }
  function toggleSource(source: string, active: boolean) {
    onChange({ ...preferences, sources: active ? Array.from(new Set([...preferences.sources, source])) : preferences.sources.filter((item) => item !== source) });
  }
  function toggleCompany(company: string, active: boolean) {
    onChange({ ...preferences, officialCompanies: active ? Array.from(new Set([...preferences.officialCompanies, company])) : preferences.officialCompanies.filter((item) => item !== company) });
  }
  function setMode(mode: SearchMode) {
    onChange({ ...preferences, searchMode: mode, sources: mode === 'adzuna' ? ['adzuna'] : ['deep', 'official'] });
  }

  return (
    <section className="panel panel--preferences" aria-labelledby="preferences-heading">
      <div className="panel__header"><div><p className="eyebrow">Search mode</p><h2 id="preferences-heading">Live controls</h2></div><SlidersHorizontal size={20} /></div>
      <div className="tab-row" role="tablist" aria-label="Search mode">
        <button type="button" className={preferences.searchMode === 'live' ? 'active' : ''} onClick={() => setMode('live')}><Globe2 size={16} /> Live Search</button>
        <button type="button" className={preferences.searchMode === 'adzuna' ? 'active' : ''} onClick={() => setMode('adzuna')}><Database size={16} /> Adzuna Search</button>
      </div>
      <label className="field-label" htmlFor="query">Target role</label>
      <input id="query" value={preferences.query} onChange={(event) => onChange({ ...preferences, query: event.target.value })} />
      <label className="field-label" htmlFor="region">Region</label>
      <select id="region" value={preferences.region} onChange={(event) => setRegion(event.target.value as RegionId)}>
        {regions.map((region) => <option key={region.id} value={region.id}>{region.label}</option>)}
      </select>
      <div className="region-note">Active countries: {preferences.countries.length ? preferences.countries.join(', ') : 'Remote/global source coverage'}</div>

      {preferences.searchMode === 'live' && (
        <fieldset className="country-grid"><legend>Live sources</legend>{sourceOptions.map((source) => <label key={source.id}><input type="checkbox" checked={preferences.sources.includes(source.id)} onChange={(event) => toggleSource(source.id, event.target.checked)} />{source.label}</label>)}</fieldset>
      )}
      {preferences.searchMode === 'live' && preferences.sources.includes('official') && (
        <fieldset className="country-grid"><legend>Official sites</legend>{companyOptions.map((company) => <label key={company.id}><input type="checkbox" checked={preferences.officialCompanies.includes(company.id)} onChange={(event) => toggleCompany(company.id, event.target.checked)} />{company.label}</label>)}</fieldset>
      )}
      <div className="inline-fields">
        <label><input type="checkbox" checked={preferences.remoteOnly} onChange={(event) => onChange({ ...preferences, remoteOnly: event.target.checked })} />Remote only</label>
        <label>Visa<select value={preferences.visaSponsorship} onChange={(event) => onChange({ ...preferences, visaSponsorship: event.target.value as VisaPreference })}><option value="preferred">Preferred</option><option value="required">Required</option><option value="any">Any</option></select></label>
      </div>
      <button className="primary-button" type="button" onClick={onSearch} disabled={loading || !preferences.query.trim()}><Search size={18} />{loading ? 'Searching' : `Run ${preferences.searchMode === 'adzuna' ? 'Adzuna' : 'live'} search`}</button>
    </section>
  );
}

