import base64
import hashlib
import hmac
import json
import time
from collections.abc import Iterable


def compute_hunar_signature(*, api_key: str, request_body: bytes, timestamp: str) -> str:
    message = f"{timestamp.strip()}.".encode("utf-8") + request_body
    digest = hmac.new(api_key.encode("utf-8"), message, hashlib.sha256).digest()
    return base64.b64encode(digest).decode("ascii")


def verify_hunar_webhook_signature(
    *, signature_header: str | None, timestamp_header: str | None,
    request_body: bytes, trusted_api_keys: Iterable[str], tolerance_seconds: int = 300,
) -> bool:
    if not signature_header or not timestamp_header:
        return False
    try:
        timestamp_value = int(timestamp_header.strip())
    except ValueError:
        return False
    if abs(int(time.time()) - timestamp_value) > tolerance_seconds:
        return False
    signatures = [part.strip() for part in signature_header.split(",") if part.strip()]
    for api_key in trusted_api_keys:
        expected = compute_hunar_signature(
            api_key=api_key, request_body=request_body, timestamp=timestamp_header
        )
        if any(hmac.compare_digest(candidate, expected) for candidate in signatures):
            return True
    return False


def webhook_fingerprint(payload: bytes) -> str:
    """Build an idempotency key that is stable across webhook retry signatures.

    Hunar may retry the same JSON event with a new timestamp and signature. The
    signature therefore cannot be part of the key. Canonical JSON also makes
    semantically identical payloads stable across whitespace differences.
    """
    parsed = json.loads(payload.decode("utf-8"))
    canonical = json.dumps(parsed, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()
