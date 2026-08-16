# Attendance without smartphones

## Recommendation

Use a shared attendance terminal at every site, backed by feature-phone IVR and a central event ledger. The design avoids dependence on personal devices while remaining resilient to local connectivity failures.

## Normal daily flow

1. The employee taps an RFID badge or uses an approved biometric terminal.
2. The terminal binds the employee ID to the site ID and original device timestamp.
3. A rotating site code adds location evidence for IVR check-ins and selected high-risk shifts.
4. Events sync into an append-only central ledger.
5. Deterministic rules flag missing punches, duplicates, impossible travel, and unusual overrides.
6. An LLM summarizes the exception queue and drafts the daily HR digest; it does not edit attendance records.
7. A supervisor and HR approver resolve exceptions with reasons preserved in the audit trail.

## Fallbacks

- **Internet outage:** the terminal encrypts and queues events locally, preserving original timestamps for later synchronization.
- **Terminal failure:** the employee calls an ordinary phone/landline IVR, enters their employee PIN and the rotating site code, and receives a confirmation number.
- **Forgotten badge:** a supervisor starts an exception call; the employee still verifies their own PIN privately.
- **Power outage:** a low-cost UPS supports the terminal; IVR remains the alternate path.
- **Missing checkout:** the system calls the employee or supervisor at a scheduled cut-off and creates an exception rather than assuming hours worked.

## Fraud controls

- Employee PIN plus rotating site code for IVR
- Optional biometric confirmation based on policy, consent, and operating environment
- Site/device signing keys and monotonic event sequence numbers
- Duplicate-punch, impossible-travel, and unusual-pattern alerts
- Supervisor override limits and second approval for payroll-impacting changes
- No shared spreadsheet or editable local register as the source of truth

## Privacy

Collect only attendance evidence required for payroll and workforce operations. Encrypt it in transit and at rest, restrict role access, redact phone numbers in logs, publish retention periods, and provide a correction process. If biometrics are used, store protected templates rather than images and complete a dedicated legal/privacy review.

## Scale

One thousand people checking in and out creates roughly 2,000 normal events per day—small for a transactional database. The hard problem is operational reliability across 100 sites, so the design prioritizes offline capture, clear exception ownership, and observable reconciliation over complex infrastructure.

## Rollout

1. Pilot five sites for two weeks; measure identity match rate, queue time, offline recovery, and correction volume.
2. Expand to 25 sites for four weeks; train supervisors and tune deterministic anomaly thresholds.
3. Roll out to all 100 sites with daily reconciliation, weekly exception review, and monthly control audits.

## Key trade-off

RFID is inexpensive and fast but easier to proxy. Biometrics provide stronger evidence but increase privacy, maintenance, and accessibility risk. The recommended hybrid uses RFID for normal flow, rotating codes and anomaly rules for additional evidence, and biometrics only where justified.
