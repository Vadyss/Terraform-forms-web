import type { JobStatus } from '../types';

interface ProgressBarProps {
  currentStatus: JobStatus;
}

const config: Record<JobStatus, { width: string; color: string; glow: string }> = {
  applying: { width: '75%', color: '#6e5bf6', glow: 'rgba(110, 91, 246, 0.45)' },
  done: { width: '100%', color: '#2dd4a7', glow: 'rgba(45, 212, 167, 0.45)' },
  error: { width: '75%', color: '#f5556c', glow: 'rgba(245, 85, 108, 0.45)' },
};

export function ProgressBar({ currentStatus }: ProgressBarProps) {
  const { width, color, glow } = config[currentStatus];

  return (
    <div className="progress-track">
      <div className="progress-fill" style={{ width, background: color, boxShadow: `0 0 12px 1px ${glow}` }} />
    </div>
  );
}