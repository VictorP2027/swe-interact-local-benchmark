"""Opaque host identity for keeping each task's two arms together."""

import hashlib
from pathlib import Path
import platform
import re
import subprocess
import uuid


def machine_id():
    identity = None
    if platform.system() == "Darwin":
        output = subprocess.check_output(["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"], text=True)
        match = re.search(r'"IOPlatformUUID"\s*=\s*"([^"]+)"', output)
        identity = match.group(1) if match else None
    elif Path("/etc/machine-id").exists():
        identity = Path("/etc/machine-id").read_text().strip()
    if not identity:
        identity = f"{platform.node()}:{uuid.getnode()}"
    return hashlib.sha256(("cs224v-paired-host-v1:" + identity).encode()).hexdigest()
