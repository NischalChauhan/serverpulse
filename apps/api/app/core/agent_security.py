
import hashlib
import secrets
import hmac


def generate_agent_key() -> str:
    """Generate a cryptographically secure agent API key."""
    return secrets.token_urlsafe(32)


def hash_agent_key(agent_key: str) -> str:
    """Return the SHA-256 hash of an agent API key."""
    return hashlib.sha256(
        agent_key.encode("utf-8")
    ).hexdigest()


def verify_agent_key(
    agent_key: str,
    stored_hash: str,
) -> bool:
    """Verify an agent key using constant-time comparison."""
    calculated_hash = hash_agent_key(agent_key)

    return hmac.compare_digest(
        calculated_hash,
        stored_hash,
    )
