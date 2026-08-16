import time

from app.webhooks import compute_hunar_signature, verify_hunar_webhook_signature, webhook_fingerprint


def test_valid_signature():
    key = "test-secret"
    body = b'{"call_id":"call-1","event_type":"call_summary"}'
    timestamp = str(int(time.time()))
    signature = compute_hunar_signature(api_key=key, request_body=body, timestamp=timestamp)
    assert verify_hunar_webhook_signature(
        signature_header=signature,
        timestamp_header=timestamp,
        request_body=body,
        trusted_api_keys=[key],
    )


def test_rejects_stale_timestamp():
    key = "test-secret"
    body = b"{}"
    timestamp = str(int(time.time()) - 600)
    signature = compute_hunar_signature(api_key=key, request_body=body, timestamp=timestamp)
    assert not verify_hunar_webhook_signature(
        signature_header=signature,
        timestamp_header=timestamp,
        request_body=body,
        trusted_api_keys=[key],
    )


def test_rejects_modified_body():
    key = "test-secret"
    body = b'{"status":"COMPLETED"}'
    timestamp = str(int(time.time()))
    signature = compute_hunar_signature(api_key=key, request_body=body, timestamp=timestamp)
    assert not verify_hunar_webhook_signature(
        signature_header=signature,
        timestamp_header=timestamp,
        request_body=b'{"status":"FAILED"}',
        trusted_api_keys=[key],
    )


def test_webhook_fingerprint_is_stable_across_json_whitespace_and_key_order():
    first = b'{"event_type":"call_summary","call_id":"call-1","status":"COMPLETED"}'
    retried = b'{ "status": "COMPLETED", "call_id": "call-1", "event_type": "call_summary" }'
    assert webhook_fingerprint(first) == webhook_fingerprint(retried)
