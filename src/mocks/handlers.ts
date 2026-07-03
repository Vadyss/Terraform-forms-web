import { http, HttpResponse } from 'msw';
import type { DeploymentConfig } from '../types';
import { applyJob, createJob, getJob } from './store';

export const handlers = [
  http.post('/api/deployments', async ({ request }) => {
    const config = (await request.json()) as DeploymentConfig;
    const job = createJob(config);
    return HttpResponse.json({ id: job.id }, { status: 201 });
  }),

  http.get('/api/deployments/:id', ({ params }) => {
    const job = getJob(params.id as string);
    if (!job) {
      return HttpResponse.json({ error: 'Job not found' }, { status: 404 });
    }
    return HttpResponse.json(job);
  }),

  http.post('/api/deployments/:id/apply', ({ params }) => {
    const job = applyJob(params.id as string);
    if (!job) {
      return HttpResponse.json({ error: 'Job not found' }, { status: 404 });
    }
    return HttpResponse.json(job);
  }),
];
