import { describe, expect, it } from 'vitest';
import { createProspectStore } from '../lib/prospects';
import { fixtureEvaluation, matchingJob } from './fixtures';

class MemoryStorage implements Storage {
  private data = new Map<string, string>();
  get length() { return this.data.size; }
  clear() { this.data.clear(); }
  getItem(key: string) { return this.data.get(key) ?? null; }
  key(index: number) { return Array.from(this.data.keys())[index] ?? null; }
  removeItem(key: string) { this.data.delete(key); }
  setItem(key: string, value: string) { this.data.set(key, value); }
}

describe('createProspectStore', () => {
  it('deduplicates saved jobs and appends status history', () => {
    const store = createProspectStore(new MemoryStorage());

    const first = store.saveProspect(matchingJob, fixtureEvaluation);
    const second = store.saveProspect(matchingJob, fixtureEvaluation);
    const updated = store.updateProspect(first.id, { status: 'tailored', notes: 'Resume draft ready.' });

    expect(first.id).toBe(second.id);
    expect(store.listProspects()).toHaveLength(1);
    expect(updated?.status).toBe('tailored');
    expect(updated?.history.some((entry) => entry.event.includes('tailored'))).toBe(true);
  });
});
