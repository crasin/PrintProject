# PrintProject — Retail Cloud Self-Printing Kiosk

A cloud-connected self-service print kiosk system built for retail stores in India.
Customers upload documents or photos via a web app, pay online, and collect prints
on-site by entering a one-time code at the kiosk.

---

## System Overview

```
┌─────────────────────────────────────┐      ┌──────────────────────────────────────┐
│            CLOUD (AWS)              │      │         RASPBERRY PI (On-site)       │
│                                     │      │                                      │
│  ┌─────────────┐  ┌──────────────┐  │      │  ┌─────────────┐  ┌──────────────┐  │
│  │   React     │  │  .NET API    │  │      │  │   React     │  │  Python      │  │
│  │  Web App    │◄─┤  (Backend)   │  │      │  │  Kiosk UI   │◄─┤  FastAPI     │  │
│  │             │  │              │  │      │  │ (Touch LCD) │  │  (Backend)   │  │
│  └──────┬──────┘  └──────┬───────┘  │      │  └─────────────┘  └──────┬───────┘  │
│         │                │          │      │                           │          │
│         │         ┌──────▼───────┐  │      │                    ┌──────▼───────┐  │
│         │         │  PostgreSQL  │  │      │                    │    CUPS      │  │
│         │         │  (RDS)      │  │      │                    │ Print Queue  │  │
│         │         └─────────────┘  │      │                    └──────┬───────┘  │
│         │                │          │      │                           │          │
│         │         ┌──────▼───────┐  │      │              ┌────────────┴────────┐ │
│         └────────►│   S3 Bucket  │  │◄─────┤              │  Color    │  Laser  │ │
│                   │  (Files)     │  │      │              │  Photo    │Document │ │
│                   └─────────────┘  │      │              │  Printer  │ Printer │ │
│                                     │      │              └─────────────────────┘ │
└─────────────────────────────────────┘      └──────────────────────────────────────┘
```

---

## Customer Flow

1. Customer walks up to the kiosk in the store
2. Customer scans the **QR code** on the kiosk screen or visits the web app directly
3. On the **Cloud Web App**:
   - Selects file type (document / photo)
   - Uploads file(s) — PDF, DOCX, XLSX, PPTX, JPG, PNG
   - Selects print options (color/BW, copies, paper size)
   - Makes payment via Razorpay
   - Receives a **one-time print code** (e.g. `A4K9-2X`)
4. Back at the **Kiosk**:
   - Taps "Enter Code" on the touch display
   - Enters the code
   - Pi validates the code with the cloud API
   - Pi downloads the file from S3
   - Pi sends the job to the correct CUPS printer queue
   - Kiosk shows job status / receipt

---

## Tech Stack

| Layer              | Technology          | Reason                                              |
|--------------------|---------------------|-----------------------------------------------------|
| Cloud Frontend     | React (Vite)        | Fast, modern SPA; kiosk-friendly UX                 |
| Cloud Backend      | .NET 8 (ASP.NET Core) | Robust REST API, strong typing, payment handling  |
| Cloud Database     | PostgreSQL (AWS RDS) | Reliable relational DB for jobs and payments       |
| Cloud File Storage | AWS S3              | Scalable, secure file storage                       |
| Payment Gateway    | Razorpay            | Widely used and well supported in India             |
| Pi Frontend        | React (Vite)        | Runs in Chromium kiosk mode on touch display        |
| Pi Backend         | Python 3 (FastAPI)  | Native Pi ecosystem, `pycups` for CUPS integration  |
| Print System       | CUPS (on Pi)        | Already tested and working                          |
| File Conversion    | LibreOffice headless (on Pi) | Convert DOCX/XLSX/PPTX → PDF before CUPS |
| Hosting            | AWS (EC2 / ECS)     | Cloud backend and frontend hosting                  |

---

## Pi Backend — Why Python + FastAPI?

- **`pycups`** provides native Python bindings directly to CUPS — the cleanest way to
  add jobs to print queues programmatically without shell hacks.
- Python is the de-facto language of the Raspberry Pi ecosystem.
- FastAPI is lightweight (critical for Pi's limited RAM), async-capable, and has
  automatic OpenAPI docs out of the box.
- Simpler than running a Node.js or .NET runtime on the Pi.

---

## Repository Structure

```
PrintProject/
├── README.md
├── TASKS.md
├── docs/
│   ├── architecture.md       # Detailed architecture notes
│   ├── api-contracts.md      # Cloud API + Pi API endpoint specs
│   └── deployment.md         # AWS + Pi deployment guide
├── cloud/
│   ├── frontend/             # React (Vite) — customer upload & payment UI
│   └── backend/              # ASP.NET Core 8 — REST API, auth, payments
├── pi/
│   ├── frontend/             # React (Vite) — kiosk touch UI
│   └── backend/              # Python FastAPI — code validation, CUPS control
└── infra/
    └── terraform/            # (future) AWS infrastructure as code
```

---

## Key Design Decisions

- **One-time codes** are alphanumeric (e.g. `A4K9-2X`), expire after first use or after a configurable TTL (e.g. 30 min).
- **Files are deleted from S3** after successful print (or after TTL) for privacy.
- **Pi operates offline-tolerant** — once a file is downloaded, printing continues even if
  cloud connectivity drops momentarily.
- **Pi backend runs as a systemd service** — auto-starts on boot, restarts on crash.
- **Kiosk frontend runs in Chromium kiosk mode** — full-screen, no browser chrome.
- **File conversion on Pi** — XLSX, PPTX, DOCX are converted to PDF locally on the Pi
  using LibreOffice headless before being sent to CUPS. S3 stores the original file.
- **Multi-store from day one** — every entity (job, payment, store) is scoped to a `store_id`.
  Each Pi authenticates with a per-store API key. Admin dashboard shows per-store revenue/queue.
- **Admin dashboard is MVP** — cloud frontend includes a protected `/admin` section with
  live job queue, revenue by store, and printer health status.

---

## Supported File Types

| Format | Extension | Conversion needed |
|--------|-----------|-------------------|
| PDF    | .pdf      | None — sent directly to CUPS |
| Word   | .docx     | LibreOffice → PDF on Pi |
| Excel  | .xlsx     | LibreOffice → PDF on Pi |
| PowerPoint | .pptx / .ppt | LibreOffice → PDF on Pi |
| JPEG   | .jpg / .jpeg | None — sent directly to CUPS |
| PNG    | .png      | None — sent directly to CUPS |

---

## Open Questions (resolved)

- [x] File types: PDF, DOCX, XLSX, PPTX, JPG, PNG
- [x] Code format: alphanumeric (e.g. `A4K9-2X`)
- [x] Multi-store: yes, from day one
- [x] Admin dashboard: yes, MVP scope
- [ ] Max file size per upload? *(still to decide)*
- [ ] S3 file retention TTL? *(still to decide)*
- [ ] USB walk-up printing? *(deferred — cloud-only for MVP)*
