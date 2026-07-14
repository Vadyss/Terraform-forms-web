"""Job and DeploymentConfig models. See jobs/repository.py for storage."""
from __future__ import annotations

import ipaddress
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
_MAX_PASSWORD_LENGTH = 200
_SAFE_VALUE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ._-]*$")


def _validate_safe_value(value: str, field_name: str) -> str:
    """Allowlist validation for values that end up in Terraform config."""
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


def _validate_optional_ip(value: str, field_name: str) -> str:
    """Empty is allowed (field may be unused); anything else must be a valid IP."""
    stripped = value.strip()
    if not stripped:
        return ""
    try:
        ipaddress.ip_address(stripped)
    except ValueError:
        raise ValueError(f"{field_name} must be a valid IP address")
    return stripped


class NetworkConnection(BaseModel):
    name: str
    subnet: str
    portSecurity: bool
    internet: bool

    @field_validator("name", "subnet")
    @classmethod
    def _validate_fields(cls, value: str, info) -> str:
        return _validate_safe_value(value, info.field_name)


class VirtualMachine(BaseModel):
    name: str
    os: str
    cpu: int = Field(ge=1, le=128)
    ram: int = Field(ge=1, le=1024)
    disk: int = Field(ge=1, le=10000)

    @field_validator("name", "os")
    @classmethod
    def _validate_fields(cls, value: str, info) -> str:
        return _validate_safe_value(value, info.field_name)


class Networks(BaseModel):
    lan: bool
    lanIp: str = ""
    ipConfig: Literal["dhcp", "static"]
    staticIp: str = ""

    @field_validator("lanIp", "staticIp")
    @classmethod
    def _validate_ips(cls, value: str, info) -> str:
        return _validate_optional_ip(value, info.field_name)


class Guacamole(BaseModel):
    enabled: bool
    os: str = ""
    type: str = ""
    keyboardLayout: str = ""
    username: str = ""
    password: str = ""
    sftp: bool = False

    @field_validator("os", "type", "keyboardLayout", "username")
    @classmethod
    def _validate_fields(cls, value: str, info) -> str:
        # These may legitimately be empty when Guacamole is disabled.
        if not value.strip():
            return ""
        return _validate_safe_value(value, info.field_name)

    @field_validator("password")
    @classmethod
    def _validate_password(cls, value: str) -> str:
        # Passwords must allow special characters, so the allowlist does not
        # apply. They are never interpolated into Terraform config or shell
        # commands - only passed as data - so length is the only constraint.
        if len(value) > _MAX_PASSWORD_LENGTH:
            raise ValueError(
                f"password must be {_MAX_PASSWORD_LENGTH} characters or fewer"
            )
        return value


class DeploymentConfig(BaseModel):
    networkConnection: NetworkConnection
    virtualMachine: VirtualMachine
    networks: Networks
    guacamole: Guacamole


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