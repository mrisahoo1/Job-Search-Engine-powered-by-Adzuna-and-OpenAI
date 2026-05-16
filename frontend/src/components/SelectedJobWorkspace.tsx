import { Download, Mail, Save, Sparkles } from 'lucide-react';
import { useEffect, useState } from 'react';
import type { FitEvaluation, JobPosting, OutreachDraft, ResumeDraft, SearchResult } from '../lib/types';
import { resumeDownloadFilename } from '../lib/downloads';
import { ApplyLink } from './JobResults';

interface SelectedJobWorkspaceProps {
  selected: SearchResult | null;
  resumeText: string;
  onSaveProspect: (job: JobPosting, evaluation: FitEvaluation) => void;
}

export function SelectedJobWorkspace({ selected, resumeText, onSaveProspect }: SelectedJobWorkspaceProps) {
  const [resumeDraft, setResumeDraft] = useState<ResumeDraft | null>(null);
  const [outreachDrafts, setOutreachDrafts] = useState<OutreachDraft[]>([]);
  const [busy, setBusy] = useState<'resume' | 'outreach' | ''>('');
  const [error, setError] = useState('');

  useEffect(() => {
    setResumeDraft(null);
    setOutreachDrafts([]);
    setBusy('');
    setError('');
  }, [selected?.job.id]);

  async function generateResumeDraft() {
    if (!selected) return;
    setBusy('resume');
    setError('');
    try {
      const response = await postJson<ResumeDraft>('/api/tailor', { resumeText, job: selected.job, evaluation: selected.evaluation });
      setResumeDraft(normalizeResumeDraft(response));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Resume tailoring failed.');
    } finally {
      setBusy('');
    }
  }

  async function generateOutreach() {
    if (!selected) return;
    setBusy('outreach');
    setError('');
    try {
      const response = await postJson<OutreachDraft[]>('/api/outreach', {
        resumeText,
        job: selected.job,
        evaluation: selected.evaluation,
      });
      setOutreachDrafts(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Outreach drafting failed.');
    } finally {
      setBusy('');
    }
  }

  function downloadResumeDraft() {
    if (!resumeDraft || !selected) return;
    const blob = new Blob([resumeDraft.draftText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = resumeDownloadFilename(selected.job.company, selected.job.title);
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  if (!selected) {
    return (
      <section className="panel panel--workspace" aria-labelledby="workspace-heading">
        <p className="eyebrow">Selected role</p>
        <h2 id="workspace-heading">Application workspace</h2>
        <div className="empty-state">Select a job to tailor the resume, draft outreach, and review apply steps.</div>
      </section>
    );
  }

  return (
    <section className="panel panel--workspace" aria-labelledby="workspace-heading">
      <div className="panel__header">
        <div>
          <p className="eyebrow">Selected role</p>
          <h2 id="workspace-heading">{selected.job.title}</h2>
        </div>
        <button className="icon-button" type="button" onClick={() => onSaveProspect(selected.job, selected.evaluation)} title="Save prospect" aria-label="Save prospect">
          <Save size={17} />
        </button>
      </div>

      <div className="workspace-summary">
        <strong>{selected.job.company}</strong>
        <span>{selected.job.location}</span>
        <ApplyLink href={selected.job.applyUrl} />
      </div>

      <div className="score-band">
        <span>{selected.evaluation.score}</span>
        <div>
          <strong>{selected.evaluation.recommendation.replace('-', ' ')}</strong>
          <p>{selected.evaluation.confidence} confidence</p>
        </div>
      </div>

      <div className="reason-grid">
        <ReasonList title="Why apply" items={selected.evaluation.strengths} />
        <ReasonList title="Gaps / risks" items={selected.evaluation.risks} />
      </div>

      <div className="action-row">
        <button className="secondary-button" type="button" onClick={generateResumeDraft} disabled={busy === 'resume'}>
          <Sparkles size={17} /> {busy === 'resume' ? 'Tailoring' : 'Tailor resume'}
        </button>
        <button className="secondary-button" type="button" onClick={generateOutreach} disabled={busy === 'outreach'}>
          <Mail size={17} /> {busy === 'outreach' ? 'Drafting' : 'Draft outreach'}
        </button>
      </div>

      {error && <div className="notice notice--compact">{error}</div>}

      {resumeDraft && (
        <section className="draft-box">
          <div className="draft-box__header">
            <h3>Tailored resume draft</h3>
            <button className="icon-button" type="button" onClick={downloadResumeDraft} title="Download tailored resume" aria-label="Download tailored resume">
              <Download size={17} />
            </button>
          </div>
          <ul>{resumeDraft.changeSummary.map((item) => <li key={item}>{item}</li>)}</ul>
          {resumeDraft.warnings.length > 0 && <p className="warning-text">{resumeDraft.warnings.join(' ')}</p>}
          <textarea value={resumeDraft.draftText} readOnly />
        </section>
      )}

      {outreachDrafts.length > 0 && (
        <section className="draft-box">
          <h3>Outreach drafts</h3>
          {outreachDrafts.map((draft) => (
            <article key={draft.id} className="message-draft">
              <strong>{draft.channel}{draft.subject ? ` - ${draft.subject}` : ''}</strong>
              <p>{draft.contactHint}</p>
              <textarea value={draft.message} readOnly />
            </article>
          ))}
        </section>
      )}

      <div className="approval-boundary">No application or outreach is submitted from this app without your explicit review and external action.</div>
    </section>
  );
}

function ReasonList({ title, items }: { title: string; items: string[] }) {
  return (
    <div>
      <h3>{title}</h3>
      <ul>{items.map((item) => <li key={item}>{item}</li>)}</ul>
    </div>
  );
}

function normalizeResumeDraft(draft: ResumeDraft): ResumeDraft {
  return {
    ...draft,
    changeSummary: Array.isArray(draft.changeSummary) ? draft.changeSummary : [String(draft.changeSummary || '')].filter(Boolean),
    warnings: Array.isArray(draft.warnings) ? draft.warnings : [String(draft.warnings || '')].filter(Boolean),
  };
}

async function postJson<T>(url: string, payload: unknown): Promise<T> {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error(await readApiMessage(response, url));
  return response.json() as Promise<T>;
}

async function readApiMessage(response: Response, url: string): Promise<string> {
  try {
    const payload = await response.json() as { message?: string };
    if (payload.message) return payload.message;
  } catch {
    // Keep a useful fallback if the platform returns a non-JSON error page.
  }
  return `${url} returned ${response.status}`;
}
