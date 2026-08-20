export interface DeploymentConfig {

  virtualMachine: {
    name: string;
    os: string;
    cpu: number;
    ram: number;
    disk: number;
    sshkey: string;
  }
}

export interface ValidationErrors {
  virtualMachine?: {
    name?: string;
    os?: string;
    sshkey?: string;
  };
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

export interface StringOption {
  value: string;
  label: string;
}

export interface NumberOption {
  value: number;
  label: string;
}

export interface GetOptions {
  operatingSystems: StringOption[];
  cpuOptions: NumberOption[];
  ramOptions: NumberOption[];
  diskOptions: NumberOption[];
  environmentTypes: StringOption[];
  keyboardLayouts: StringOption[];
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
