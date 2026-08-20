"""FastAPI backend for accepting deployment requests.

Endpoints:
  POST /api/deployments        - validate a deployment config and create a job
  GET  /api/deployments        - list all jobs
  GET  /api/deployments/{id}  - fetch job status
  GET  /api/options            - fetch form options"""

from __future__ import annotations

import os
import uuid
from pathlib import Path

import requests
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from proxmox.repository import proxmox_get_status
from proxmox.repository import proxmox_get_vmid
from options.repository import options_repository
from jobs.repository import JobStoreFullError, job_repository
from jobs.store import DeploymentConfig, Job

_DEFAULT_ALLOWED_ORIGINS = ["http://localhost:5173"]

def _allowed_origins() -> list[str]:
    raw = os.environ.get("ALLOWED_ORIGINS")
    if not raw:
        return _DEFAULT_ALLOWED_ORIGINS
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    return origins or _DEFAULT_ALLOWED_ORIGINS

app = FastAPI()

# SECURITY (audit 2026-08-17):
#   1. No authentication/authorization on any endpoint - anyone who can
#      reach this API can create and read jobs. Before exposing this beyond
#      local/dev use, add an auth dependency (e.g. `Depends(require_auth)`
#      verifying an OAuth2/JWT bearer token) to the route decorators below,
#      or register it as global middleware here.
#   2. No per-client rate limiting on job creation. Combined with #1, an
#      unauthenticated caller can spam POST /api/deployments until MAX_JOBS
#      (jobs/repository.py) is hit, and since the apply/destroy endpoints
#      were removed there is no way to clear jobs short of restarting the
#      process - a trivial denial-of-service against everyone else. Add a
#      rate limiter (e.g. slowapi) or require auth so abuse is attributable
#      and blockable.
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)


def _require_valid_job_id(job_id: str) -> None:
    """Defense-in-depth: job ids are always server-generated uuid4 values.
    Reject anything that isn't a well-formed UUID before it can reach the
    job store lookup."""
    try:
        uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Job not found")

@app.get("/api/proxmox/status")
def get_status():
    return proxmox_get_status()

@app.get("/api/proxmox/vmid/next")
def get_vmid():
    return proxmox_get_vmid()

# SECURITY: see the audit note above app.add_middleware(...) - insert an
# auth dependency (e.g. `current_user: User = Depends(require_auth)`) as a
# parameter on each route below once authentication is implemented.
@app.post("/api/deployments", status_code=201)
async def create_deployment(config: DeploymentConfig):
    job_id = str(uuid.uuid4())
    job = Job(id=job_id, status="applying", config=config)
    try:
        await job_repository.create(job)
    except JobStoreFullError:
        raise HTTPException(status_code=503, detail="Service is at capacity, try again later")
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

# Servíruje zbuilděný frontend (npm run build → ../dist).
# Musí být připojené AŽ NAKONEC, aby /api/* routy výše měly přednost.
# Guard: backend nastartuje i v devu, než je frontend zbuilděný.
_FRONTEND_DIST = Path(__file__).resolve().parent.parent / "dist"
if _FRONTEND_DIST.is_dir():
    app.mount("/", StaticFiles(directory=str(_FRONTEND_DIST), html=True), name="frontend")