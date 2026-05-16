import { ExternalLink, Loader2, MapPin, ShieldCheck, Star } from 'lucide-react';
import type { SearchResult } from '../lib/types';

interface JobResultsProps {
  results: SearchResult[];
  selectedId?: string;
  onSelect: (result: SearchResult) => void;
  loading: boolean;
}

export function JobResults({ results, selectedId, onSelect, loading }: JobResultsProps) {
  return (
    <section className="panel panel--results" aria-labelledby="results-heading">
      <div className="panel__header">
        <div>
          <p className="eyebrow">Ranked opportunities</p>
          <h2 id="results-heading">Matches</h2>
        </div>
        {loading && <Loader2 className="spin" size={18} />}
      </div>

      {!loading && results.length === 0 && (
        <div className="empty-state">Run a backend search to assemble EU prospects with direct apply links.</div>
      )}

      <div className="job-list">
        {results.map((result) => (
          <button
            key={result.job.id}
            type="button"
            className={`job-card ${selectedId === result.job.id ? 'job-card--active' : ''}`}
            onClick={() => onSelect(result)}
          >
            <span className="job-card__score"><Star size={15} /> {result.evaluation.score}</span>
            <strong>{result.job.title}</strong>
            <span>{result.job.company}</span>
            <span className="muted"><MapPin size={14} /> {result.job.location || 'Location not stated'}</span>
            <span className="job-card__signals">
              <span>{result.job.remote === 'yes' ? 'Remote' : result.job.remote === 'no' ? 'Onsite' : 'Remote unknown'}</span>
              <span><ShieldCheck size={13} /> Visa {result.job.visaSponsorship}</span>
            </span>
            <span className="muted">{result.job.sourceName}</span>
          </button>
        ))}
      </div>
    </section>
  );
}

export function ApplyLink({ href }: { href: string }) {
  return <a className="text-link" href={href} target="_blank" rel="noreferrer"><ExternalLink size={15} /> Apply link</a>;
}
