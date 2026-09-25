# Spec: WorkAI Enterprise UI Redesign & Production Optimization

## Objective
Transform the WorkAI Employee Activity & Time Tracker application from its current generic "AI-generated" aesthetic (oversaturated purple gradients, emoji clutter, 5300-line fragmented CSS, broken responsive layouts, unstyled feeds) into a sleek, premium, enterprise-grade workforce intelligence SaaS platform (styled like Linear, Stripe, or Datadog). 

Ensure full responsiveness from mobile (320px) to ultra-wide displays (1440px+), fix all misaligned elements and hardcoded grid columns, modernize the dynamic feeds with rich structured components, and optimize backend query/database performance for production scale without breaking any existing business logic or test specifications.

## Assumptions
1. The app remains a hybrid Flask (Jinja2 SSR + vanilla JS) & FastAPI application. No heavy node-based SPA frameworks (React/Vue) are introduced, preserving simplicity and instant server-side loading.
2. The CSS design system is pure modern CSS with CSS variables, Flexbox, and CSS Grid, eliminating the chaotic 5300-line bloated Frankenstein CSS file while maintaining full class compatibility for existing markup.
3. Database changes must be additive (indexes on `timestamp`, `employee_id`, `session_id`) so existing SQLite installations and in-memory test databases run without data loss or breaking migrations.
4. All existing URLs, endpoints, form field names, CSRF tokens, and security contracts remain intact.

## Tech Stack
- **Backend Core:** Python 3.10+, Flask 3.x, Flask-Login, Flask-SQLAlchemy 3.x, Werkzeug
- **ASGI & Analytics API:** FastAPI, Uvicorn, Starlette, Pydantic
- **Machine Learning & Data:** Scikit-learn (Isolation Forest), NumPy
- **Frontend Core:** HTML5, Jinja2, Vanilla JavaScript (ES6+), Modern Modular CSS (CSS Custom Properties)
- **Icons & Visuals:** Inline SVG icons (Lucide / Heroicons style clean vector lines), eliminating raw emoji clutter
- **Charts:** Chart.js (CDN-backed) with dark/light neutral palette tuning

## Commands
```powershell
# Run Flask server locally
.\venv\Scripts\python.exe -m flask --app app run

# Run FastAPI analytics server
.\venv\Scripts\python.exe -m uvicorn fastapi_app:api --host 127.0.0.1 --port 8000

# Run full Python test suite
.\venv\Scripts\python.exe -B -W ignore::DeprecationWarning -m unittest discover -s tests -v

# Run browser tracker simulation tests
node --test tests/test_tracker.cjs

# Verify Python package dependencies
.\venv\Scripts\python.exe -m pip check
```

## Project Structure
```
static/
  css/
    workai.css             # Consolidated, production-grade enterprise design system
  activity_tracker.js     # Non-invasive client activity telemetry
  admin_live.js           # Real-time workforce stream with rich structured cards
  security.js             # Client CSRF and form security tokens
templates/
  base_admin.html         # Admin shell with responsive drawer, topbar, mobile nav
  base_employee.html      # Employee shell with live status pill, responsive drawer
  login.html              # Enterprise split login with responsive single-column collapse
  admin_dashboard.html    # Executive KPI cards, trend chart, structured live feed
  admin_employees.html    # Workforce directory, responsive add form, status toggles
  admin_projects.html     # Project portfolio & task assignment directory
  admin_activity.html     # Telemetry logs, filter bar, interval statistics
  admin_ai_analysis.html  # ML Isolation forest scoring & explainable attribution
  admin_reports.html      # Period reporting (daily/weekly/monthly), CSV export
  admin_login_sessions.html # Session audit table, online presence, revoke actions
  employee_dashboard.html # Precision stopwatch widget, task selector, KPI cards
  employee_projects.html  # Employee-assigned project work hours & tasks
  employee_activity_history.html # Employee session intervals & monitored ratio
  employee_work_summary.html # Daily digest, datepicker form, AI synthesis
  _session_history.html   # Reusable responsive work/break table partial
models/                   # SQLAlchemy data models with database indexing
routes/                   # Flask blueprints (auth, dashboard, assistant)
services/                 # Background business logic & ML analyzer
tests/                    # Python and Node regression tests
tasks/                    # Plan and task tracking documents
```

