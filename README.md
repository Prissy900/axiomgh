# AxiomGH — CISD 2026 Compliance Intelligence Platform

> **Ghana's first purpose-built compliance assessment platform for the Bank of Ghana Cyber and Information Security Directive (CISD) 2026.**

Built by **Priscilla Kporha** — MSc Computer Science Candidate, Ghana Communication Technology University (GCTU).  
Thesis: *Designing and Evaluating a Hybrid Zero Trust Architecture Access Control Model for Enterprise Cloud Systems.*

---

## What is AxiomGH?

AxiomGH guides BoG-regulated financial institutions through the full CISD 2026 compliance assessment process — covering all 23 directive sections, scoring institutions out of 1000, and generating board-ready PDF gap reports.

Every bank, fintech, payment processor, microfinance institution, savings & loans company, credit bureau, and foreign exchange bureau regulated by the Bank of Ghana must comply with CISD 2026. AxiomGH is the tool that makes that process structured, measurable, and auditable.

---

## Key Features

| Feature | Description |
|---|---|
| **23 Sections** | Full coverage of all CISD 2026 directive parts including 3 new 2026 additions |
| **172 Questions** | Yes / Partial / No / N/A responses with optional evidence notes per question |
| **Weighted Scoring** | Compliance score out of 1000 with section-level breakdowns |
| **Gap Report** | Prioritised gap list sorted by risk severity (Critical → High → Medium) |
| **PDF Export** | Board-ready compliance report downloadable as PDF |
| **Benchmarking** | Anonymised peer comparison across institution types |
| **Multi-Institution** | One platform, multiple institutions — each with their own login |
| **Auto-Save** | Answers save automatically as you go — resume any time |

---

## CISD 2026 Coverage

### Original 20 Sections (inherited from CISD 2018, updated)
Board Governance · Senior Management · Internal Audit · CISO · Risk Policy · Risk Assessment · Asset Management · Cyber Defence · Cyber Response & SIEM/SOC · Employee Access · Electronic Banking · Training & Awareness · External Connections · Cloud Services · International Affiliation · Physical Security · HR Management · Contractual Requirements · ISMS/ISO 27001 · Business Continuity

### New CISD 2026 Sections
- **Section 21 — Digital Innovations** (AI governance, blockchain risk, virtual assets)
- **Section 22 — Data Centre Operations** (13 sub-sections including data sovereignty requirement)
- **Section 23 — API Security** (OWASP API Top 10, API gateway, inventory)

---

## Tech Stack

**Backend**
- Python 3.14 / Django 6.0
- Django REST Framework
- SimpleJWT Authentication
- PostgreSQL
- ReportLab (PDF generation)

**Frontend**
- React 18
- Vite
- Axios
- React Router v6

**Infrastructure**
- AWS (EC2, S3, IAM) — deployment target
- PostgreSQL 18

---

## Architecture

```
axiomgh/
├── axiomgh/          # Django project settings & URLs
├── core/
│   ├── models.py     # 12 models: Institution, User, Assessment, Response, etc.
│   ├── scoring.py    # Weighted scoring engine
│   ├── serializers.py
│   ├── views.py      # API ViewSets with custom actions
│   ├── urls.py       # API routing
│   ├── authentication.py  # Email-based JWT auth
│   └── reports.py    # PDF report generation
├── axiomgh_frontend/
│   └── src/
│       └── App.jsx   # Full React SPA — all pages and components
├── seed_data.py      # Database seeder — loads all 23 sections & 172 questions
└── onboard_client.py # Client onboarding CLI tool
```

---

## API Endpoints

```
POST   /api/v1/auth/token/                          Login
GET    /api/v1/assessments/                         List assessments
POST   /api/v1/assessments/                         Create assessment
GET    /api/v1/assessments/{id}/responses/          Get all questions grouped by section
POST   /api/v1/responses/bulk_save/                 Save answers
POST   /api/v1/assessments/{id}/complete/           Complete & score assessment
GET    /api/v1/assessments/{id}/scores/             Section scores
GET    /api/v1/assessments/{id}/gaps/               Prioritised gap list
GET    /api/v1/assessments/{id}/pdf_report/         Download PDF report
GET    /api/v1/benchmarks/?type={institution_type}  Peer benchmarks
```

---

## Local Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL

### Backend

```bash
# Clone and set up
git clone https://github.com/Prissy900/axiomgh.git
cd axiomgh

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers psycopg2-binary reportlab

# Configure database
# Edit axiomgh/settings.py — set your PostgreSQL password

# Run migrations
python manage.py migrate

# Seed directive sections and questions
python seed_data.py

# Create admin user
python manage.py createsuperuser

# Start server
python manage.py runserver
```

### Frontend

```bash
cd axiomgh_frontend
npm install
npm run dev
```

Open `http://localhost:3000`

### Onboard a Client

```bash
python onboard_client.py
```

---

## Scoring Methodology

| Answer | Points Awarded |
|---|---|
| Yes | Full points |
| Partial | 50% of points |
| No | 0 points |
| N/A | Excluded from scoring |

Each section carries a risk-weighted percentage of the total 1000-point score. Sections covering Board Governance, CISO, and Cyber Defence carry higher weights given their criticality under CISD 2026.

**Compliance Ratings:**
- ✅ **Compliant** — 80% and above
- ⚠️ **Partial** — 60–79%
- 🔶 **At Risk** — 40–59%
- ❌ **Non-Compliant** — below 40%

---

## Regulatory Context

The Bank of Ghana launched CISD 2026 in March 2026, replacing the 2018 directive. It applies to:

- Commercial Banks
- Specialised Deposit-Taking Institutions (SDIs)
- Financial Holding Companies
- Development Finance Institutions
- Non-Deposit-Taking Microfinance Institutions
- Payment Service Providers (PSPs)
- Dedicated Electronic Money Issuers
- Credit Reference Bureaux
- Foreign Exchange Bureaux

AxiomGH was built specifically for this regulatory environment — not adapted from a generic compliance tool.

---

## Academic Context

AxiomGH was developed as a practical implementation of MSc research on Zero Trust Architecture (ZTA) for financial institutions at GCTU. The platform applies ZTA principles — never trust, always verify, least privilege access — to the compliance assessment and evidence management process itself.

**Thesis:** Designing and Evaluating a Hybrid Zero Trust Architecture (ZTA) Access Control Model for Enterprise Cloud Systems Using AWS  
**Supervisor:** Prof. Amankwa  
**Institution:** Ghana Communication Technology University (GCTU)  
**Expected:** May 2026

---

## Author

**Priscilla Emefa Kporha**  
MSc Computer Science Candidate — GCTU  
📧 priscillakporha900@gmail.com  
🔗 [linkedin.com/in/priscilla-akua-8bb597202](https://linkedin.com/in/priscilla-akua-8bb597202)

---

*AxiomGH is designed to assist regulated financial institutions in Ghana with self-assessment against the BoG CISD 2026. This platform does not constitute legal or regulatory advice. Institutions remain responsible for their own compliance obligations.*
