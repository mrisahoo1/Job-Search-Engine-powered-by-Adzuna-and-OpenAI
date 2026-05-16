export type Signal = 'yes' | 'no' | 'unknown';
export type Confidence = 'high' | 'medium' | 'low';
export type Recommendation = 'strong-fit' | 'possible-fit' | 'stretch' | 'low-fit';
export type VisaPreference = 'required' | 'preferred' | 'any';
export type SearchMode = 'live' | 'adzuna';
export type RegionId = 'eu_uk' | 'india' | 'us' | 'australia' | 'remote_global';
export type ProspectStatus = 'new' | 'reviewing' | 'tailored' | 'outreach-drafted' | 'applied' | 'interviewing' | 'rejected' | 'archived';

export interface SearchPreference {
  query: string;
  region: RegionId;
  countries: string[];
  remoteOnly: boolean;
  visaSponsorship: VisaPreference;
  sources: string[];
  officialCompanies: string[];
  searchMode: SearchMode;
}

export interface ParsedResume {
  text: string;
  fileName: string;
  fileType: string;
  warnings: string[];
}

export interface JobPosting {
  id: string;
  sourceId: string;
  sourceName: string;
  title: string;
  company: string;
  location: string;
  country: string;
  remote: Signal;
  visaSponsorship: Signal;
  description: string;
  tags: string[];
  applyUrl: string;
  fetchedAt: string;
  postedAt?: string | null;
}

export interface FitEvaluation {
  jobId: string;
  score: number;
  confidence: Confidence;
  recommendation: Recommendation;
  matchedSkills: string[];
  missingSkills: string[];
  strengths: string[];
  risks: string[];
  signalNotes: string[];
}

export interface SearchResult { job: JobPosting; evaluation: FitEvaluation; }
export interface SourceStatus { sourceId: string; status: 'available' | 'degraded' | 'disabled' | 'unsupported'; message: string; }
export interface SearchResponse { results: SearchResult[]; sourceStatuses: SourceStatus[]; fetchedAt: string; }
export interface ResumeDraft { id: string; jobId: string; baseResumeText: string; draftText: string; changeSummary: string[]; warnings: string[]; createdAt: string; }
export interface OutreachDraft { id: string; jobId: string; channel: 'linkedin' | 'email' | 'text'; targetPersona: string; contactHint: string; message: string; reviewStatus: 'draft' | 'copied' | 'approved' | 'rejected'; subject?: string | null; }
export interface ProspectHistoryEntry { at: string; event: string; }
export interface Prospect { id: string; job: JobPosting; evaluation: FitEvaluation; status: ProspectStatus; notes: string; nextAction: string; resumeDrafts: ResumeDraft[]; outreachDrafts: OutreachDraft[]; history: ProspectHistoryEntry[]; }
