# PrintProject — Task Breakdown

Status legend: `[ ]` todo · `[~]` in progress · `[x]` done

---

## Phase 0 — Project Setup

- [x] Write project README and architecture overview
- [x] Write task breakdown (this file)
- [x] Initialize git repository
- [ ] Create directory structure (cloud/frontend, cloud/backend, pi/frontend, pi/backend, docs, infra)
- [ ] Write `.gitignore` (Node, Python, .NET, OS files)
- [ ] Decide and document final answers to open questions in README

---

## Phase 1 — Cloud Backend (.NET 8 / ASP.NET Core)

### 1.1 Project Scaffolding
- [ ] `dotnet new webapi` in `cloud/backend/`
- [ ] Add packages: EF Core, Npgsql, AWSSDK.S3, Razorpay SDK, FluentValidation
- [ ] Configure appsettings + environment-based config (dev / prod)
- [ ] Set up PostgreSQL connection with EF Core

### 1.2 Database Schema
- [ ] Design and create EF Core models:
  - `PrintJob` — id, code, status, file_key (S3), printer_type, options, created_at, expires_at, used_at
  - `Payment` — id, job_id, razorpay_order_id, razorpay_payment_id, amount, status, created_at
- [ ] Run initial EF Core migration

### 1.3 File Upload API
- [ ] `POST /api/jobs/upload` — accept multipart file, validate type and size, upload to S3
- [ ] Generate pre-signed S3 URL or store file_key
- [ ] Return `job_id` and draft job details

### 1.4 Payment API
- [ ] `POST /api/payments/create-order` — create Razorpay order for job_id
- [ ] `POST /api/payments/verify` — verify Razorpay signature, mark payment complete
- [ ] On payment success: generate one-time print code, set job status to `PAID`, set expiry TTL

### 1.5 Pi Validation API
- [ ] `POST /api/jobs/validate-code` — validate code, return job metadata + signed S3 download URL
- [ ] Mark job as `CLAIMED` on first successful validation (prevent reuse)
- [ ] Return 404 / 410 for invalid or already-used codes

### 1.6 Job Lifecycle
- [ ] `GET /api/jobs/{id}/status` — return current print job status (for kiosk polling)
- [ ] `PATCH /api/jobs/{id}/status` — Pi backend updates status (PRINTING, DONE, FAILED)
- [ ] Scheduled cleanup: delete expired/used files from S3, purge old records

### 1.7 Security & Config
- [ ] HTTPS only; CORS locked to kiosk origin and web app origin
- [ ] Rate limiting on validate-code endpoint (prevent brute force)
- [ ] API key auth between Pi backend and cloud backend (simple shared secret for MVP)
- [ ] Input validation on all endpoints

---

## Phase 2 — Cloud Frontend (React + Vite)

### 2.1 Project Scaffolding
- [ ] `npm create vite@latest` in `cloud/frontend/` with React + TypeScript template
- [ ] Add: React Router, Axios, Tailwind CSS, Razorpay checkout script

### 2.2 Pages & Components
- [ ] **Landing / Home** — tagline, "Print Now" CTA, QR description
- [ ] **Upload Page**
  - File picker (drag & drop + button), type/size validation on client
  - Print options: type (document/photo), color/BW, copies, paper size
  - File preview (PDF preview, image thumbnail)
- [ ] **Payment Page**
  - Order summary (file name, options, price)
  - Razorpay checkout integration
  - Loading/success/failure states
- [ ] **Code Display Page**
  - Large, clear display of one-time print code
  - "Save to phone" / copy button
  - Instructions for using the kiosk
- [ ] **Error / Expired Page**

### 2.3 Pricing Logic
- [ ] Define pricing table (BW per page, color per page, photo sizes)
- [ ] Client-side price calculation based on options

---

## Phase 3 — Pi Backend (Python 3 / FastAPI)

### 3.1 Project Scaffolding
- [ ] Create `pi/backend/` Python project with `venv`
- [ ] Add packages: `fastapi`, `uvicorn`, `pycups`, `httpx`, `python-dotenv`, `aiofiles`
- [ ] Configure environment variables (cloud API URL, API key, printer names)

