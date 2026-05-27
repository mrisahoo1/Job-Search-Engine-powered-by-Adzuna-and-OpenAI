import { useMemo, useState } from 'react';
import { BriefcaseBusiness, RefreshCw, Search, ShieldCheck } from 'lucide-react';
import type { FitEvaluation, JobPosting, Prospect, SearchPreference, SearchResponse, SearchResult, SourceStatus } from './lib/types';
import { JobResults } from './components/JobResults';
import { PreferencesPanel } from './components/PreferencesPanel';
import { ProspectBoard } from './components/ProspectBoard';
import { ResumePanel } from './components/ResumePanel';
import { SelectedJobWorkspace } from './components/SelectedJobWorkspace';
import { createProspectStore } from './lib/prospects';

const sampleResume = `Maya Rao
Senior Full Stack Engineer
Built TypeScript and React product dashboards, Node.js APIs, PostgreSQL data models, and CI/CD deployments on Vercel.
Led migration work across distributed teams and improved API response times by 35%.
Experience with accessibility, testing, product analytics, and stakeholder communication.`;

const defaultPreferences: SearchPreference = {
  query: 'software engineer',
  region: 'eu_uk',
  countries: ['Germany', 'Netherlands', 'Ireland', 'France', 'Spain', 'United Kingdom'],
  remoteOnly: false,
  visaSponsorship: 'preferred',
  sources: ['deep', 'official'],
  officialCompanies: ['bmw', 'example-greenhouse'],
  searchMode: 'live',
};

export function App() {
  const prospectStore = useMemo(() => createProspectStore(), []);
  const [resumeText, setResumeText] = useState(sampleResume);
  const [preferences, setPreferences] = useState<SearchPreference>(defaultPreferences);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [sourceStatuses, setSourceStatuses] = useState<SourceStatus[]>([]);
  const [selected, setSelected] = useState<SearchResult | null>(null);
  const [prospects, setProspects] = useState<Prospect[]>(() => prospectStore.listProspects());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function runSearch() {
    setLoading(true);
    setError('');
    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resumeText, preferences }),
      });
      if (!response.ok) throw new Error(`Search endpoint returned ${response.status}`);
      const payload = await response.json() as SearchResponse;
      setResults(payload.results);
      setSourceStatuses(payload.sourceStatuses);
      setSelected(payload.results[0] ?? null);
      if (!payload.results.length) setError('No matching jobs returned for the active EU filters.');
    } catch (apiError) {
      setError(apiError instanceof Error ? apiError.message : 'Search failed.');
    } finally {
      setLoading(false);
    }
  }

  function saveProspect(job: JobPosting, evaluation: FitEvaluation) {
    prospectStore.saveProspect(job, evaluation);
    setProspects(prospectStore.listProspects());
  }

  function updateProspect(id: string, patch: Partial<Pick<Prospect, 'status' | 'notes' | 'nextAction'>>) {
    prospectStore.updateProspect(id, patch);
    setProspects(prospectStore.listProspects());
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">EU prospect assembly</p>
          <h1>Job Search Curation Agent</h1>
        </div>
        <div className="topbar__meta" aria-label="Active operating guardrails">
          <span><ShieldCheck size={16} /> EU active</span>
          <span><BriefcaseBusiness size={16} /> User-reviewed apply</span>
        </div>
      </header>

      <section className="control-grid" aria-label="Search controls">
        <ResumePanel resumeText={resumeText} onChange={setResumeText} onLoadSample={() => setResumeText(sampleResume)} />
        <PreferencesPanel preferences={preferences} onChange={setPreferences} onSearch={runSearch} loading={loading} />
      </section>

      {sourceStatuses.length > 0 && (
        <section className="source-strip" aria-label="Source status">
          {sourceStatuses.map((status) => (
            <span key={`${status.sourceId}-${status.message}`} className={`source-pill source-pill--${status.status}`}>
              {status.sourceId}: {status.message}
            </span>
          ))}
        </section>
      )}

      {error && <div className="notice" role="status">{error}</div>}

      <section className="work-grid">
        <JobResults results={results} selectedId={selected?.job.id} onSelect={setSelected} loading={loading} />
        <SelectedJobWorkspace selected={selected} resumeText={resumeText} onSaveProspect={saveProspect} />
        <ProspectBoard prospects={prospects} onUpdateProspect={updateProspect} />
      </section>

      <button className="floating-search" type="button" onClick={runSearch} disabled={loading} aria-label="Run EU job search">
        {loading ? <RefreshCw size={18} className="spin" /> : <Search size={18} />}
      </button>
    </main>
  );
}

