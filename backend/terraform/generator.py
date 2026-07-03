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
itself; safety instead relies on DeploymentConfig's field validator
(backend/jobs/store.py) restricting every field to a strict
alphanumeric/space/`.`/`_`/`-` allowlist before it ever reaches here. Do not
call write_main_tf with unvalidated config.

To connect a real cloud provider: replace the `null_resource` block below
with the provider's resource (region/size/image map onto its
region/instance-type/AMI-equivalent attributes), and change the `ip` output
to the resource's real public IP attribute instead of the empty placeholder.
No other file in the pipeline needs to change.
"""
from __future__ import annotations

import json
from pathlib import Path

from jobs.store import DeploymentConfig


def write_main_tf(job_dir: Path, config: DeploymentConfig) -> Path:
    """Write main.tf into job_dir and return its path."""
    job_dir.mkdir(parents=True, exist_ok=True)

    command = (
        f"echo Deploying {json.dumps(config.name)} "
        f"region={json.dumps(config.region)} "
        f"size={json.dumps(config.size)} "
        f"image={json.dumps(config.image)}"
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
    name   = {json.dumps(config.name)}
    region = {json.dumps(config.region)}
    size   = {json.dumps(config.size)}
    image  = {json.dumps(config.image)}
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
