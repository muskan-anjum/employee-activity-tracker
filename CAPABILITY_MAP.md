# Capability Map: WorkAI Enterprise UI Redesign & Production Optimization

| Module id | Responsibility | Depends on |
|---|---|---|
| `design-system-core` | Modern enterprise design system tokens (slate/zinc palette, typography scale, responsive grid, card/badge/button/table/form components, eliminating AI aesthetic tropes & bloated 5300-line CSS) | — |
| `responsive-navigation-shell` | Unified layout shell (`base_admin.html`, `base_employee.html`) with responsive sidebar, mobile hamburger drawer, backdrop overlay, topbar status, and flash alerts | `design-system-core` |
| `auth-experience` | Premium sign-in interface (`login.html`) with clean split layout, mobile fluidity, and accessible authentication controls | `design-system-core` |
| `admin-portal-ui` | Professional admin suite (`admin_dashboard.html`, `admin_employees.html`, `admin_projects.html`, `admin_activity.html`, `admin_ai_analysis.html`, `admin_reports.html`, `admin_login_sessions.html`, `admin_live.js` rich rendering) | `design-system-core`, `responsive-navigation-shell` |
| `employee-portal-ui` | Employee experience (`employee_dashboard.html`, `employee_projects.html`, `employee_activity_history.html`, `employee_work_summary.html`, `_session_history.html`) with precision timer and task workflows | `design-system-core`, `responsive-navigation-shell` |
| `production-optimization` | Database indexing (`activity_logs`, `work_sessions`), query efficiency, asset delivery optimization, and regression test validation | `admin-portal-ui`, `employee-portal-ui` |

**Build order:**
`design-system-core` → `responsive-navigation-shell`, `auth-experience` → `admin-portal-ui`, `employee-portal-ui` → `production-optimization`
