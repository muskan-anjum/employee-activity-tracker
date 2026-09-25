# Task List: WorkAI Enterprise UI Redesign & Production Optimization

- [x] Task 1: Enterprise Design System Core (`design-system-core`)
  - Acceptance: `static/css/workai.css` rewritten into a sleek, production-grade design system under 1,000 lines. Uses CSS variables, Inter typography, clean slate/neutral palette, responsive grid utilities (`.layout-split`, `.layout-two-thirds`, `.stats-grid`), button & card components, table styles, form controls, and mobile navigation drawer styles. All 4,300+ lines of duplicate override junk removed.
  - Verify: Check file size and syntax, ensure clean rendering without console errors.
  - Files: `static/css/workai.css`

- [x] Task 2: Responsive Navigation Shells & Sign-In Page (`responsive-navigation-shell` & `auth-experience`)
  - Acceptance: `templates/base_admin.html` and `templates/base_employee.html` updated with accessible mobile hamburger menu, slide-out sidebar drawer with overlay, refined top bar with user profile, live heartbeat status pill, and flash message alerts. `templates/login.html` redesigned with clean enterprise split layout, accessible inputs, demo pills, and smooth mobile single-column stacking.
  - Verify: Run test suite to verify CSRF tokens and page renders; test mobile layout down to 320px.
  - Files: `templates/base_admin.html`, `templates/base_employee.html`, `templates/login.html`

- [x] Task 3: Admin Portal UI Redesign & Rich Live Stream (`admin-portal-ui`)
  - Acceptance: All 7 admin templates (`admin_dashboard.html`, `admin_employees.html`, `admin_projects.html`, `admin_activity.html`, `admin_ai_analysis.html`, `admin_reports.html`, `admin_login_sessions.html`) upgraded to enterprise layout. Hardcoded inline `grid-template-columns` replaced with responsive CSS classes. Raw emojis replaced with crisp vector SVG icons. `static/admin_live.js` upgraded to render structured employee presence cards (online dot, avatar, project, duration), task progress bars, and event badges instead of unstyled `<p>` dot dumps.
  - Verify: `.\venv\Scripts\python.exe -B -m unittest discover -s tests -v`
  - Files: `templates/admin_*.html`, `static/admin_live.js`

- [x] Task 4: Employee Portal UI Redesign (`employee-portal-ui`)
  - Acceptance: All 5 employee templates (`employee_dashboard.html`, `employee_projects.html`, `employee_activity_history.html`, `employee_work_summary.html`, `_session_history.html`) modernized. Precision stopwatch display with crisp monospaced digital layout, responsive project/task dropdowns, cohesive action buttons (Start, Pause, Resume, Stop), datepicker form styling in work summary, and AI summary cards.
  - Verify: `.\venv\Scripts\python.exe -B -m unittest discover -s tests -v` and `node --test tests/test_tracker.cjs`
  - Files: `templates/employee_*.html`, `templates/_session_history.html`

- [x] Task 5: Production Optimization, DB Indexes & Final Verification (`production-optimization`)
  - Acceptance: Add `index=True` to `ActivityLog.timestamp`, `ActivityLog.employee_id`, `ActivityLog.session_id`, and `WorkSession.employee_id`. Verify query efficiency. Ensure all 15 Python unit tests and 3 Node tracker tests pass cleanly. Confirm responsive layout across 320px, 375px, 768px, 1024px, and 1440px+.
  - Verify: `.\venv\Scripts\python.exe -B -W ignore::DeprecationWarning -m unittest discover -s tests -v`, `node --test tests/test_tracker.cjs`, `.\venv\Scripts\python.exe -m pip check`
  - Files: `models/activity.py`, `models/work_session.py`, `routes/dashboard.py`
