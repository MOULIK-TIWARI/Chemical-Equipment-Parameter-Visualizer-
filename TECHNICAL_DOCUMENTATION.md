# Chemical Equipment Analytics — Technical Documentation

Version: workspace snapshot (branch: `main`)
Date: 2025-11-21

---

## Contents
- Architecture Overview
- Components and Responsibilities
- Dependencies
- Setup & Run
- Backend: File-by-file responsibilities
- API Services: responsibilities
- Frontend: File-by-file responsibilities
- Desktop App: File-by-file responsibilities
- Tests
- Data model summary
- API endpoints (summary)
- How components connect (end-to-end)
- Next steps / Recommendations

---

**Architecture Overview**

This project is a three-tier application for uploading, validating and analyzing chemical equipment CSV datasets and producing downloadable PDF reports. The main parts are:

- Backend: Django + Django REST Framework API (serves data, authentication, CSV processing, analytics, PDF generation).
- Frontend: React (Vite) single-page app for user interaction (login, upload, view dashboard, charts, download reports).
- Desktop client: PyQt5-based application scaffold that can use the same API via an `APIClient`.

Services in the backend are split into a service layer (`csv_processor`, `analytics_service`, `pdf_generator`) to keep business logic outside views.

---

**Components and Responsibilities (high level)**

- `backend/` — Django project; implements REST API, models, serializers, viewsets, middleware and unit tests.
- `backend/api/services/` — Python service modules (CSV parsing/validation, analytics computation, PDF generation).
- `frontend/` — React application that consumes the API; uses `axios`, `chart.js`, and React Router.
- `desktop_app/` — PyQt5 app scaffold and an HTTP `APIClient` to interact with the backend programmatically.
- Tests (primarily `backend/api/tests.py`) provide extensive coverage for CSV processing, upload flow, analytics and permissions.

---

**Dependencies**

Backend / Desktop (Python):
- See `requirements.txt` (top-level). Core packages referenced in code:
  - `Django` (4.x assumed)
  - `djangorestframework`
  - `djangorestframework-authtoken`
  - `pandas` (CSV parsing/validation)
  - `reportlab` (PDF generation)
  - `matplotlib` (charts embedded in PDFs)
  - `PyQt5` (desktop UI)

Frontend (JavaScript):
- See `frontend/package.json` — key deps:
  - `react`, `react-dom`
  - `axios` (HTTP client)
  - `chart.js`, `react-chartjs-2` (charts in dashboard)
  - `react-router-dom` (routing)
  - `vite` and `@vitejs/plugin-react` (dev tooling)

---

**Setup & Run (short)**

Backend (dev):

1. Create and activate Python virtualenv.
2. Install dependencies: `pip install -r requirements.txt`.
3. Run migrations: `python manage.py migrate`.
4. Run server: `python manage.py runserver`.

Frontend (dev):

1. `cd frontend`.
2. `npm install` (or `pnpm`/`yarn`).
3. `npm run dev` (starts Vite dev server).

Desktop (dev):

1. Install `PyQt5` and other Python deps (same `requirements.txt`).
2. `python desktop_app/main.py` (currently scaffold; UI main window TODO).

Note: Ports and base URLs are configured in `chemical_equipment_analytics/settings.py` (backend) and `frontend` env (defaults to `http://localhost:8000/api`). Desktop `config.ini` contains default base URL and timeouts.

---

**Backend: File-by-file responsibilities**

Below are the important files and what they do. Paths are relative to `backend/`.

- `manage.py`:
  - Django CLI entrypoint for running server, migrations, tests.

- `chemical_equipment_analytics/settings.py`:
  - Django settings: installed apps (`api`, `rest_framework`, `corsheaders`), auth configuration (`TokenAuthentication`), CORS config for frontend dev, database (SQLite), middleware (includes custom `api.middleware.TokenValidationMiddleware`), and REST pagination defaults.

- `chemical_equipment_analytics/urls.py`:
  - Mounts `admin/` and `api/` route namespaces.

- `api/apps.py`:
  - `AppConfig` for the `api` app.

- `api/__init__.py`:
  - Package initializer (empty).

- `api/admin.py`:
  - Registers `Dataset` and `EquipmentRecord` models in Django Admin and configures list display/filters.

- `api/middleware.py`:
  - `TokenValidationMiddleware`: inspects `HTTP_AUTHORIZATION` header and validates token presence/active user; sets `request.user = AnonymousUser()` for invalid tokens. Provides an extra guard in addition to DRF auth.

- `api/models.py`:
  - `Dataset` model: stores dataset metadata and cached summary fields (`total_records`, `avg_flowrate`, `avg_pressure`, `avg_temperature`, `type_distribution` (JSONField)).
    - `calculate_summary_statistics()` computes aggregates from related `EquipmentRecord`s.
    - `maintain_history_limit(user, limit=5)` deletes oldest datasets beyond a per-user limit.
  - `EquipmentRecord` model: stores each CSV row (equipment_name, equipment_type, flowrate, pressure, temperature) and a FK `dataset`.

