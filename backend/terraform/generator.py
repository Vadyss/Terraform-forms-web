"""Generates placeholder Terraform config from a deployment config.

No real cloud provider is used: the resource is a `null_resource` whose
local-exec provisioner just echoes the submitted values.

Security audit finding: config values below are interpolated into an HCL
string literal (via json.dumps) and, for `command`, into a shell command
string that Terraform's local-exec provisioner passes to a shell. json.dumps
correctly escapes HCL string syntax (quotes/backslashes/control chars), but
it does NOT neutralize Terraform's `${...}` interpolation syntax or shell
metacharacters (`$`, backticks, `;`, `|`, etc.) - a value like
'$(rm -rf /)' or '${file("/etc/passwd")}' would be executed/evaluated
unless blocked earlier. This module intentionally does no sanitization
itself; safety instead relies on DeploymentConfig's field validators
(backend/jobs/store.py) restricting every interpolated field to a strict
alphanumeric/space/`.`/`_`/`-` allowlist before it ever reaches here. Do not
call write_main_tf with unvalidated config.

NOTE: guacamole.password is deliberately NOT interpolated into the Terraform
config here - it is not allowlist-validated (passwords need special chars),
so writing it into an HCL/shell context would reintroduce the injection
vector the allowlist closes. When wiring up a real Guacamole provisioner,
pass it via a sensitive variable / file, never via string interpolation.

To connect a real hypervisor (Hyper-V) provider: replace the `null_resource`
block below with the provider's resources (VM, network, etc.), and change the
`ip` output to the VM's real IP attribute instead of the empty placeholder.
No other file in the pipeline needs to change.
"""
from __future__ import annotations

import json
from pathlib import Path

from jobs.store import DeploymentConfig


def write_main_tf(job_dir: Path, config: DeploymentConfig) -> Path:
    """Write main.tf into job_dir and return its path."""
    job_dir.mkdir(parents=True, exist_ok=True)

    vm = config.virtualMachine

    command = (
        f"echo Deploying VM {json.dumps(vm.name)} "
        f"os={json.dumps(vm.os)} "
        f"cpu={vm.cpu} ram={vm.ram} disk={vm.disk}"
    )

    main_tf = f"""\
terraform {{
  required_providers {{
    null = {{
      source  = "hashicorp/null"
      version = "~> 3.0"
    }}
  }}
}}

resource "null_resource" "deployment" {{
  triggers = {{

    vm_name         = {json.dumps(vm.name)}
    vm_os           = {json.dumps(vm.os)}
    vm_cpu          = {json.dumps(str(vm.cpu))}
    vm_ram          = {json.dumps(str(vm.ram))}
    vm_disk         = {json.dumps(str(vm.disk))}
    
  }}

  provisioner "local-exec" {{
    command = {json.dumps(command)}
  }}
}}

output "resource_id" {{
  value = null_resource.deployment.id
}}

output "ip" {{
  value = ""
}}
"""

    main_tf_path = job_dir / "main.tf"
    main_tf_path.write_text(main_tf)
    return main_tf_path