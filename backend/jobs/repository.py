"""Job storage abstraction.

`JobRepository` is the only interface the rest of the backend is allowed to
use for reading/writing jobs. `InMemoryJobRepository` is the current default
implementation. To back this with a real database, implement
`JobRepository`'s four methods against your DB driver and swap the
`job_repository` instance below for it - no other file needs to change.
"""
from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import Optional

class JobStoreFullError(RuntimeError):
    """Raised when a repository has reached its capacity (e.g. MAX_JOBS)."""

class JobRepository(ABC):
    """Abstract job storage. Implement this against a real DB to replace
    InMemoryJobRepository - every method is async so a DB-backed
    implementation can use a real driver without blocking the event loop."""

    @abstractmethod
    async def create(self, job: Job) -> None:
        """Persist a new job. Raise JobStoreFullError if at capacity."""

    @abstractmethod
    async def get(self, job_id: str) -> Optional[Job]:
        """Fetch a job by id, or None if it doesn't exist."""

    @abstractmethod
    async def list_all(self) -> list[Job]:
        """Return all jobs, newest first."""

    @abstractmethod
    async def update(self, job_id: str, **fields) -> Optional[Job]:
        """Apply a partial update to a job and return the updated job, or
        None if it doesn't exist."""

class InMemoryJobRepository(JobRepository):
    """Default in-process implementation, keyed by job id in a dict."""

    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = asyncio.Lock()

    async def create(self, job: Job) -> None:
        async with self._lock:
            if len(self._jobs) >= MAX_JOBS:
                raise JobStoreFullError(f"job store has reached its capacity of {MAX_JOBS}")
            self._jobs[job.id] = job

    async def get(self, job_id: str) -> Optional[Job]:
        async with self._lock:
            return self._jobs.get(job_id)

    async def list_all(self) -> list[Job]:
        async with self._lock:
            return sorted(self._jobs.values(), key=lambda job: job.createdAt, reverse=True)

    async def update(self, job_id: str, **fields) -> Optional[Job]:
        async with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return None
            updated = job.model_copy(update=fields)
            self._jobs[job_id] = updated
            return updated

# Single place to swap storage backends, e.g.:
#   job_repository: JobRepository = PostgresJobRepository(dsn=os.environ["DATABASE_URL"])
job_repository: JobRepository = InMemoryJobRepository()
