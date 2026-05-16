import { describe, expect, it } from 'vitest';
import { resumeDownloadFilename } from '../lib/downloads';

describe('resumeDownloadFilename', () => {
  it('creates a safe job-specific tailored resume filename', () => {
    expect(resumeDownloadFilename('Leidos Europe', 'Lead Software Engineer')).toBe('leidos-europe-lead-software-engineer-tailored-resume.txt');
  });
});
