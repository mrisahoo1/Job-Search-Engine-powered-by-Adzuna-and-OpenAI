import type { Prospect, ProspectStatus } from '../lib/types';

const statuses: ProspectStatus[] = ['new', 'reviewing', 'tailored', 'outreach-drafted', 'applied', 'interviewing', 'rejected', 'archived'];

interface ProspectBoardProps {
  prospects: Prospect[];
  onUpdateProspect: (id: string, patch: Partial<Pick<Prospect, 'status' | 'notes' | 'nextAction'>>) => void;
}

export function ProspectBoard({ prospects, onUpdateProspect }: ProspectBoardProps) {
  return (
    <section className="panel panel--prospects" aria-labelledby="prospects-heading">
      <div className="panel__header">
        <div>
          <p className="eyebrow">Pipeline</p>
          <h2 id="prospects-heading">Prospects</h2>
        </div>
        <span className="count-pill">{prospects.length}</span>
      </div>

      {prospects.length === 0 && <div className="empty-state">Saved jobs appear here with notes and next actions.</div>}

      <div className="prospect-list">
        {prospects.map((prospect) => (
          <article className="prospect-card" key={prospect.id}>
            <strong>{prospect.job.company}</strong>
            <span>{prospect.job.title}</span>
            <select value={prospect.status} onChange={(event) => onUpdateProspect(prospect.id, { status: event.target.value as ProspectStatus })}>
              {statuses.map((status) => <option key={status} value={status}>{status.replace('-', ' ')}</option>)}
            </select>
            <textarea
              value={prospect.notes}
              placeholder="Notes"
              onChange={(event) => onUpdateProspect(prospect.id, { notes: event.target.value })}
            />
            <input
              value={prospect.nextAction}
              placeholder="Next action"
              onChange={(event) => onUpdateProspect(prospect.id, { nextAction: event.target.value })}
            />
          </article>
        ))}
      </div>
    </section>
  );
}
