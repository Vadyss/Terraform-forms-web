import { useEffect, useRef, useState } from 'react';
import type { MouseEvent } from 'react';
import { Play, Square, Trash2 } from 'lucide-react';
import type { Job, JobStatus } from '../../types';

interface DeploymentListProps {
  onSelectJob: (id: string) => void;
}

type VmStatus = 'running' | 'stopped' | 'unknown';
type JobAction = 'start' | 'stop' | 'delete';

interface ConfirmTarget {
  jobId: string;
  resourceId: string;
  name: string;
}

const POLL_INTERVAL_MS = 5000;

const STATUS_LABEL: Record<JobStatus, string> = {
  applying: 'Aplikace',
  done: 'Hotovo',
  error: 'Chyba',
};

export function DeploymentList({ onSelectJob }: DeploymentListProps) {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [vmStatus, setVmStatus] = useState<Record<string, VmStatus>>({});
  const [statusLoading, setStatusLoading] = useState<Record<string, boolean>>({});
  const [actionLoading, setActionLoading] = useState<Record<string, JobAction>>({});
  const [actionErrors, setActionErrors] = useState<Record<string, string>>({});
  const [confirmTarget, setConfirmTarget] = useState<ConfirmTarget | null>(null);
  const fetchedStatusIds = useRef<Set<string>>(new Set());

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

  useEffect(() => {
    jobs.forEach((job) => {
      const resourceId = job.outputs?.resourceId;
      if (job.status !== 'done' || !resourceId) return;
      if (fetchedStatusIds.current.has(resourceId)) return;
      fetchedStatusIds.current.add(resourceId);
      fetchVmStatus(resourceId);
    });
  }, [jobs]);

  async function fetchVmStatus(resourceId: string) {
    setStatusLoading((prev) => ({ ...prev, [resourceId]: true }));
    try {
      const res = await fetch(`/api/deployment/status/${resourceId}`);
      if (!res.ok) {
        throw new Error('Nepodařilo se zjistit stav VM');
      }
      const data: { status?: string } = await res.json();
      setVmStatus((prev) => ({
        ...prev,
        [resourceId]: data.status === 'running' ? 'running' : 'stopped',
      }));
    } catch {
      setVmStatus((prev) => ({ ...prev, [resourceId]: 'unknown' }));
    } finally {
      setStatusLoading((prev) => ({ ...prev, [resourceId]: false }));
    }
  }

  async function handleToggleRun(e: MouseEvent, job: Job) {
    e.stopPropagation();
    const resourceId = job.outputs?.resourceId;
    if (!resourceId) return;
    const action: JobAction = vmStatus[resourceId] === 'running' ? 'stop' : 'start';
    setActionLoading((prev) => ({ ...prev, [job.id]: action }));
    setActionErrors((prev) => {
      const next = { ...prev };
      delete next[job.id];
      return next;
    });
    try {
      const res = await fetch(`/api/deployment/${action}/${resourceId}`, { method: 'POST' });
      if (!res.ok) {
        throw new Error();
      }
      await fetchVmStatus(resourceId);
    } catch {
      setActionErrors((prev) => ({
        ...prev,
        [job.id]: action === 'start' ? 'Spuštění se nezdařilo' : 'Zastavení se nezdařilo',
      }));
    } finally {
      setActionLoading((prev) => {
        const next = { ...prev };
        delete next[job.id];
        return next;
      });
    }
  }

  function requestDelete(e: MouseEvent, job: Job) {
    e.stopPropagation();
    const resourceId = job.outputs?.resourceId;
    if (!resourceId) return;
    setConfirmTarget({ jobId: job.id, resourceId, name: job.config.virtualMachine.name });
  }

  function cancelDelete() {
    setConfirmTarget(null);
  }

  async function confirmDelete() {
    if (!confirmTarget) return;
    const { jobId, resourceId } = confirmTarget;
    setConfirmTarget(null);
    setActionLoading((prev) => ({ ...prev, [jobId]: 'delete' }));
    setActionErrors((prev) => {
      const next = { ...prev };
      delete next[jobId];
      return next;
    });
    try {
      const res = await fetch(`/api/deployment/delete/${resourceId}`, { method: 'DELETE' });
      if (!res.ok) {
        throw new Error();
      }
      fetchedStatusIds.current.delete(resourceId);
      setVmStatus((prev) => {
        const next = { ...prev };
        delete next[resourceId];
        return next;
      });
      const listRes = await fetch('/api/deployments');
      if (listRes.ok) {
        setJobs(await listRes.json());
      }
    } catch {
      setActionErrors((prev) => ({ ...prev, [jobId]: 'Smazání se nezdařilo' }));
    } finally {
      setActionLoading((prev) => {
        const next = { ...prev };
        delete next[jobId];
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
          const resourceId = job.outputs?.resourceId;
          const canManage = job.status === 'done' && !!resourceId;
          const vmState = resourceId ? vmStatus[resourceId] : undefined;
          const isStatusLoading = resourceId ? !!statusLoading[resourceId] : false;
          const runningAction = actionLoading[job.id];
          const isToggleBusy = isStatusLoading || runningAction === 'start' || runningAction === 'stop';
          const isDeleteBusy = runningAction === 'delete';
          const isRunning = vmState === 'running';

          return (
            <div
              key={job.id}
              className="job-card"
              onClick={() => onSelectJob(job.id)}
            >
            <div className="job-card-body">
              <div className="job-card-field">
                <span className="job-card-label">Stav</span>
                <span>{STATUS_LABEL[job.status]}</span>
              </div>
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
                <span className="job-card-label">IP</span>
                <span>{job.outputs?.ip || '—'}</span>
              </div>
            </div>
              <div className="job-card-footer">
                <span className="job-card-time">
                  {job.createdAt ? new Date(job.createdAt).toLocaleString() : ''}
                </span>
                {canManage && (
                  <div className="job-card-footer-end">
                    <div className="job-card-actions">
                      <button
                        type="button"
                        className={`job-icon-btn ${isRunning ? 'job-icon-btn-stop' : 'job-icon-btn-start'}`}
                        onClick={(e) => handleToggleRun(e, job)}
                        disabled={isToggleBusy || vmState === undefined}
                        title={isRunning ? 'Zastavit VM' : 'Spustit VM'}
                        aria-label={isRunning ? 'Zastavit VM' : 'Spustit VM'}
                      >
                        {isToggleBusy ? (
                          <span className="job-icon-spinner" aria-hidden="true" />
                        ) : isRunning ? (
                          <Square size={16} aria-hidden="true" />
                        ) : (
                          <Play size={16} aria-hidden="true" />
                        )}
                      </button>
                      <button
                        type="button"
                        className="job-icon-btn job-icon-btn-danger"
                        onClick={(e) => requestDelete(e, job)}
                        disabled={isDeleteBusy}
                        title="Smazat VM"
                        aria-label="Smazat VM"
                      >
                        {isDeleteBusy ? (
                          <span className="job-icon-spinner" aria-hidden="true" />
                        ) : (
                          <Trash2 size={16} aria-hidden="true" />
                        )}
                      </button>
                    </div>
                    {actionErrors[job.id] && (
                      <span className="job-action-error">{actionErrors[job.id]}</span>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
      {error && <p className="form-error">{error}</p>}
      {confirmTarget && (
        <div className="confirm-overlay" onClick={cancelDelete}>
          <div className="confirm-modal" onClick={(e) => e.stopPropagation()}>
            <h3>Smazat VM</h3>
            <p>Opravdu smazat VM {confirmTarget.name}?</p>
            <div className="confirm-modal-actions">
              <button type="button" className="confirm-cancel-btn" onClick={cancelDelete}>
                Zrušit
              </button>
              <button type="button" className="confirm-delete-btn" onClick={confirmDelete}>
                Smazat
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
