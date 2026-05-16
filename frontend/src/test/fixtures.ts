import type { FitEvaluation, JobPosting } from '../lib/types';

export const matchingJob: JobPosting = {
  id: 'fixture:1',
  sourceId: 'fixture',
  sourceName: 'Fixture Jobs',
  title: 'Senior Full Stack Engineer',
  company: 'Northstar Labs',
  location: 'Berlin, Germany',
  country: 'Germany',
  remote: 'yes',
  visaSponsorship: 'yes',
  description: 'TypeScript, React, Node.js, APIs, PostgreSQL, accessibility, testing. Visa sponsorship and remote work available.',
  tags: ['TypeScript', 'React', 'Node.js'],
  applyUrl: 'https://example.com/apply/1',
  fetchedAt: '2026-05-12T00:00:00.000Z',
  postedAt: '2026-05-12T00:00:00.000Z',
};

export const fixtureEvaluation: FitEvaluation = {
  jobId: matchingJob.id,
  score: 87,
  confidence: 'high',
  recommendation: 'strong-fit',
  matchedSkills: ['TypeScript', 'React', 'Node.js'],
  missingSkills: ['AWS'],
  strengths: ['Strong product engineering overlap'],
  risks: ['Cloud evidence is lighter'],
  signalNotes: ['Remote signal found', 'Visa sponsorship signal found'],
};
