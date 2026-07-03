export interface DeploymentConfig {
  name: string;
  region: string;
  size: string;
  image: string;
}

export type JobStatus =
  | 'planning'
  | 'awaiting_confirmation'
  | 'applying'
  | 'done'
  | 'error'
  | 'destroying'
  | 'destroyed';

export interface JobPlan {
  summary: string;
  risks: string[];
}

export interface JobOutputs {
  ip: string;
  resourceId: string;
}

export interface Job {
  id: string;
  status: JobStatus;
  config: DeploymentConfig;
  plan?: JobPlan;
  outputs?: JobOutputs;
  error?: string;
  createdAt?: string;
}