- `api/serializers.py`:
  - `UserSerializer`, `EquipmentRecordSerializer`, `DatasetSerializer`, `DatasetDetailSerializer` (includes `records`). Used by DRF views to produce JSON.

- `api/permissions.py`:
  - `IsOwnerOrReadOnly`, `IsDatasetOwner` — custom permission classes ensuring that only dataset owners can access or modify their datasets.

- `api/urls.py`:
  - DRF router registering `DatasetViewSet` at `/api/datasets/`; routes for auth endpoints (`auth/login/`, `auth/register/`, `auth/logout/`).

- `api/views.py`:
  - `LoginView`, `RegisterView`, `LogoutView`: handle token-based auth flows using `rest_framework.authtoken`.
  - `DatasetViewSet` (ModelViewSet): main API for datasets.
    - `get_queryset()` restricts to datasets uploaded by authenticated user; listing returns last 5 items.
    - `upload` action (`POST /api/datasets/upload/`): validates `.csv` extension, uses `CSVProcessor` to parse and validate file, creates `Dataset` and `EquipmentRecord` objects, computes summary, and trims history to 5 datasets per user.
    - `data` action (`GET /api/datasets/{id}/data/`): returns paginated `EquipmentRecord`s.
    - `summary` action (`GET /api/datasets/{id}/summary/`): returns stored summary fields.
    - `report` action (`GET /api/datasets/{id}/report/`): invokes `PDFGenerator` to create report and returns `application/pdf`.
  - `EquipmentRecordPagination`: custom pagination class (page_size=50).

- `api/tests.py`:
  - Comprehensive test suite that validates authentication, permissions, CSV parsing rules, upload flow, history maintenance, analytics computations, pagination, and PDF generation endpoints.

---

**API Services (backend/api/services)**

- `csv_processor.py`:
  - `CSVProcessor` class — central CSV parsing and validation logic.
    - `REQUIRED_COLUMNS` defines expected CSV header fields: `Equipment Name`, `Type`, `Flowrate`, `Pressure`, `Temperature`.
    - Numeric validation: `Flowrate` and `Pressure` must be positive (> 0); `Temperature` can be negative.
    - Methods: `validate_csv_structure`, `validate_required_fields`, `validate_numeric_fields`, `validate`, `parse_to_records`, `parse_csv_file` (file-like), `create_equipment_records` (bulk_create into DB).
    - Raises `CSVValidationError` for validation failures.

- `analytics_service.py`:
  - `AnalyticsService` computes analytics from a `Dataset` or a provided queryset:
    - `calculate_total_count`, `calculate_averages` (flowrate/pressure/temperature via ORM `Avg`), `generate_type_distribution` (ORM `Count` per `equipment_type`), `calculate_summary_statistics`, and `update_dataset_statistics` (copies computed values into `Dataset` instance — caller saves model).

- `pdf_generator.py`:
  - `PDFGenerator` uses ReportLab and Matplotlib to produce a report that includes:
    - Dataset metadata, summary statistics, chart of equipment type distribution (Matplotlib), and a table of equipment records (with an optional `max_records` limit).
    - Exposes `generate_dataset_report(dataset, include_records=True, max_records=None)` which returns a `BytesIO` with PDF content.

---

**Frontend: File-by-file responsibilities (important files)**

Files are in `frontend/src`.

- `src/services/api.js`:
  - `axios` instance configured with base URL (env var fallback), request interceptor that adds `Authorization: Token <token>` using `getToken()` from `utils/auth`, and response interceptor that handles errors (401 triggers `logout()` and redirect to `/login`).

- `src/utils/auth.js`:
  - LocalStorage helpers: `getToken`, `setToken`, `removeToken`, `getUsername`, `setUsername`, `isAuthenticated`, `validateToken`, `logout`.

- `src/App.jsx`:
  - Routes configuration (public `/login`, protected `/dashboard` and `/history` via `PrivateRoute`).

- `src/components/Auth/Login.jsx`:
  - Login form, calls `api.post('/auth/login/')`, stores token via `setToken`, navigates to `/dashboard` on success.

- `src/components/Auth/PrivateRoute.jsx`:
  - Route guard that checks `isAuthenticated()` and redirects to `/login` if not logged in (protects dashboard/history pages).

- `src/components/Dashboard/*`:
  - `Dashboard.jsx`: orchestrates fetching the most recent dataset (last 5 via `/datasets/`) and fetching dataset summary (`/datasets/{id}/summary/`) and data (`/datasets/{id}/data/`). Renders `SummaryStats`, `Charts`, `DataTable`, `PDFDownload`, and `FileUpload` components.
  - `SummaryStats.jsx`, `Charts.jsx`, `DataTable.jsx`: presentational components rendering summary metrics, charts (chart.js), and table of records respectively.

- `src/components/Upload/FileUpload.jsx`:
  - Upload UI; posts CSV file as multipart/form-data to `/api/datasets/upload/`.

- `src/components/Reports/PDFDownload.jsx`:
  - Trigger to GET `/api/datasets/{id}/report/` and download the PDF.

- Other assets (CSS) live alongside components and style the UI.

---

**Desktop App: File-by-file responsibilities**

