# Assignment review

Both assignment files were inspected. The root `task.md` expands the same ten
features listed in `templates/task.md`. The existing project already implemented
parts of every feature; the changes below close concrete functional gaps.

| Requirement | Implementation and corrections |
| --- | --- |
| 1. Employee authentication | Hashed passwords, role checks returning 403, audited browser sessions, CSRF-protected mutations and logout. Every request checks account and login revocation. Password reset and deactivation revoke all logins. Analytics API requires an active administrator. |
| 2. Automatic time tracking | Start/pause/resume/end workflow; timer now starts from server-calculated net work and excludes completed and current breaks. Deactivation preserves net time. |
| 3. Activity monitoring | Count-only keyboard/mouse signals, 60-second inactivity threshold, 30-second uploads. Tracking follows the server's work state, suppresses breaks, validates payloads and session identity, and coordinates same-browser tabs where supported. |
| 4. Project/task time | Only assigned active projects and owned tasks can be tracked; mismatched project/task requests are rejected. Project and individual task totals include ongoing sessions. |
| 5. ML analysis | Existing Isolation Forest and explanation rules retained. Ingestion now persists model results over recent employee samples, with cold-start heuristics for small samples. |
| 6. Work summaries | Daily/historical date selection, net work, breaks, active ratios, task progress and immutable task-update milestones. Cross-midnight sessions are included and clipped. |
| 7. Admin dashboard | Ten-second refresh of current work states, heartbeat-based presence, project task progress and latest interaction intervals. Weekly chart uses the whole week rather than the latest 100 records. Local assistant answers workforce, project and anomaly questions. |
| 8. Reports/analytics | UTC daily and trailing 7/30-day views and CSV export; overnight work/break calculations agree. CSV text is protected from common spreadsheet-formula prefixes. |
| 9. Activity history | Employee-owned sessions/breaks plus telemetry; administrator can filter by employee. Interaction history is no longer truncated to 50 records. |
| 10. Employee management | Employee creation, password reset, account toggles, projects, statuses and task assignment. Invalid/inactive assignment targets are rejected, task statuses are validated, and progress updates leave milestone snapshots. |

## Verification coverage

`tests/test_requirements.py` covers real Flask routes, rendered pages, ASGI analytics
authentication, work/break lifecycle, cross-role and cross-employee access, CSRF,
session revocation, presence expiry, input validation, overnight time, CSV formula
escaping, historical milestones and the actual Isolation Forest branch.
`tests/test_tracker.cjs` covers the client activity/idle accounting, break suppression
and switching work sessions without attributing old counts to the new session.
Tests do not seed, delete or alter the user's existing database.

## Deliberate scope

This is a browser-based assignment implementation. It does not observe operating
system activity. Work summaries and the natural-language assistant use local rules;
the anomaly analyzer is the machine-learning component. Client telemetry is not a
tamper-proof record. Network/browser suspension may leave gaps. No deployment or
visual browser acceptance test is implied by the automated test results. See
`README.md` for startup instructions, date semantics and operational limitations.
