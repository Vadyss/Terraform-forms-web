"""Runs terraform commands via asyncio subprocesses.

Security audit finding: _run() already uses asyncio.create_subprocess_exec
with an explicit argument list (no shell=True, no shell string
concatenation), so arguments are passed directly to execve and are never
parsed by a shell. This is safe against shell injection at the Python
level - no change needed here.
"""
from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CommandResult:
    returncode: int
    stdout: str
    stderr: str

    def check(self, action: str) -> None:
        if self.returncode != 0:
            raise RuntimeError(f"terraform {action} failed: {self.stderr or self.stdout}")


async def _run(cwd: Path, *args: str) -> CommandResult:
    proc = await asyncio.create_subprocess_exec(
        "terraform",
        *args,
        cwd=str(cwd),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    return CommandResult(
        returncode=proc.returncode,
        stdout=stdout.decode(),
        stderr=stderr.decode(),
    )


async def init(job_dir: Path) -> CommandResult:
    result = await _run(job_dir, "init", "-input=false", "-no-color")
    result.check("init")
    return result


async def plan(job_dir: Path) -> CommandResult:
    result = await _run(job_dir, "plan", "-input=false", "-no-color", "-out=tfplan")
    result.check("plan")
    return result


async def apply(job_dir: Path) -> CommandResult:
    result = await _run(job_dir, "apply", "-input=false", "-no-color", "-auto-approve", "tfplan")
    result.check("apply")
    return result


async def output_value(job_dir: Path, name: str) -> str:
    result = await _run(job_dir, "output", "-json", name)
    result.check("output")
    return json.loads(result.stdout)


async def destroy(job_dir: Path) -> CommandResult:
    result = await _run(job_dir, "destroy", "-auto-approve", "-no-color")
    result.check("destroy")
    return result