### 3.2 Code Validation & File Download
- [ ] `POST /local/print` — accept code from kiosk UI
- [ ] Call cloud `validate-code` API with the entered code
- [ ] On success: download file from the returned signed S3 URL to local temp dir
- [ ] Handle errors: invalid code, expired, network failure

### 3.3 CUPS Print Queue Integration
- [ ] Detect printer type from job metadata (`COLOR_PHOTO` or `LASER_DOCUMENT`)
- [ ] Map printer type to correct CUPS printer name (from config)
- [ ] Submit job to CUPS via `pycups` with correct options (copies, paper size, color mode)
- [ ] Monitor CUPS job status and poll until complete/failed
- [ ] Report final status back to cloud API

### 3.4 Local Job State
- [ ] Maintain a lightweight local SQLite DB (via `aiosqlite`) for in-flight jobs
  - Survives Pi restarts; prevents re-downloading on reconnect
- [ ] Clean up temp files after successful print

### 3.5 System Service
- [ ] Write `systemd` unit file for pi backend auto-start on boot
- [ ] Auto-restart on crash policy

---

## Phase 4 — Pi Frontend (React + Vite — Kiosk UI)

### 4.1 Project Scaffolding
- [ ] `npm create vite@latest` in `pi/frontend/` with React + TypeScript
- [ ] Tailwind CSS; design for **touch display** (large tap targets, high contrast)
- [ ] Configure to connect to Pi backend (localhost)

### 4.2 Screens
- [ ] **Idle / Attract Screen**
  - Animated QR code for cloud web app URL
  - "Scan to upload" instruction
  - "Already have a code? Tap here" button
  - Rotating store branding / promotional content
- [ ] **Enter Code Screen**
  - Large on-screen numpad or alphanumeric keyboard
  - Code input field with clear visual feedback
  - Submit / Cancel buttons
- [ ] **Processing Screen**
  - "Downloading your file..." with progress indicator
  - "Sending to printer..." status
- [ ] **Success Screen**
  - Confirmation message, estimated wait time
  - Auto-return to idle after timeout
- [ ] **Error Screen**
  - Clear error messages (invalid code / printer offline / network error)
  - Retry / Return to idle options

### 4.3 Kiosk Hardening
- [ ] Chromium kiosk mode launch script (full-screen, no address bar)
- [ ] Disable right-click and keyboard shortcuts in app
- [ ] Auto-refresh / watchdog for frontend process
- [ ] Write `systemd` unit file for frontend auto-start

---

## Phase 5 — Integration & Testing

- [ ] End-to-end test: upload → pay → get code → enter on kiosk → printed
- [ ] Test code expiry behavior
- [ ] Test printer queue when both printers busy
- [ ] Test network drop between Pi download and print
- [ ] Test large file handling (multi-page PDF)
- [ ] Test concurrent users (multiple uploads at once)
- [ ] Validate Razorpay webhook signature handling

---

## Phase 6 — Infrastructure & Deployment

### Cloud
- [ ] Choose AWS deployment: EC2 (simple) or ECS Fargate (scalable)
- [ ] Set up RDS PostgreSQL instance
- [ ] Create S3 bucket with lifecycle policies (auto-delete after TTL)
- [ ] Configure environment variables / AWS Secrets Manager
- [ ] Set up domain + SSL (ACM + ALB or Cloudflare)
- [ ] CI/CD pipeline (GitHub Actions) for cloud backend and frontend

### Pi
- [ ] Write Pi setup script (`setup.sh`): install Python, Node, CUPS, deps, systemd services
- [ ] Configure Pi auto-login and kiosk auto-start on boot
- [ ] Configure CUPS printers (already tested — document steps in `docs/deployment.md`)
- [ ] Test cold boot to kiosk ready

---

## Phase 7 — Nice to Haves (Post-MVP)

- [ ] Admin dashboard — live job queue, revenue, printer status
- [ ] SMS/WhatsApp notification to customer with print code
- [ ] Multi-store support (store_id scoping on cloud backend)
- [ ] Print job history for customers (optional account)
- [ ] USB walk-up printing (local upload at kiosk)
- [ ] Printer ink/paper level alerts
- [ ] Remote Pi management (SSH tunnel or Tailscale)
