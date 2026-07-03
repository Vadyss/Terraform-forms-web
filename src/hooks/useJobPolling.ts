import { useQuery } from '@tanstack/react-query';
import type { Job } from '../types';

async function fetchJob(jobId: string): Promise<Job> {
  const res = await fetch(`/api/deployments/${jobId}`);
  if (!res.ok) {
    throw new Error('Failed to fetch job');
  }
  return res.json();
}

export function useJobPolling(jobId: string | null) {
  const { data: job, isLoading, isError } = useQuery({
    queryKey: ['job', jobId],
    queryFn: () => fetchJob(jobId as string),
    enabled: jobId !== null,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      const isTerminal = status === 'done' || status === 'error' || status === 'destroyed';
      return status && !isTerminal ? 2000 : false;
    },
  });

  return { job, isLoading, isError };
}
