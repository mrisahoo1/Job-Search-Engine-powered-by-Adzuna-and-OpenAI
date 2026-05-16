import type { FitEvaluation, JobPosting, Prospect, ProspectStatus } from './types';

const STORAGE_KEY = 'job-curation-agent:prospects';

type ProspectPatch = Partial<Pick<Prospect, 'status' | 'notes' | 'nextAction' | 'resumeDrafts' | 'outreachDrafts'>>;

export function createProspectStore(storage: Storage = window.localStorage) {
  return {
    listProspects(): Prospect[] {
      return read(storage);
    },
    saveProspect(job: JobPosting, evaluation: FitEvaluation): Prospect {
      const prospects = read(storage);
      const existing = prospects.find((prospect) => prospect.job.applyUrl === job.applyUrl || prospect.job.id === job.id);
      if (existing) return existing;
      const prospect: Prospect = {
        id: `prospect:${job.id}`,
        job,
        evaluation,
        status: 'new',
        notes: '',
        nextAction: 'Review fit and decide whether to tailor resume.',
        resumeDrafts: [],
        outreachDrafts: [],
        history: [{ at: new Date().toISOString(), event: 'Saved prospect.' }],
      };
      write(storage, [prospect, ...prospects]);
      return prospect;
    },
    updateProspect(id: string, patch: ProspectPatch): Prospect | null {
      const prospects = read(storage);
      const updated = prospects.map((prospect) => {
        if (prospect.id !== id) return prospect;
        const statusChanged = patch.status && patch.status !== prospect.status;
        const next: Prospect = { ...prospect, ...patch };
        if (statusChanged) {
          next.history = [{ at: new Date().toISOString(), event: `Status changed to ${labelStatus(patch.status as ProspectStatus)}.` }, ...prospect.history];
        }
        return next;
      });
      write(storage, updated);
      return updated.find((prospect) => prospect.id === id) ?? null;
    },
  };
}

function read(storage: Storage): Prospect[] {
  const raw = storage.getItem(STORAGE_KEY);
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw) as Prospect[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function write(storage: Storage, prospects: Prospect[]): void {
  storage.setItem(STORAGE_KEY, JSON.stringify(prospects));
}

function labelStatus(status: ProspectStatus): string {
  return status.replace('-', ' ');
}
