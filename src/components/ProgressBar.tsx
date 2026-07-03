import type { JobStatus } from '../types';

interface ProgressBarProps {
  currentStatus: JobStatus;
}

const config: Record<JobStatus, { width: string; color: string; glow: string }> = {
  planning: { width: '15%', color: '#4b4b57', glow: 'rgba(255, 255, 255, 0.08)' },
  awaiting_confirmation: { width: '40%', color: '#f5a524', glow: 'rgba(245, 165, 36, 0.45)' },
  applying: { width: '75%', color: '#6e5bf6', glow: 'rgba(110, 91, 246, 0.45)' },
  done: { width: '100%', color: '#2dd4a7', glow: 'rgba(45, 212, 167, 0.45)' },
  error: { width: '75%', color: '#f5556c', glow: 'rgba(245, 85, 108, 0.45)' },
  destroying: { width: '75%', color: '#4b4b57', glow: 'rgba(255, 255, 255, 0.08)' },
  destroyed: { width: '100%', color: '#6b6b76', glow: 'rgba(107, 107, 118, 0.35)' },
};

export function ProgressBar({ currentStatus }: ProgressBarProps) {
  const { width, color, glow } = config[currentStatus];

  return (
    <div className="progress-track">
      <div className="progress-fill" style={{ width, background: color, boxShadow: `0 0 12px 1px ${glow}` }} />
    </div>
  );
}