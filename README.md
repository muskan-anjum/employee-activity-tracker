# WorkAI — AI-Powered Employee Work Activity & Time Tracker

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://python.org)
[![Framework](https://img.shields.io/badge/Web%20Framework-Flask%203.1-emerald.svg)](https://palletsprojects.com/p/flask/)
[![Intelligence API](https://img.shields.io/badge/Intelligence%20API-FastAPI%20%2B%20OpenAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Machine Learning](https://img.shields.io/badge/AI%2FML-Isolation%20Forest%20%2B%20Explainable%20AI-orange.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-Enterprise%20Proprietary-indigo.svg)]()

> **WorkAI** is an executive-grade workforce intelligence and productivity platform. Built with a dual-tier architecture (Flask web portal + FastAPI intelligence layer), WorkAI delivers real-time time tracking, granular project and task attribution, automated break analytics, and explainable Machine Learning anomaly detection while upholding strict zero-keystroke privacy standards.

---

## 📑 Table of Contents

- [Executive Summary & Key Features](#-executive-summary--key-features)
- [System Architecture](#-system-architecture)
- [Compliance with `task.md`](#-compliance-with-taskmd)
- [Explainable AI & Machine Learning Engine](#-explainable-ai--machine-learning-engine)
- [Privacy-First Telemetry Architecture](#-privacy-first-telemetry-architecture)
- [Quick Start Guide](#-quick-start-guide)
- [Default Demo Credentials](#-default-demo-credentials)
- [Interactive API Documentation (Swagger / OpenAPI)](#-interactive-api-documentation-swagger--openapi)
- [Client & Mentor Presentation Walkthrough Script](#-client--mentor-presentation-walkthrough-script)
- [Automated Verification & Test Suite](#-automated-verification--test-suite)

---

## 🌟 Executive Summary & Key Features

WorkAI bridges the gap between workforce productivity management and employee trust through transparent, privacy-first telemetry and explainable machine learning:

1. **Role-Based Authentication & Session Auditing**: Dedicated portals for Employees and Administrators, tracking active presence, login/logout timestamps, and automatic session revocation upon account deactivation.
2. **Precision Work & Break Tracking**: Real-time digital session timers, pause/resume break lifecycle controls, and mathematical subtraction of idle break times from total logged hours.
3. **Granular Project & Task Attribution**: Employees select active projects and assigned tasks; starting work automatically transitions task status to "In Progress".
4. **Explainable AI Anomaly Detection**: `IsolationForest` unsupervised machine learning analyzes normalized multi-dimensional telemetry (active/idle ratios, event frequency per active second, keyboard-to-mouse distributions) accompanied by human-readable justification reasons for every flagged interval.
5. **Automated AI Work Summaries**: Daily, weekly, and period-based productivity digests synthesizing task velocity, monitored active ratios, and milestone updates.
6. **Executive Admin Console**: Live workforce presence stream, 7-day productivity velocity graphs, and a natural-language WorkAI Assistant chatbot.
7. **Multi-Period Analytics & CSV Export**: Dynamic daily, weekly, and monthly productivity summaries with rich multi-column CSV reporting.

---

## 🏗️ System Architecture

WorkAI employs a unified dual-engine architecture:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        WORKAI CLIENT INTERFACE                         │
│  - Vanilla CSS Glassmorphism Design System (Inter Font, Dark Accents)  │
│  - Background Activity Telemetry Engine (Zero Raw Keystroke Logging)   │
│  - Live Session Timer & Break Status Synchronization                   │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                 ┌─────────────────┴─────────────────┐
                 │                                   │
                 ▼                                   ▼
┌─────────────────────────────────┐ ┌────────────────────────────────────┐
│      FLASK ENTERPRISE APP       │ │       FASTAPI REST ENGINE          │
│   (Web Portal & Controllers)    │ │    (Intelligence Layer & API)      │
├─────────────────────────────────┤ ├────────────────────────────────────┤
│ • Auth & Role Access Control    │ │ • `/health` & Platform Status      │
│ • Employee Work & Break State   │ │ • `/docs` Interactive OpenAPI UI   │
│ • Admin Intelligence Dashboards │ │ • `/api/workforce/overview`        │
│ • Natural Language Assistant    │ │ • `/api/ml/analyze` Live Scoring   │
│ • Period Aggregation & CSV      │ │ • `/api/projects/overview`         │
└────────────────┬────────────────┘ └─────────────────┬──────────────────┘
                 │                                    │
                 └─────────────────┬──────────────────┘
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                 SHARED SERVICE & INTELLIGENCE LAYER                    │
│ • services/ml_analyzer.py   (Isolation Forest + Explainable AI)        │
│ • services/work_summary.py  (Net Work Seconds & Period Aggregation)    │
│ • services/activity_tracker.py (Heartbeat Persistence & Auto-Scoring)  │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      SQLITE PERSISTENCE LAYER                          │
│ • users (Roles, Passwords, Active Account Toggles)                     │
│ • projects & tasks (Lifecycle, Progress %, Assignments)                │
│ • work_sessions & breaks (Cascading Duration Attribution)              │
│ • activity_logs (Intervals, Anomaly Scores, Attribution Reasons)       │
│ • login_sessions (Audit Trails, Online Presence)                       │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 Compliance with `task.md`

| # | Requirement from `task.md` | Implementation Status | Core Technical Component |
|---|----------------------------|-----------------------|--------------------------|
| **1** | **Employee Authentication** | ✅ 100% Complete | `routes/auth.py`, `models/user.py`, `models/login_session.py`, quick-fill credentials helper on `/login`. |
| **2** | **Automatic Time Tracking** | ✅ 100% Complete | `routes/dashboard.py` (`start_work`, `take_break`, `end_break`, `end_work`), `services/work_summary.py`. |
| **3** | **Activity Monitoring** | ✅ 100% Complete | `static/activity_tracker.js` heartbeat engine embedded globally across all employee pages; records counts only. |
| **4** | **Project-Wise Time Tracking** | ✅ 100% Complete | `models/work_session.py` (`project_id`, `task_id`), `/employee/projects`, `/admin/projects`. |
| **5** | **AI-Based Activity Analysis** | ✅ 100% Complete | `services/ml_analyzer.py` Isolation Forest model with 9 engineered features and human-readable explanation generator. |
| **6** | **AI Work Summary** | ✅ 100% Complete | `services/work_summary.py` (`generate_work_summary`), `/employee/work-summary`. |
| **7** | **Admin Dashboard** | ✅ 100% Complete | `/admin/dashboard`, Chart.js 7-day trend graph, live stream, and WorkAI Assistant natural-language chat. |
| **8** | **Reports & Analytics** | ✅ 100% Complete | `/admin/reports` with daily, weekly, and monthly period filters + CSV download via `/admin/reports/export`. |
| **9** | **Activity History** | ✅ 100% Complete | `/employee/activity-history` and `/admin/activity` with real-time search and status filters. |
| **10** | **Employee Management** | ✅ 100% Complete | `/admin/employees` (create employee, deactivate account, revoke session, reset password) and `/admin/projects`. |

---

## 🧠 Explainable AI & Machine Learning Engine

WorkAI rejects "black box" statistical claims. Its machine learning pipeline combines scikit-learn's **Isolation Forest** with an **Explainable Attribution Classifier**:

### Feature Engineering
For every activity interval (active time, idle time, keystroke count, mouse interaction count), the engine calculates:
- $\text{Active Ratio} = \frac{\text{Active Seconds}}{\text{Active Seconds} + \text{Idle Seconds}}$
- $\text{Idle Ratio} = \frac{\text{Idle Seconds}}{\text{Active Seconds} + \text{Idle Seconds}}$
- $\text{Interaction Density} = \frac{\text{Keyboard Events} + \text{Mouse Events}}{\text{Active Seconds} + 1.0}$
- $\text{Input Modality Ratio} = \frac{\text{Keyboard Events}}{\text{Mouse Events} + 1.0}$

### Explainability Matrix
When an interval is identified as a statistical outlier, the engine generates an explicit attribution rationale:
- *Extended idle duration with zero recorded input events.*
- *Active window reported without corresponding keyboard or mouse inputs.*
- *Unusually high input frequency (>18 events/sec), potential macro or automated tool.*
- *Single-mode interaction: unusually high keystroke volume with zero mouse engagement.*
- *High click/scroll frequency with complete absence of keyboard interaction.*

---

## 🔒 Privacy-First Telemetry Architecture

Unlike intrusive surveillance tools, WorkAI adheres strictly to enterprise privacy regulations (GDPR / CCPA compliant architecture):
- **NO Raw Keystrokes Logged**: The tracker only counts keypress down events; characters and text typed are discarded in the browser memory.
- **NO Screen Captures or Video Recording**: Employee privacy is preserved at all times.
- **NO Clipboard Access**: Clipboard text or passwords are never read or transmitted.
- **Transparent Indicator**: A persistent pulsing indicator badge (`● Live Monitoring Active`) informs employees that monitoring is active.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ (Tested up to Python 3.14)
- Git

### 2. Environment Setup

```bash
# Clone the repository
git clone https://github.com/muskan-anjum/employee-activity-tracker.git
cd employee-activity-tracker

# Create and activate virtual environment
python -m venv venv

# Windows:
.\venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Initialization & Seeding

```bash
# Seed initial admin and employee accounts
python seed_users.py
```

### 4. Running the Platform

#### Option A: Unified Full Stack (Flask Web App + FastAPI Docs)
```bash
python -m uvicorn fastapi_app:app --host 127.0.0.1 --port 8000 --reload
```
- **Web Application Portal:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **FastAPI OpenAPI / Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative ReDoc Docs:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

#### Option B: Standalone Flask Dev Server
```bash
python app.py
```
- Available at [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🔑 Default Demo Credentials

The login page includes instant one-click **"⚡ Quick Demo Credentials"** buttons for effortless client presentations:

| Role | Email | Password | Access Scope |
|------|-------|----------|--------------|
| **Administrator** | `admin@workai.com` | `Admin@123` | Full Admin Console, AI Analysis, Reports, Projects, Employees |
| **Employee** | `employee@workai.com` | `Employee@123` | Personal Dashboard, Timer, Project Selection, Work Summaries |

---

## 📖 Interactive API Documentation (Swagger / OpenAPI)

FastAPI provides an interactive API playground at `/docs`:

- `GET /health`: Platform health check and ML engine status.
- `GET /api/workforce/overview`: Aggregated workforce presence, total hours, and completion rates.
- `POST /api/ml/analyze`: Real-time Isolation Forest scoring for incoming telemetry intervals.
- `GET /api/projects/overview`: Project-level health, task progress, and activity scores.
- `GET /api/employees/overview`: Per-employee performance metrics.

---

## 🎤 Client & Mentor Presentation Walkthrough Script

When presenting WorkAI to company mentors or executive clients, follow this structured demo script:

### Step 1: Login & Privacy Architecture (`/login`)
- **Showcase:** Point out the dark glassmorphism login portal. Click **"👔 Admin Account"** to demonstrate the instant demo autofill.
- **Talking Point:** *"WorkAI is designed for modern enterprise workflows with a focus on trust. Notice our privacy banner: WorkAI logs interaction counts only and never logs raw keystrokes, clipboard, or screenshots."*

### Step 2: Employee Real-Time Workspace (`/employee/dashboard`)
- **Action:** Log in as `employee@workai.com`.
- **Showcase:**
  1. Show the dynamic project and task selector dropdowns.
  2. Click **"Start Work Session"**: The digital clock begins ticking (`00:00:01`), and the assigned task automatically switches from *Pending* to *In Progress*.
  3. Notice the top-right green pulsing badge: `● Live Monitoring Active`.
  4. Click **"Take Break"**: The timer pauses, status switches to `On Break`, and break seconds are counted separately so employees are never penalized for resting.
  5. Click **"Resume Work"** then **"End Work Session"**: The calculation engine automatically subtracts the break duration from the total logged time.

### Step 3: Executive Admin Dashboard (`/admin/dashboard`)
- **Action:** Switch to `admin@workai.com`.
- **Showcase:**
  1. **KPI Cards:** Live count of employees currently working vs on break.
  2. **Productivity Velocity:** Interactive Chart.js graph tracking 7-day company-wide activity.
  3. **WorkAI Assistant:** Scroll down to the assistant widget and type: *"Who worked the most hours?"* or *"Are there any anomalies?"* — the chatbot instantly responds with real database insights.

### Step 4: Explainable AI Anomaly Detection (`/admin/ai-analysis`)
- **Showcase:** Explain that instead of opaque numbers, WorkAI presents the **Isolation Forest score** alongside an **Attribution Reason** (e.g., *"Extended idle duration with zero recorded input events"* or *"Potential macro automation"*).
- **Talking Point:** *"Managers don't need black-box algorithms. WorkAI provides explainable AI so administrators understand exactly why an activity pattern was flagged."*

### Step 5: Reports, Multi-Period Analytics & CSV Export (`/admin/reports`)
- **Showcase:** Click between **"Daily"**, **"Weekly"**, and **"Monthly"** filters to demonstrate multi-period historical aggregation.
- **Action:** Click **"Download CSV Export"** — download the clean, executive-ready report featuring employee names, period, net work time, break time, and productivity percentages.

### Step 6: FastAPI OpenAPI Documentation (`/docs`)
- **Showcase:** Click the **"⚡ FastAPI OpenAPI Docs"** link in the sidebar to open Swagger UI.
- **Talking Point:** *"In addition to our web interface, WorkAI provides an enterprise REST API powered by FastAPI, enabling seamless integration with enterprise HRMS systems, Slack bots, and automated payroll pipelines."*

---

## 🧪 Automated Verification & Test Suite

The codebase includes an end-to-end automated verification script covering all database models, calculation engines, ML services, Flask routes, and FastAPI endpoints.

Run the test suite anytime with:

```bash
python scratch/test_e2e_verification.py
```

### Verified Test Assertions:
```text
============================================================
🚀 STARTING E2E VERIFICATION OF WORKAI PLATFORM
============================================================
✓ Users verified: Admin (admin@workai.com), Employee (employee@workai.com)
✓ Database schema verified: work_sessions.task_id and activity_logs.anomaly_reason present
✓ Work summary calculation verified: 2h session with 30m break = 5400 net work seconds, 1800 break seconds
✓ Normal telemetry evaluated: is_anomaly=False, score=0.15
✓ Anomaly correctly flagged: score=-0.25, reason='Extended idle duration with zero recorded input events.'
✓ Employee login successful and redirected to dashboard
✓ All 4 Employee console views verified (200 OK)
✓ Admin login successful
✓ All 7 Admin console views verified (200 OK)
✓ Multi-period reports (daily, weekly, monthly) and rich CSV export verified
✓ WorkAI Assistant chat verified: response received ('I am the WorkAI Insights Assistant. You ...')
✓ FastAPI /health verified (200 OK)
✓ FastAPI /api/workforce/overview verified: workforce_status=Stable Productivity, employees={'total': 5, 'active_accounts': 5, 'currently_working': 1}
✓ FastAPI /api/ml/analyze verified: status=Normal, score=0.15
============================================================
🎉 ALL 10 REQUIREMENTS & ARCHITECTURE TESTS PASSED SUCCESSFULLY!
============================================================
```

---

## 👥 Contributors & Acknowledgements

- **Developed for:** Enterprise Client Demonstration & Academic Evaluation.
- **Architecture & Machine Learning:** WorkAI Engineering Team.