## Code Style & Design Tokens
```css
:root {
  /* Enterprise Slate Palette */
  --bg-app: #f8fafc;
  --bg-surface: #ffffff;
  --bg-surface-elevated: #ffffff;
  --bg-subtle: #f1f5f9;
  
  --text-primary: #0f172a;
  --text-secondary: #475569;
  --text-muted: #94a3b8;
  --text-on-accent: #ffffff;
  
  --border-subtle: #e2e8f0;
  --border-strong: #cbd5e1;
  
  /* Semantic Accent Tokens - Precision Blue / Emerald / Amber / Crimson */
  --brand-primary: #2563eb;
  --brand-primary-hover: #1d4ed8;
  --brand-primary-subtle: #eff6ff;
  
  --status-success: #10b981;
  --status-success-subtle: #ecfdf5;
  --status-warning: #f59e0b;
  --status-warning-subtle: #fffbeb;
  --status-danger: #ef4444;
  --status-danger-subtle: #fef2f2;
  
  /* Hierarchy Scales */
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 14px;
  --radius-xl: 18px;
  
  --shadow-card: 0 1px 3px 0 rgba(15, 23, 42, 0.05), 0 1px 2px -1px rgba(15, 23, 42, 0.05);
  --shadow-float: 0 10px 25px -5px rgba(15, 23, 42, 0.08), 0 8px 10px -6px rgba(15, 23, 42, 0.04);
}
```

## Testing Strategy
- **Unit & Integration:** Run Python `unittest` suite (`tests/test_requirements.py`) covering all 15 core assertions (authentication, CSRF, session invalidation, overnight work clipping, net work calculations, Isolation Forest explanations, CSV export, live data endpoints).
- **Client Telemetry:** Run Node test runner (`node --test tests/test_tracker.cjs`) to guarantee privacy boundaries, count-only payloads, break handling, and active/idle state transitions.
- **Visual & Layout Check:** Verify layout integrity across key viewport widths: 320px (iPhone SE), 375px/390px (standard mobile), 768px (tablet portrait), 1024px (tablet landscape/small laptop), 1440px+ (desktop).
- **Accessibility:** Ensure all interactive elements have semantic labels, focus outlines, minimum 44px touch targets on mobile, and readable color contrast ratios (≥ 4.5:1).

## Boundaries
- **Always:**
  - Keep all existing IDs and data attributes used by JavaScript (`timer`, `startWork`, `pauseWork`, `resumeWork`, `stopWork`, `workProject`, `workTask`, `live-projects`, `live-presence`, `live-events`, `live-status`, `trackerPulseDot`, `trackerPulseText`, `trackerLiveCounter`).
  - Preserve all Flask routing, template variables, and CSRF token mechanics.
  - Run full regression tests after each change.
- **Ask First:**
  - Changing public API contracts or route URLs.
  - Introducing heavy frontend build systems (webpack, vite, npm dependencies for frontend).
- **Never:**
  - Re-introduce bloated duplicate CSS blocks.
  - Remove existing features or bypass test assertions.
  - Break mobile responsiveness by adding hardcoded fixed-pixel widths or non-responsive inline column layouts.

## Success Criteria
1. **Clean Professional Aesthetic:** Eliminate all saturated AI neon purple glows and raw emoji headers; adopt an executive enterprise layout with crisp typography, subtle borders, and clean SVG vector icons.
2. **True Responsive Layout:** Fluid experience across mobile (<768px), tablet (768px-1023px), and desktop (1024px+). On screens under 1024px, the sidebar collapses into a mobile slide-out drawer accessible via an accessible hamburger toggle button.
3. **Alignment & Grid System:** Replace all brittle inline `grid-template-columns: 1.3fr 0.7fr;` styles with responsive layout utility classes (`layout-split`, `stats-grid`, `table-responsive`) that wrap gracefully on mobile devices.
4. **Enhanced Live Streaming:** Upgrade `admin_live.js` and `admin_dashboard.html` from raw `<p>` dot-separated text dumps to cleanly styled live cards with status badges, timestamps, progress bars, and avatars.
5. **CSS Architecture:** Replace the 5,297-line Frankenstein `workai.css` with a lean, well-organized, high-performance design system under 1,000 lines that loads instantly and eliminates conflicting `!important` tags.
6. **Production Optimization:** Add database indexes to `ActivityLog` and `WorkSession` for fast query performance, clean up template markup, and verify 100% test pass rate with zero regressions.
