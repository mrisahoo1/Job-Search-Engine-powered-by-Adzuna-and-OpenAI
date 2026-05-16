import { Upload, FileText, RotateCcw } from 'lucide-react';
import { useRef, useState } from 'react';
import type { ParsedResume } from '../lib/types';

interface ResumePanelProps {
  resumeText: string;
  onChange: (value: string) => void;
  onLoadSample: () => void;
}

export function ResumePanel({ resumeText, onChange, onLoadSample }: ResumePanelProps) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [parseStatus, setParseStatus] = useState('');

  async function uploadResume(file: File | undefined) {
    if (!file) return;
    setParseStatus(`Parsing ${file.name}...`);
    try {
      const data = await readFileAsDataUrl(file);
      const response = await fetch('/api/parse_resume', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fileName: file.name, data }),
      });
      if (!response.ok) throw new Error(await readParserMessage(response));
      const parsed = await response.json() as ParsedResume;
      if (!parsed.text.trim()) throw new Error('No resume text could be extracted from this file.');
      onChange(parsed.text);
      const warning = parsed.warnings.length ? ` - ${parsed.warnings[0]}` : '';
      setParseStatus(`${parsed.fileName} parsed as ${parsed.fileType}${warning}`);
    } catch (error) {
      setParseStatus(error instanceof Error ? error.message : 'Resume parsing failed.');
    } finally {
      if (fileRef.current) fileRef.current.value = '';
    }
  }

  return (
    <section className="panel panel--resume" aria-labelledby="resume-heading">
      <div className="panel__header">
        <div>
          <p className="eyebrow">Resume input</p>
          <h2 id="resume-heading">Upload or edit CV</h2>
        </div>
        <div className="button-cluster">
          <button className="icon-button" type="button" onClick={() => fileRef.current?.click()} title="Upload resume" aria-label="Upload resume"><Upload size={17} /></button>
          <button className="icon-button" type="button" onClick={onLoadSample} title="Load sample resume" aria-label="Load sample resume"><RotateCcw size={17} /></button>
        </div>
      </div>
      <input ref={fileRef} className="sr-only" type="file" accept=".pdf,.docx,.txt,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain" onChange={(event) => uploadResume(event.target.files?.[0])} />
      <label className="field-label" htmlFor="resume-text"><FileText size={16} /> Parsed resume / CV text</label>
      <textarea id="resume-text" value={resumeText} onChange={(event) => onChange(event.target.value)} spellCheck={false} />
      {parseStatus && <p className="parse-status">{parseStatus}</p>}
    </section>
  );
}

async function readParserMessage(response: Response): Promise<string> {
  try {
    const payload = await response.json() as { message?: string };
    if (payload.message) return payload.message;
  } catch {
    // The API normally returns JSON, but keep the UI useful if a proxy returns HTML/text.
  }
  return `Parser returned ${response.status}`;
}

function readFileAsDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result));
    reader.onerror = () => reject(reader.error ?? new Error('Could not read file.'));
    reader.readAsDataURL(file);
  });
}
