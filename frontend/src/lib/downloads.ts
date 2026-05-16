export function resumeDownloadFilename(company: string, title: string): string {
  const base = `${company} ${title} tailored resume`
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 120);
  return `${base || 'tailored-resume'}.txt`;
}
