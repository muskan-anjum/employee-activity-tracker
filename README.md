# WorkAI — Employee Activity & Time Tracker

Flask employee/admin portal with SQLite persistence, browser interaction counts,
project/task time tracking, Isolation Forest analysis, and an optional FastAPI
analytics service. Requirements are in `task.md` and `templates/task.md`.
See [the requirement review](REQUIREMENTS_REVIEW.md) for implementation details.

## Run locally on Windows

The existing `venv` can be used directly without activation:

```powershell
.\venv\Scripts\python.exe seed_users.py
.\venv\Scripts\python.exe -m flask --app app run
```

Open http://127.0.0.1:5000/login. On a fresh checkout, create the environment first:

```powershell
py -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

`seed_users.py` creates missing demo accounts and does not reset existing passwords:

| Role | Email | Demo password |
| --- | --- | --- |
| Administrator | admin@workai.com | Admin@123 |
| Employee | employee@workai.com | Employee@123 |

These accounts are for a local demonstration. Use private credentials for a deployment.
Set `SECRET_KEY` to a long random secret shared across server workers. Without it,
development starts with a random key and existing browser logins expire on restart.
Set `COOKIE_SECURE=1` when serving through HTTPS. `DATABASE_URL` defaults to
`sqlite:///employee_tracker.db`, stored under `instance/`.

Tables are created at startup. Existing SQLite installations receive additive
migrations for task attribution, anomaly reasons and login heartbeat timestamps;
the new `task_updates` table retains task milestones. Existing records are preserved.

## Demonstrate the assignment

1. Log in as administrator. Add employees, create an active project, and assign tasks.
2. Log in as an employee in a different browser/private window. Choose an assigned
   project/task and start work. The task moves from Pending to In Progress.
3. Use the app for at least 30 seconds. Pause, resume, and end work. The timer and
   recorded net work exclude breaks, including an unfinished break at end-work.
4. Update task progress. View per-project and per-task net time in My Projects.
5. View work sessions, break intervals and count-only telemetry in Activity History.
   Choose a date in Work Summary to inspect historical time and task milestones.
6. View live workforce work states, heartbeat presence, task progress and interaction
   intervals on the admin dashboard. The feed refreshes every ten seconds.
7. Inspect AI Analysis and employee-filtered Activity History. Try assistant prompts:
   “Who is working?”, “Show unusual activity”, and “Which project has the most tracked time?”
8. Choose daily, weekly or monthly Reports and export CSV. Daily means UTC today;
   weekly/monthly mean the trailing 7/30 days. Overnight work and breaks are clipped
   to the selected period. Task completion columns show current assignment status.
9. Deactivate an employee or reset their password. All their browser logins are
   revoked and open work/break intervals are closed with net time preserved.

## Optional analytics API

```powershell
.\venv\Scripts\python.exe -m uvicorn fastapi_app:api --host 127.0.0.1 --port 8000
```

The employee portal is also available at http://127.0.0.1:8000/login, and interactive
API documentation at http://127.0.0.1:8000/docs. Use the documentation's Authorize
button with an active administrator email and password (HTTP Basic authentication).
All analytics endpoints require administrator authentication; `/health` is public.
Serve the API over HTTPS outside localhost. Use the same configured database and
`SECRET_KEY` if running Flask and FastAPI in separate processes.

## Verification

```powershell
.\venv\Scripts\python.exe -B -W ignore::DeprecationWarning -m unittest discover -s tests -v
node --test tests/test_tracker.cjs
.\venv\Scripts\python.exe -m pip check
```

The Python tests create an isolated in-memory SQLite database and exercise real
routes, authorization, CSRF protection, account revocation, time calculations,
historical reports, CSV export, milestones, page rendering and the ASGI API.
Node tests execute the tracker in a simulated browser environment, checking
count-only payloads, active/idle transitions, breaks and session changes. They
are not a visual browser test. The old `scratch/test_e2e_verification.py` uses
the live demo database and is not the supported regression suite.

## Monitoring and AI scope

- Interaction monitoring runs only within this application's browser pages. It
  records event counts and active/idle seconds, never key characters, coordinates,
  clipboard content, screenshots or activity in other desktop applications.
- Work sessions are explicitly started/stopped. Work time continues until ended,
  even if the browser closes; presence expires after 90 seconds without a heartbeat.
  Idle time is separate from breaks and remains part of elapsed net work time.
- Telemetry is sent about every 30 seconds. Background tab throttling, browser
  suspension or network failure can leave gaps. Uncertain writes are not retried
  automatically, to avoid counting the same interval twice.
- Browsers with Web Locks coordinate one tracker per origin across tabs, with
  count-only cross-tab interaction messages. Without Web Locks, use a single tab.
  Separate devices are not coordinated.
- Isolation Forest uses up to 100 recent employee intervals for stored scoring.
  Fewer than five records use explicitly defined cold-start heuristics. Admin
  analysis views may score a different workforce sample. Explanations are rule
  descriptions of unusual patterns, not proof of misconduct or a causal model.
- Summaries and the workforce assistant are local, rule-based text generation;
  no external LLM or API key is required. Milestones are retained from this update
  onward; past task changes cannot be reconstructed from older databases.
- Dates are displayed and filtered in UTC. The chart dependency is served from
  a CDN, so charts require internet access; core workflows use the local server.
