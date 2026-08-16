# QA report

QA pass completed on 16 August 2026 against the assignment checklist. This report separates verified behavior from work that requires live credentials.

## Automated checks passed

- Production frontend build
- Standalone strict TypeScript check
- Frontend lint and accessibility rules
- Server-render smoke tests
- No starter/loading placeholder metadata in production HTML
- No Hunar or Apollo secret patterns in source or generated frontend files
- Python source compilation
- Ten backend tests covering demo-provider labelling, Hunar HMAC verification, timestamp replay rejection, modified-body rejection, retry-safe webhook idempotency, out-of-order lifecycle protection, partial-provider failure tracking, E.164 validation, and the complete HTTP demo workflow
- API integration coverage for health, role validation, repeated people search, duplicate prevention, shortlist updates, missing-candidate rejection, demo campaign creation, call polling, recruiter review, unsigned-webhook rejection, and canonical webhook retries
- API health and database initialization from an empty SQLite database

## Security checks passed

- `.env` is ignored; `.env.example` contains placeholders only.
- Git history does not contain the supplied Hunar live-key prefix.
- Provider credentials are referenced only in Python server configuration.
- Hunar requests are issued only by the backend adapter.
- Webhooks verify the raw request body before JSON parsing and reject timestamps outside the five-minute replay window.
- Idempotency uses canonical event JSON, so a retry with a fresh timestamp/signature cannot double-process an identical event.
- Live campaigns pre-validate every selected candidate before any outbound request. Call reservations are committed before provider requests, so partial provider failures stay tracked instead of disappearing in a rolled-back transaction.
- The deployed Hunar status request has a 10-second timeout and never caches credential-validation responses.

## User-flow checks passed

- Role title, location, and job description show readable inline validation for empty/short values and enforce maximum lengths.
- Saved role title, location, experience, and description survive refresh and feed the talent and campaign screens.
- The UI uses a real shadcn/ui Button primitive backed by Radix Slot, CVA, `clsx`, and `tailwind-merge`; `components.json` records the shadcn configuration.
- Talent title, location, experience, and keyword filters are editable, and the four-result demo has working two-page pagination.
- Talent search has a disabled/loading button and prevents double submission during the simulated request.
- Shortlist singular/plural copy is correct and the avatar stack reflects the actual selected people.
- Opening a talent result now preserves that exact candidate through candidate review and page refresh; review content no longer falls back to Ananya for every result.
- Every demo person, call, and transcript is explicitly labelled.
- Missing contact data is safe: demo candidates never expose or call a fake real number, and live mode requires an authorized E.164 number.
- Voice simulation displays the documented sequence `NOT_STARTED → INITIATED → RINGING → IN_PROGRESS → COMPLETED`.
- Campaign timers are cleared on unmount.
- Shortlist, campaign, role, selected candidate, and per-candidate recruiter review state survive refresh through device-local demo persistence.
- Hash routes restore Overview, Roles, Talent Search, Campaigns, Candidate Review, and Attendance Blueprint directly; browser back/forward updates the visible screen.
- Candidate A and B retain separate call records keyed by `candidate_id`, `request_id`, and unique `provider_call_id`; late `RINGING` events cannot regress a `COMPLETED` call.
- Campaign candidate counts, confirmation copy, lifecycle progress, and review links derive from the actual shortlist instead of two hard-coded people.
- Backend search pagination accepts `page` and `per_page` and forwards both to Apollo.
- Duplicate candidates are prevented by provider/external-ID and role/candidate uniqueness constraints.
- The API polling fallback (`GET /api/calls/{id}`) refreshes and persists status/results when callbacks are delayed.
- The built production bundle was exercised at 375 px, 768 px, and 1440 px widths. Mobile navigation opens/closes correctly and no tested page produced horizontal overflow.
- Campaign launch cancellation, launch, completion, refresh persistence, attendance tabs, and browser back/forward routing passed in the interactive browser run.
- Attendance governance, privacy, capacity, disaster-recovery, and human-accountability safeguards are visible in the deployed interface, not only in repository documentation.
- The final rebuilt bundle produced no browser console warnings or errors.
- The production URL was tested without authentication after public access was enabled: it returned HTTP 200, the correct RecruitOS metadata and interface, and no sign-in gate.
- The deployed server-only Hunar endpoint authenticated with `X-API-Key`, resolved active agent `[HunarHire] Candidate Screening` (FD35), and returned HTTP 200 without exposing the credential to the browser or repository.
- With explicit ownership and consent from the test-number owner, one live Hunar call completed on 16 August 2026 with retries disabled. Observed provider states included `RINGING`, `IN_PROGRESS`, and `COMPLETED`; duration was 106 seconds, and Hunar returned a summary plus structured answer, interest, experience, location, notice-period, compensation, and recommendation fields.
- The live-call endpoint required a 64-character one-time bearer token, validated E.164 and explicit consent, returned sanitized fields only, and was disabled after the test. Its token was removed, a new environment revision was deployed, and an unauthenticated production request then returned HTTP 404.

## Deliberately not applicable

- **Agent-management UI:** intentionally out of scope. RecruitOS selects a preconfigured active Hunar agent using `HUNAR_AGENT_ID`; it does not expose partial agent updates, persona editing, retry configuration, or guardrail editing. This avoids sending invalid partial Hunar objects.
- **Large-list virtualization:** the submission limits each people-search page to at most 100 results and the demo renders four. Server-side pagination exists; virtualization is unnecessary at this scope.
- **Transcript from live Hunar response:** Hunar's current external call schema does not document a transcript field. Live mode does not invent one.

## Requires final live authorization

- Delivery of live results through the separately deployable FastAPI webhook into the public dashboard (the authorized test used secure polling and did not persist personal answers in the public demo)
- Apollo search using a credential with People API Search access
- Production backend environment values and a public HTTPS webhook URL
- A complete Chrome plus one independent-browser matrix (the interactive pass used Chromium-based browser surfaces, not a full engine matrix)
- Lighthouse/PageSpeed against the final public URL

These remaining items must not be marked complete until actually run. One explicitly consented test call was completed; no candidate or non-consenting person was called.

## Remaining product limitations

- The public frontend is a resilient reviewer demo and does not currently fetch the separately deployable FastAPI backend. The repository contains the real backend and provider adapters, but a final production backend deployment is required for live API operation.
- Authentication and organization permissions are outside the three-day scope and must be added before handling real candidate data.
- Demo persistence uses browser storage only. Live workflow state is stored in the backend database.
