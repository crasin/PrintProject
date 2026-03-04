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
   - Uploads file(s) — PDF, DOCX, JPG, PNG
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

- **One-time codes** expire after first use or after a configurable TTL (e.g. 30 min).
- **Files are deleted from S3** after successful print (or after TTL) for privacy.
- **Pi operates offline-tolerant** — once a file is downloaded, printing continues even if
  cloud connectivity drops momentarily.
- **Pi backend runs as a systemd service** — auto-starts on boot, restarts on crash.
- **Kiosk frontend runs in Chromium kiosk mode** — full-screen, no browser chrome.

---

## Open Questions (to resolve before implementation)

- [ ] File types to support: PDF, DOCX, JPG, PNG — any others (e.g. XLSX)?
- [ ] Max file size per upload?
- [ ] How long should uploaded files remain on S3 before auto-delete?
- [ ] Should the kiosk also support walk-up USB or only cloud uploads?
- [ ] Multi-store support needed now or a future phase?
- [ ] Admin dashboard needed (view jobs, revenue, printer status)?
- [ ] Should print codes be numeric-only (easier to type on touch) or alphanumeric?
