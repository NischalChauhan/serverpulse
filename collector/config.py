
import os
from pathlib import Path

# OPSPULSE AGENT CONFIGURATION

AGENT_KEY_PATH = Path("/etc/opspulse/agent.key")

API_URL = os.getenv(
    "OPSPULSE_API_URL",
    "http://127.0.0.1:8000/api/metrics/ingest",
)

SERVER_ID = int(os.getenv("OPSPULSE_SERVER_ID", "1"))

COLLECTION_INTERVAL = int(
    os.getenv("OPSPULSE_COLLECTION_INTERVAL", "15")
)


def load_agent_key() -> str:
    if not AGENT_KEY_PATH.exists():
        raise FileNotFoundError(
            f"Agent key not found: {AGENT_KEY_PATH}"
        )

    if not AGENT_KEY_PATH.is_file():
        raise ValueError("Agent key path is not a regular file")

    permissions = AGENT_KEY_PATH.stat().st_mode & 0o777

    # Allow root read/write and opspulse group read only.
    # Reject group write/execute and all permissions for others.
    if permissions & 0o037:
        raise PermissionError(
            "Agent key permissions are too open. "
            "Expected 640 (root:opspulse)."
        )

    agent_key = AGENT_KEY_PATH.read_text().strip()

    if not agent_key:
        raise ValueError("Agent API key is empty")

    return agent_key
