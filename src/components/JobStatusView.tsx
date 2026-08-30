import { useJobPolling } from '../hooks/useJobPolling';
import { Planning } from './screens/Planning';
import { Applying } from './screens/Applying';
import { Done } from './screens/Done';
import { ErrorScreen } from './screens/Error';
import { ProgressBar } from './ProgressBar';

interface JobStatusViewProps {
  jobId: string;
  onBackToDeployments: () => void;
}

export function JobStatusView({ jobId, onBackToDeployments }: JobStatusViewProps) {
  const { job, isLoading, isError } = useJobPolling(jobId);

  if (isLoading || !job) {
    return <Planning />;
  }

  if (isError) {
    return <ErrorScreen error="Nepodařilo se načíst stav jobu" onBackToDeployments={onBackToDeployments} />;
  }

  const screen = () => {
    switch (job.status) {
      case 'applying':
        return <Applying />;
      case 'done':
        return <Done outputs={job.outputs!} onBackToDeployments={onBackToDeployments} />;
      case 'error':
        return <ErrorScreen error={job.error ?? 'Neznámá chyba'} onBackToDeployments={onBackToDeployments} />;
      default:
        return null;
    }
  };

  return (
    <div className="card">
      <div className="app-header">
        <h1><span className="status-dot" aria-hidden="true" /> Deployment</h1>
        <p className="app-header-sub">Job #{jobId.slice(0, 8)}</p>
      </div>
      <ProgressBar currentStatus={job.status} />
      {screen()}
    </div>
  );
}