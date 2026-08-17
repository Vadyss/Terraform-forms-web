"""Job and DeploymentConfig models. See jobs/repository.py for storage."""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

JobStatus = Literal[
    "applying",
    "done",
    "error",
]

_MAX_FIELD_LENGTH = 100
_SAFE_VALUE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ._-]*$")

def _validate_safe_value(value: str, field_name: str) -> str:
    """Allowlist validation for values that end up as the VM name sent to
    the target API."""
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{field_name} must not be empty")
    if len(stripped) > _MAX_FIELD_LENGTH:
        raise ValueError(
            f"{field_name} must be {_MAX_FIELD_LENGTH} characters or fewer"
        )
    if ".." in stripped or "/" in stripped or "\\" in stripped:
        raise ValueError(f"{field_name} must not contain path separators")
    if not _SAFE_VALUE_RE.match(stripped):
        raise ValueError(
            f"{field_name} may only contain letters, numbers, spaces, "
            "'.', '_' and '-'"
        )
    return stripped

class VirtualMachine(BaseModel):
    name: str
    os: Literal["ubuntu-22.04", "debian-12"]
    cpu: int = Field(ge=1, le=128)
    ram: int = Field(ge=1, le=1024)
    disk: int = Field(ge=1, le=10000)
    
    @field_validator("name")
    @classmethod
    def _validate_fields(cls, value: str, info) -> str:
        return _validate_safe_value(value, info.field_name)

class DeploymentConfig(BaseModel):
    virtualMachine: VirtualMachine


class JobOutputs(BaseModel):
    ip: str
    resourceId: str


class Job(BaseModel):
    id: str
    status: JobStatus
    config: DeploymentConfig
    outputs: Optional[JobOutputs] = None
    error: Optional[str] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))