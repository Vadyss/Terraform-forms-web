import type { DeploymentConfig, Job } from '../types';

const jobs = new Map<string, Job>();

const PLAN_DELAY_MS = 3000;
const APPLY_DELAY_MS = 3000;

function mockPlanFor(config: DeploymentConfig) {
  return {
    summary: `Plan: create ${config.size} instance "${config.name}" (${config.image}) in ${config.region}.`,
    risks: [
      'Resource will incur ongoing cloud costs.',
      'Region change after creation requires a full replace.',
    ],
  };
}

function mockOutputsFor(config: DeploymentConfig) {
  const octet = () => Math.floor(Math.random() * 255);
  return {
    ip: `10.${octet()}.${octet()}.${octet()}`,
    resourceId: `res-${config.name}-${Math.random().toString(36).slice(2, 8)}`,
  };
}

export function createJob(config: DeploymentConfig): Job {
  const id = crypto.randomUUID();
  const job: Job = { id, status: 'planning', config };
  jobs.set(id, job);

  setTimeout(() => {
    const current = jobs.get(id);
    if (!current || current.status !== 'planning') return;
    jobs.set(id, {
      ...current,
      status: 'awaiting_confirmation',
      plan: mockPlanFor(current.config),
    });
  }, PLAN_DELAY_MS);

  return job;
}

export function getJob(id: string): Job | undefined {
  return jobs.get(id);
}

export function applyJob(id: string): Job | undefined {
  const current = jobs.get(id);
  if (!current) return undefined;

  const applying: Job = { ...current, status: 'applying' };
  jobs.set(id, applying);

  setTimeout(() => {
    const job = jobs.get(id);
    if (!job || job.status !== 'applying') return;
    jobs.set(id, {
      ...job,
      status: 'done',
      outputs: mockOutputsFor(job.config),
    });
  }, APPLY_DELAY_MS);

  return applying;
}