Files are in `desktop_app/`.

- `config.ini`:
  - Default configuration: API base URL (`http://localhost:8000/api`), timeouts, app name, default page size and file paths for temporary and report storage.

- `utils/config.py`:
  - `get_config()` reads `config.ini` and returns a `Config` object exposing typed values used by desktop app.

- `services/api_client.py`:
  - `APIClient` class used by desktop UI to communicate with backend.
  - Handles login/register/logout, token persistence to `~/.chemical_equipment_analytics/token.txt`, file upload (`upload_dataset`), dataset retrieval (`get_datasets`, `get_dataset`, `get_dataset_data`, `get_dataset_summary`), report download (`download_report`) and network/error handling.

- `ui/login_dialog.py`:
  - PyQt5 `LoginDialog` that collects credentials and calls `api_client.login()`; emits a `login_successful` signal on success.

- `main.py`:
  - Desktop app entry; initializes QApplication and config, placeholder for launching UI main window (currently scaffolded).

---

**Tests**

- `backend/api/tests.py`:
  - Broad and detailed tests covering CSV parsing rules (missing columns, non-numeric values, negative/zero checks), creation of `Dataset` and `EquipmentRecord`s via upload endpoint, authentication & permission enforcement, listing/retrieve operations, pagination, analytics service behavior, and parts of the PDF/report flow.

- Other high-level test files exist near the repo root for validating the API and desktop components (e.g., `test_api_report_endpoint.py`).

Running tests: `python manage.py test` (ensuring virtualenv and dependencies are installed).

---

**Data model summary**

- `Dataset`:
  - `id`, `name`, `uploaded_at`, `uploaded_by` (FK to `auth.User`), `total_records`, `avg_flowrate`, `avg_pressure`, `avg_temperature`, `type_distribution` (JSON)
  - Relationships: One-to-many `Dataset.records -> EquipmentRecord` (related_name `records`).

- `EquipmentRecord`:
  - `id`, `dataset` (FK), `equipment_name`, `equipment_type`, `flowrate`, `pressure`, `temperature`.

---

**API Endpoints (summary)**

- Authentication:
  - `POST /api/auth/login/` — body: `{username, password}` → returns `{token, user_id, username}`
  - `POST /api/auth/register/` — create user and token
  - `POST /api/auth/logout/` — delete token

- Datasets (DRF `DatasetViewSet`): mounted under `/api/datasets/` via router
  - `GET /api/datasets/` — list (returns last 5 for authenticated user)
  - `POST /api/datasets/` — (ModelViewSet default create; upload exists separately)
  - `POST /api/datasets/upload/` — custom action that accepts CSV multipart/form-data `file` field, parses/validates, creates `Dataset` + `EquipmentRecord`s, computes summary, returns created dataset JSON.
  - `GET /api/datasets/{id}/` — retrieve dataset detail (includes `records`) — owner-only
  - `DELETE /api/datasets/{id}/` — delete dataset — owner-only
  - `GET /api/datasets/{id}/data/` — custom action returning paginated equipment records
  - `GET /api/datasets/{id}/summary/` — custom action returning summary stats
  - `GET /api/datasets/{id}/report/` — custom action generating a PDF report (attachment)

Permissions: all dataset endpoints require token auth; `IsDatasetOwner` is enforced for retrieve/update/delete/report/data actions.

---

**How components connect (end-to-end)**

- User (frontend or desktop) logs in → receives token.
- Client stores token (`localStorage` for web, token file for desktop) and includes it in `Authorization: Token <token>` header for subsequent requests.
- Client posts CSV to `/api/datasets/upload/`.
  - Backend `DatasetViewSet.upload` checks extension, passes file to `CSVProcessor.parse_csv_file()`.
  - `CSVProcessor` validates columns and numeric constraints and converts rows to record objects.
  - Backend creates `Dataset` record and `EquipmentRecord` objects (via `bulk_create`) and calls `Dataset.calculate_summary_statistics()`.
  - `Dataset.maintain_history_limit()` ensures only last 5 datasets are kept per user.
- Dashboard fetches dataset summary and records and renders charts/tables.
- User can request `/api/datasets/{id}/report/`, which calls `PDFGenerator.generate_dataset_report()` to build the PDF with charts/tables and returns it; client downloads/saves the file.

---

**Next steps & recommendations**

- CI: add automated test runs (`python manage.py test`) and linting in CI pipeline.
- Production settings: rotate secret key, disable `DEBUG`, configure allowed hosts and static/media serving.
- Token management improvements: consider shorter token lifetime + refresh mechanism or JWT for more modern patterns.
- Desktop UI: implement `MainWindow` and hook up `APIClient` to provide parity with web features.
- Frontend: add better error handling and loading states for long-running report generation.
- Security: review file upload sanitization and limits; ensure file size and content scanning if deploying to production.

---

If you want, I can:
- Generate a compact per-file list of every file in the workspace (including CSS and README files) with one-line descriptions.
- Add architecture diagrams (Mermaid or PlantUML) to this document.
- Run `python manage.py test` here and present failing tests (if you want me to run tests locally in this workspace).

