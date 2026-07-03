"""Job and DeploymentConfig models. See jobs/repository.py for storage."""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

JobStatus = Literal[
    "planning",
    "awaiting_confirmation",
    "applying",
    "done",
    "error",
    "destroying",
    "destroyed",
]

# Security audit finding: DeploymentConfig fields were free-form strings with
# no length limit, and were interpolated (via json.dumps) into both an HCL
# string literal and a shell command run by Terraform's local-exec
# provisioner. json.dumps only escapes JSON/HCL string syntax - it does not
# neutralize Terraform's `${...}` interpolation or shell metacharacters like
# `$`, backticks, `;`, `|`, quotes, which the provisioner's shell interprets.
# An unsanitized field (e.g. name = '$(rm -rf /)' or '${file("/etc/passwd")}')
# would therefore be a command/template injection vector. Fixed with a strict
# allowlist below: only alphanumerics, spaces, `.`, `_`, `-` are permitted,
# which rules out every character needed for shell or HCL interpolation
# injection, plus explicit length/emptiness/path-traversal checks.
_MAX_FIELD_LENGTH = 100
_SAFE_VALUE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ._-]*$")


class DeploymentConfig(BaseModel):
    name: str
    region: str
    size: str
    image: str

    @field_validator("name", "region", "size", "image")
    @classmethod
    def _validate_safe_value(cls, value: str, info) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError(f"{info.field_name} must not be empty")
        if len(stripped) > _MAX_FIELD_LENGTH:
            raise ValueError(
                f"{info.field_name} must be {_MAX_FIELD_LENGTH} characters or fewer"
            )
        if ".." in stripped or "/" in stripped or "\\" in stripped:
            raise ValueError(f"{info.field_name} must not contain path separators")
        if not _SAFE_VALUE_RE.match(stripped):
            raise ValueError(
                f"{info.field_name} may only contain letters, numbers, spaces, "
                "'.', '_' and '-'"
            )
        return stripped


class JobPlan(BaseModel):
    summary: str
    risks: list[str]


class JobOutputs(BaseModel):
    ip: str
    resourceId: str


class Job(BaseModel):
    id: str
    status: JobStatus
    config: DeploymentConfig
    plan: Optional[JobPlan] = None
    outputs: Optional[JobOutputs] = None
    error: Optional[str] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
