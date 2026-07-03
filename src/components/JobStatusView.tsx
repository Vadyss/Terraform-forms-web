import { useQueryClient } from '@tanstack/react-query';
import { useJobPolling } from '../hooks/useJobPolling';
import { Planning } from './screens/Planning';
import { AwaitingConfirmation } from './screens/AwaitingConfirmation';
import { Applying } from './screens/Applying';
import { Done } from './screens/Done';
import { ErrorScreen } from './screens/Error';
import { Destroying } from './screens/Destroying';
import { Destroyed } from './screens/Destroyed';
import { ProgressBar } from './ProgressBar';

interface JobStatusViewProps {
  jobId: string;
  onBackToDeployments: () => void;
}

export function JobStatusView({ jobId, onBackToDeployments }: JobStatusViewProps) {
  const { job, isLoading, isError } = useJobPolling(jobId);
  const queryClient = useQueryClient();

  if (isLoading || !job) {
    return <Planning />;
  }

  if (isError) {
    return <ErrorScreen error="Nepodařilo se načíst stav jobu" onBackToDeployments={onBackToDeployments} />;
  }

  async function handleConfirm() {
    await fetch(`/api/deployments/${jobId}/apply`, { method: 'POST' });
    await queryClient.invalidateQueries({ queryKey: ['job', jobId] });
  }

  const screen = () => {
    switch (job.status) {
      case 'planning':
        return <Planning />;
      case 'awaiting_confirmation':
        return <AwaitingConfirmation plan={job.plan!} onConfirm={handleConfirm} />;
      case 'applying':
        return <Applying />;
      case 'done':
        return <Done outputs={job.outputs!} onBackToDeployments={onBackToDeployments} />;
      case 'error':
        return <ErrorScreen error={job.error ?? 'Neznámá chyba'} onBackToDeployments={onBackToDeployments} />;
      case 'destroying':
        return <Destroying />;
      case 'destroyed':
        return <Destroyed onBackToDeployments={onBackToDeployments} />;
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