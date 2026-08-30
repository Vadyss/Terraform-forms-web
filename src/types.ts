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
  | 'applying'
  | 'done'
  | 'error';

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
}

export interface JobOutputs {
  ip: string;
  resourceId: string;
}

export interface Job {
  id: string;
  status: JobStatus;
  config: DeploymentConfig;
  outputs?: JobOutputs;
  error?: string;
  createdAt?: string;
}
