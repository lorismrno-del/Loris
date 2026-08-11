/**
 * Hintergrund-Jobs (Suche + Website-Analyse laufen bis zu ein paar Minuten).
 * Der Browser fragt den Fortschritt per Polling ab, statt auf eine lange
 * HTTP-Antwort zu warten.
 */
const jobs = new Map();
const MAX_JOBS = 20;

export function createJob(label) {
  const id = 'job_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
  const job = {
    id,
    label,
    state: 'running',
    step: 'Start …',
    done: 0,
    total: 0,
    startedAt: Date.now(),
    finishedAt: null,
    result: null,
    error: null,
    log: [],
  };
  jobs.set(id, job);

  // Alte Jobs aufräumen
  if (jobs.size > MAX_JOBS) {
    const sorted = [...jobs.values()].sort((a, b) => a.startedAt - b.startedAt);
    for (const old of sorted.slice(0, jobs.size - MAX_JOBS)) jobs.delete(old.id);
  }
  return job;
}

export function getJob(id) {
  return jobs.get(id) || null;
}

export function setStep(job, step, extra = {}) {
  job.step = step;
  Object.assign(job, extra);
  job.log.push({ ts: Date.now(), step });
  if (job.log.length > 50) job.log.shift();
}

export function finishJob(job, result) {
  job.state = 'done';
  job.step = 'Fertig';
  job.result = result;
  job.finishedAt = Date.now();
}

export function failJob(job, error) {
  job.state = 'error';
  job.error = error?.message || String(error);
  job.step = 'Fehlgeschlagen';
  job.finishedAt = Date.now();
}
