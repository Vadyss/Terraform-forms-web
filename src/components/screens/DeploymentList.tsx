import { useEffect, useState } from 'react';
import type { MouseEvent } from 'react';
import type { Job, JobStatus } from '../../types';

interface DeploymentListProps {
  onSelectJob: (id: string) => void;
}

const POLL_INTERVAL_MS = 5000;

const STATUS_LABEL: Record<JobStatus, string> = {
  planning: 'Plánování',
  awaiting_confirmation: 'Čeká na potvrzení',
  applying: 'Aplikace',
  done: 'Hotovo',
  error: 'Chyba',
  destroying: 'Ruší se',
  destroyed: 'Zrušeno',
};

export function DeploymentList({ onSelectJob }: DeploymentListProps) {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [destroyingIds, setDestroyingIds] = useState<Set<string>>(new Set());

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const res = await fetch('/api/deployments');
        if (!res.ok) {
          throw new Error('Nepodařilo se načíst deploymenty');
        }
        const data: Job[] = await res.json();
        if (!cancelled) {
          setJobs(data);
          setError(null);
        }
      } catch {
        if (!cancelled) setError('Nepodařilo se načíst deploymenty');
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    load();
    const timer = setInterval(load, POLL_INTERVAL_MS);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, []);

  async function handleDestroy(e: MouseEvent, id: string) {
    e.stopPropagation();
    setDestroyingIds((prev) => new Set(prev).add(id));
    try {
      const res = await fetch(`/api/deployments/${id}/destroy`, { method: 'POST' });
      if (!res.ok) {
        throw new Error('Zrušení se nezdařilo');
      }
      const listRes = await fetch('/api/deployments');
      if (listRes.ok) {
        setJobs(await listRes.json());
      }
    } catch {
      setError('Nepodařilo se zrušit deployment');
    } finally {
      setDestroyingIds((prev) => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    }
  }

  return (
    <div className="card card-wide">
      <div className="form-header">
        <h2>Deploymenty</h2>
        <p className="form-subtitle">Aktualizace každých 5 s.</p>
      </div>
      {isLoading && jobs.length === 0 && <p className="status-text">Načítání…</p>}
      {!isLoading && jobs.length === 0 && <p className="status-text">Žádné deploymenty.</p>}
      <div className="job-list">
        {jobs.map((job) => {
          const isDestroyed = job.status === 'destroyed';
          return (
            <div
              key={job.id}
              className={`job-card ${isDestroyed ? 'job-card-disabled' : ''}`}
              onClick={() => !isDestroyed && onSelectJob(job.id)}
            >
            <div className="job-card-body">
              <div className="job-card-field">
                <span className="job-card-label">VM</span>
                <span>{job.config.virtualMachine.name}</span>
              </div>
              <div className="job-card-field">
                <span className="job-card-label">OS</span>
                <span>{job.config.virtualMachine.os}</span>
              </div>
              <div className="job-card-field">
                <span className="job-card-label">Zdroje</span>
                <span>
                  {job.config.virtualMachine.cpu} vCPU / {job.config.virtualMachine.ram} GB / {job.config.virtualMachine.disk} GB
                </span>
              </div>
              <div className="job-card-field">
                <span className="job-card-label">Síť</span>
                <span>{job.config.networkConnection.name}</span>
              </div>
              <div className="job-card-field">
                <span className="job-card-label">IP</span>
                <span>{job.outputs?.ip || '—'}</span>
              </div>
            </div>
              <div className="job-card-footer">
                <span className="job-card-time">
                  {job.createdAt ? new Date(job.createdAt).toLocaleString() : ''}
                </span>
                {job.status === 'done' && (
                  <button
                    className="job-destroy-btn"
                    onClick={(e) => handleDestroy(e, job.id)}
                    disabled={destroyingIds.has(job.id)}
                  >
                    Zrušit
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
      {error && <p className="form-error">{error}</p>}
    </div>
  );
}