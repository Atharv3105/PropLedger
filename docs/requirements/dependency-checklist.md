# PropLedger — Environment & Dependency Checklist
## Hardware, Runtime, and Technology Audit

> [!IMPORTANT]
> **Rule A1 & A5 Compliance**:
> All tools detected on the host machine are recorded below. No unavailable technology is assumed. Approved substitutions are explicitly noted and fully traceable.

---

## 1. Host Machine Environment Audit

| Component | Target Version | Detected Local Version | Status | Notes |
|---|---|---|---|---|
| **Operating System** | Windows 10/11 | Windows 11 (NT 10.0) | ✅ Ready | Native environment |
| **Node.js** | >= 18.0.0 | **v24.19.0** | ✅ Ready | Powers React + Vite frontend |
| **npm** | >= 9.0.0 | **11.17.0** | ✅ Ready | Package manager for frontend |
| **Python** | >= 3.10.0 | **3.14.7** | ✅ Ready | Powers FastAPI backend & reporting |
| **pip** | >= 23.0.0 | **26.2.1** | ✅ Ready | Python package installer |
| **Git** | >= 2.30.0 | **2.55.0.windows.4** | ✅ Ready | Version control |
| **Docker Engine** | >= 20.0.0 | **29.7.2** | ✅ Ready | Daemon running; hosts PostgreSQL container |
| **SQL Server** | Developer / Express | Not installed locally | ⚠️ Substituted | Approved substitution: PostgreSQL 16 (via Docker) |
| **.NET SDK** | .NET 8.0 LTS | Skipped per user request | ⚠️ Substituted | Approved substitution: FastAPI (Python 3.14) |
| **SSRS** | SQL Server Reporting | Not installed locally | ⚠️ Substituted | Approved substitution: FastAPI ReportingService + WeasyPrint/openpyxl |
| **Crystal Reports** | SAP Crystal Runtime | Not installed locally | ⚠️ Substituted | Approved substitution: ReportLab formal financial reporting module |

---

## 2. Approved Technology Stack Substitutions (Rule A1 Declaration)

### Database: PostgreSQL 16 (replacing Microsoft SQL Server)
- **Host Mechanism**: Docker container `propledger-db` running image `postgres:16-alpine` on port `5432`.
- **Preservation of PRD Intent**:
  - Full support for recursive and non-recursive CTEs (`WITH RECURSIVE`).
  - Full support for all required window functions (`ROW_NUMBER`, `RANK`, `DENSE_RANK`, `LAG`, `LEAD`, `SUM OVER`, `AVG OVER`).
  - Cross-tabulation / PIVOT equivalent via `tablefunc` extension (`crosstab()`) and conditional aggregation (`FILTER` / `CASE WHEN`).
  - Stored procedures and functions via `PL/pgSQL` with explicit transaction control (`BEGIN`, `COMMIT`, `ROLLBACK`).
  - Triggers (`AFTER INSERT`, `BEFORE UPDATE`) and audit tables.
  - Execution plan analysis via `EXPLAIN (ANALYZE, BUFFERS, VERBOSE)`.
  - Composite, partial, and covering indexes (`INCLUDE`).

### Backend: FastAPI & Python (replacing ASP.NET Core)
- **Runtime**: Python 3.14.7 with `FastAPI`, `uvicorn`, `SQLAlchemy`, `asyncpg`, and `pydantic`.
- **Preservation of PRD Intent**:
  - Server-side RBAC middleware and JWT authentication.
  - Clean layered architecture (Routers -> Services -> Repositories -> Database).
  - Transactional payment processing orchestration with atomic rollback.
  - Global error handling translating database exceptions to structured JSON problem details.
  - Comprehensive logging and diagnostic endpoints.

### Reporting Engine: FastAPI ReportingService + WeasyPrint + openpyxl (replacing SSRS)
- **Architecture**:
  - Authoritative SQL stored procedures / queries generate tabular datasets.
  - FastAPI `ReportingService` handles parameter validation, grouping, subtotals, conditional formatting, and multi-dataset assembly.
  - `WeasyPrint` compiles HTML/CSS report templates into paginated, print-ready PDF files with running headers, footers, page numbering, and company branding.
  - `openpyxl` generates styled multi-sheet Excel (.xlsx) workbooks with frozen headers and formulas.
  - React frontend embeds interactive report previews with direct PDF/Excel download buttons.

### Crystal Reports Equivalent: ReportLab Module (replacing SAP Crystal Reports)
- **Architecture**:
  - A distinct reporting pipeline in `reporting/crystal-equivalent/` using `reportlab.platypus` and flowables.
  - Renders 3 formal financial statements (Tenant Payment History, Property Rent Roll, Property Income & Expense) with precise point-level typography, tabular borders, and formal accounting headers.
  - Serves as proof of multi-tool reporting competency.

---

## 3. Required Python Packages for Backend & Reporting

The following packages will be installed in the backend virtual environment:

```text
fastapi>=0.110.0
uvicorn[standard]>=0.28.0
sqlalchemy>=2.0.28
asyncpg>=0.29.0
psycopg2-binary>=2.9.9
pydantic>=2.6.4
pydantic-settings>=2.2.1
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.9
weasyprint>=61.2
openpyxl>=3.1.2
reportlab>=4.1.0
pytest>=8.1.1
pytest-asyncio>=0.23.5
httpx>=0.27.0
```

---

## 4. Phase Readiness Gate Status

- [x] Phase 0: Requirements & Execution Control — **READY**
- [x] Phase 1: Database Foundation (PostgreSQL 16 via Docker) — **READY**
- [x] Phase 2: Advanced SQL (PL/pgSQL, CTEs, Window Functions) — **READY**
- [x] Phase 3: Business Workflows (Atomic Transactions, Billing Engine) — **READY**
- [x] Phase 4: FastAPI Backend API — **READY**
- [x] Phase 5: React Application (Vite + TS + Tailwind) — **READY**
- [x] Phase 6: SSRS Reporting Equivalent (WeasyPrint + openpyxl) — **READY**
- [x] Phase 7: Crystal Reports Equivalent (ReportLab Module) — **READY**
- [x] Phase 8: Performance Engineering (EXPLAIN ANALYZE + Indexing) — **READY**
- [x] Phase 9: Testing & Quality Validation (pytest + SQL tests) — **READY**
- [x] Phase 10: Interview & Portfolio Packaging — **READY**
