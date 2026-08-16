# Verified API contracts

Verified against the public documentation on 13 August 2026. This file records only fields and behavior that the providers document; it is the boundary for the live adapters.

## Hunar Voice Agents

Documentation: <https://api.voice.hunar.ai/docs/external/>

### Authentication and base URL

- Production base: `https://api.voice.hunar.ai/external/v1/`
- Authentication header: `X-API-Key: <server-side key>`
- JSON requests use `Content-Type: application/json`

### Supported resources used here

- `GET /agents/`
- `GET /agents/{agent_id}/`
- `POST /agents/`
- `PUT /agents/{agent_id}/`
- `POST /calls/`
- `POST /calls/bulk/`
- `GET /calls/`
- `GET /calls/{call_id}/`
- `GET /numbers/`

### Single-call request

Required fields are `agent_id`, `callee_name`, and E.164 `mobile_number`. `custom_data` must contain every custom variable required by the chosen agent. The application uses a unique `request_id`, complete `retry_config`, `timezone`, and per-event callback URLs.

`callback_config` supports:

- `call_status_callback_url`
- `call_recording_callback_url`
- `call_result_callback_url`
- `call_summary_callback_url`

Successful resource creation returns HTTP 200, not 201.

### Status and results

Documented call states include `NOT_STARTED`, `SCHEDULED`, `INITIATED`, `RINGING`, `IN_PROGRESS`, `COMPLETED`, `NOT_CONNECTED`, `CANCELLED`, and `FAILED`.

Call detail may include duration, engagement, answering party, recording URL, structured `result`, retries, timestamps, and raw custom/system data. The current external documentation does **not** document a transcript field. RecruitOS does not fabricate one for live calls.

### Webhooks

Hunar documents four event types:

- `call_status_updated`
- `call_recording_done`
- `call_result_done`
- `call_summary`

Every event contains `event_type`, `call_id`, `agent_id`, and `request_id`. `call_summary` combines terminal status, recording, and structured result information.

Signature validation:

1. Read the raw JSON body bytes.
2. Require `X-Hunar-Timestamp` within a five-minute window.
3. Compute HMAC-SHA256 over `{timestamp}.` followed by the raw body bytes using the Hunar API key.
4. Base64-encode the digest.
5. Compare in constant time with every comma-separated segment in `X-Hunar-Signature`.
6. Accept if any supplied signature matches any trusted active key.

The webhook handler stores a unique fingerprint because Hunar explicitly documents retries and duplicate delivery.

### Errors

- 400 telephony or business validation error
- 401 missing/invalid API key
- 402 expired subscription or exhausted calling minutes
- 404 resource not found
- 422 request validation failure
- 500 server error

## Apollo People API Search

Official reference: <https://docs.apollo.io/reference/people-api-search>

- Endpoint: `POST https://api.apollo.io/api/v1/mixed_people/api_search`
- Authentication: `x-api-key` header
- Filters used: `person_titles[]`, `person_locations[]`, `q_keywords`, `include_similar_titles`, `page`, and `per_page`
- Maximum documented page size: 100; maximum display window: 50,000 records
- Search returns net-new prospects but explicitly does not return email addresses or phone numbers. Those require separate enrichment endpoints.
- Common responses documented for the endpoint: 200, 401, 403, 422, and 429.

RecruitOS normalizes the search payload while retaining the original provider response for controlled debugging. It does not claim contactability until enrichment or an authorized manually supplied number exists.
