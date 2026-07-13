"""FastAPI backend for driving placeholder Terraform deployments.

Endpoints mirror the frontend's MSW mock handlers:
  POST /api/deployments               - create a job, run `terraform plan` async
  GET  /api/deployments                - list all jobs
  GET  /api/deployments/{id}          - fetch job status
  POST /api/deployments/{id}/apply    - run `terraform apply` async
  POST /api/deployments/{id}/destroy  - run `terraform destroy` async

Security audit findings (2026-07-01) and how they were addressed:
  1. CORS was hardcoded to http://localhost:5173. Now reads a comma-separated
     ALLOWED_ORIGINS env var, falling back to the localhost default.
  2. DeploymentConfig had no input validation (see jobs/store.py) - fixed
     with a strip/length/allowlist validator on every field. Its capacity
     guard (MAX_JOBS) now lives in jobs/repository.py.
  3. Terraform/shell injection: config values reach an HCL string literal
     *and* a local-exec shell command. json.dumps() correctly escapes HCL
     string syntax, but does not neutralize Terraform's `${...}` interpolation
     or shell metacharacters (`$`, backticks, `;`, `|`, quotes) that the
     local-exec provisioner's shell will interpret. Fixed upstream by
     restricting DeploymentConfig fields to a safe character allowlist
     (see jobs/store.py) so no such metacharacters can reach generator.py.
  4. Job directory traversal: job_dir_for() joins JOBS_ROOT with job_id.
     Job ids are always server-generated uuid4 values and the store is
     looked up by exact key before any filesystem path is built, so a
     path-traversal job_id can never reach job_dir_for() today. As
     defense-in-depth (in case the store or id scheme ever changes), the
     job_id path parameter is now validated as a UUID before use.
  5. Subprocess execution: runner.py already uses
     asyncio.create_subprocess_exec with an argument list (no shell=True,
     no string concatenation), so it is not susceptible to shell injection
     at the Python level. No change needed there.
  6. Error messages: exceptions raised by terraform (e.g. from
     RuntimeError in runner.CommandResult.check) can embed the job's
     absolute /tmp path. These were being stored verbatim and returned to
     API clients via the `error` field. Fixed by sanitizing paths out of
     the message before storing it, and logging the full detail
     server-side instead.
  7. In-memory store had no bound and could grow without limit under
     load/abuse. Fixed with a MAX_JOBS cap in jobs/repository.py that
     rejects new jobs with a 503 once reached.
  8. No authentication/authorization exists on any endpoint. Not
     implemented per instructions; see the marker comment below for where
     an auth dependency should be inserted.
  9. outputs.ip was hardcoded to "0.0.0.0" instead of being read from
     Terraform, which would silently produce a wrong IP once generator.py
     is swapped to a real cloud resource. Fixed by reading it from a new
     `ip` output (see generator.py and runner.output_value below).
"""
from __future__ import annotations

import asyncio
import logging
import os
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from options.repository import options_repository
from jobs.repository import JobStoreFullError, job_repository
from jobs.store import DeploymentConfig, Job, JobOutputs, JobPlan
from terraform import generator, runner

logger = logging.getLogger(__name__)

JOBS_ROOT = Path("/tmp/jobs")

STATIC_RISKS = [
    "null_resource: nevytváří se žádná reálná infrastruktura",
    "tfstate je uložen lokálně v /tmp",
]

_DEFAULT_ALLOWED_ORIGINS = ["http://localhost:5173"]


def _allowed_origins() -> list[str]:
    raw = os.environ.get("ALLOWED_ORIGINS")
    if not raw:
        return _DEFAULT_ALLOWED_ORIGINS
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    return origins or _DEFAULT_ALLOWED_ORIGINS


app = FastAPI()

# SECURITY: no authentication/authorization is implemented anywhere in this
# API. Before exposing this beyond local/dev use, add an auth dependency
# (e.g. `Depends(require_auth)` verifying an OAuth2/JWT bearer token) to the
# route decorators below, or register it as global middleware here.
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)


def job_dir_for(job_id: str) -> Path:
    return JOBS_ROOT / job_id


def _require_valid_job_id(job_id: str) -> None:
    """Defense-in-depth: job ids are always server-generated uuid4 values
    and are used to build filesystem paths in job_dir_for(). Reject
    anything that isn't a well-formed UUID before it can reach the store
    or filesystem layer."""
    try:
        uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Job not found")


def _sanitize_error(message: str, job_dir: Path) -> str:
    """Strip internal filesystem paths out of error text before it is
    returned to API clients."""
    sanitized = message.replace(str(job_dir), "<job_dir>")
    sanitized = sanitized.replace(str(JOBS_ROOT), "<jobs_root>")
    return sanitized


async def run_plan(job_id: str) -> None:
    job = await job_repository.get(job_id)
    if job is None:
        return
    job_dir = job_dir_for(job_id)
    try:
        generator.write_main_tf(job_dir, job.config)
        await runner.init(job_dir)
        plan_result = await runner.plan(job_dir)
        for line in reversed(plan_result.stdout.splitlines()):
            stripped = line.strip()
            if stripped.startswith("Plan:"):
                summary = stripped
                break
        else:
            summary = "Plan complete"
        await job_repository.update(
            job_id,
            status="awaiting_confirmation",
            plan=JobPlan(summary=summary, risks=STATIC_RISKS),
        )
    except Exception as exc:  # noqa: BLE001 - surface any failure as a job error
        logger.exception("plan failed for job %s", job_id)
        await job_repository.update(job_id, status="error", error=_sanitize_error(str(exc), job_dir))


async def run_apply(job_id: str) -> None:
    job = await job_repository.get(job_id)
    if job is None:
        return
    job_dir = job_dir_for(job_id)
    try:
        await runner.apply(job_dir)
        resource_id = await runner.output_value(job_dir, "resource_id")
        ip = await runner.output_value(job_dir, "ip")
        await job_repository.update(
            job_id,
            status="done",
            outputs=JobOutputs(ip=ip, resourceId=resource_id),
        )
    except Exception as exc:  # noqa: BLE001 - surface any failure as a job error
        logger.exception("apply failed for job %s", job_id)
        await job_repository.update(job_id, status="error", error=_sanitize_error(str(exc), job_dir))


async def run_destroy(job_id: str) -> None:
    job = await job_repository.get(job_id)
    if job is None:
        return
    job_dir = job_dir_for(job_id)
    try:
        await runner.destroy(job_dir)
        await job_repository.update(job_id, status="destroyed")
    except Exception as exc:  # noqa: BLE001 - surface any failure as a job error
        logger.exception("destroy failed for job %s", job_id)
        await job_repository.update(job_id, status="error", error=_sanitize_error(str(exc), job_dir))


# SECURITY: insert an auth dependency (e.g. `current_user: User = Depends(require_auth)`)
# as a parameter on each route below once authentication is implemented.
@app.post("/api/deployments", status_code=201)
async def create_deployment(config: DeploymentConfig):
    job_id = str(uuid.uuid4())
    job = Job(id=job_id, status="planning", config=config)
    try:
        await job_repository.create(job)
    except JobStoreFullError:
        raise HTTPException(status_code=503, detail="Service is at capacity, try again later")
    asyncio.create_task(run_plan(job_id))
    return {"id": job_id}


@app.get("/api/deployments", response_model=list[Job], response_model_exclude_none=True)
async def list_deployments():
    return await job_repository.list_all()

@app.get("/api/deployments/{job_id}", response_model=Job, response_model_exclude_none=True)
async def get_deployment(job_id: str):
    _require_valid_job_id(job_id)
    job = await job_repository.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.get("/api/options")
async def send_options():
    return await options_repository.get_options()
    
@app.post(
    "/api/deployments/{job_id}/apply",
    response_model=Job,
    response_model_exclude_none=True,
)
async def apply_deployment(job_id: str):
    _require_valid_job_id(job_id)
    job = await job_repository.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "awaiting_confirmation":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot apply job in status '{job.status}'",
        )
    job = await job_repository.update(job_id, status="applying")
    asyncio.create_task(run_apply(job_id))
    return job


@app.post(
    "/api/deployments/{job_id}/destroy",
    response_model=Job,
    response_model_exclude_none=True,
)
async def destroy_deployment(job_id: str):
    _require_valid_job_id(job_id)
    job = await job_repository.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "done":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot destroy job in status '{job.status}'",
        )
    job = await job_repository.update(job_id, status="destroying")
    asyncio.create_task(run_destroy(job_id))
    return job