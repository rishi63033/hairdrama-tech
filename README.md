# HairDrama Tech — Task Management App

A full-stack task management application with Google OAuth, task assignment, and email notifications.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT BROWSER                        │
│              Next.js 14 + TypeScript (Vercel)                │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS REST API calls
┌──────────────────────▼──────────────────────────────────────┐
│                    FLASK BACKEND (Railway/Render)            │
│  - Google OAuth 2.0 token verification                       │
│  - Task CRUD endpoints                                       │
│  - User management                                           │
│  - Gmail SMTP email notifications                            │
└────────┬────────────────────────────────┬───────────────────┘
         │ SQL (psycopg2)                  │ Gmail SMTP
┌────────▼────────────┐       ┌───────────▼───────────────────┐
│  Supabase (Postgres) │       │  Gmail API / SMTP              │
│  - users table       │       │  - Task created notifications  │
│  - tasks table       │       │  - Task completed notifications│
│  - /migrations       │       └───────────────────────────────┘
└─────────────────────┘
```

### Key Components

| Layer | Technology | Hosting |
|-------|-----------|---------|
| Frontend | Next.js 14 + TypeScript + Tailwind CSS | Vercel |
| Backend | Flask (Python 3.11) | Railway / Render |
| Database | Supabase (PostgreSQL) | Supabase |
| Auth | Google OAuth 2.0 (via `google-auth` library) | — |
| Email | Gmail SMTP (via Python `smtplib`) | — |

---

## Features

- **Google OAuth Login** — Users sign in with their Gmail accounts
- **Create Tasks** — Title, description, priority, due date
- **Assign Tasks** — Assign tasks to any registered user
- **Email Notifications** — Gmail email sent when task is created or completed
- **Dashboard** — View your tasks and tasks assigned to you

---

## Project Structure

```
hairdrama-tech/
├── frontend/                  # Next.js + TypeScript app
│   ├── src/
│   │   ├── app/               # App Router pages
│   │   │   ├── page.tsx       # Landing/login page
│   │   │   ├── dashboard/     # Main dashboard
│   │   │   └── tasks/         # Task pages
│   │   ├── components/        # Reusable components
│   │   ├── lib/               # API client, auth helpers
│   │   └── types/             # TypeScript types
│   ├── .env.local.example
│   └── package.json
│
├── backend/                   # Flask API
│   ├── app/
│   │   ├── __init__.py        # Flask app factory
│   │   ├── routes/
│   │   │   ├── auth.py        # OAuth endpoints
│   │   │   ├── tasks.py       # Task CRUD
│   │   │   └── users.py       # User endpoints
│   │   ├── models.py          # DB query helpers
│   │   ├── email_service.py   # Gmail SMTP service
│   │   └── middleware.py      # JWT auth middleware
│   ├── migrations/            # SQL migration files
│   │   ├── 001_create_users.sql
│   │   └── 002_create_tasks.sql
│   ├── .env.example
│   ├── requirements.txt
│   └── run.py
│
└── README.md
```

---

## Local Development Setup

### Prerequisites
- Node.js 18+
- Python 3.11+
- Supabase project
- Google Cloud project (OAuth credentials)
- Gmail account with App Password

### 1. Clone & configure environment

```bash
git clone https://github.com/YOUR_USERNAME/hairdrama-tech.git
cd hairdrama-tech
```

### 2. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Fill in your .env values
python run.py
```

### 3. Frontend setup

```bash
cd frontend
npm install
cp .env.local.example .env.local
# Fill in your .env.local values
npm run dev
```

### 4. Run database migrations

```bash
# Connect to your Supabase project SQL editor and run:
# migrations/001_create_users.sql
# migrations/002_create_tasks.sql
```

---

## Environment Variables

See `backend/.env.example` and `frontend/.env.local.example`.

---

## Deployment

| Service | URL |
|---------|-----|
| Frontend (Vercel) | `https://hairdrama-tech.vercel.app` |
| Backend (Railway) | `https://hairdrama-tech-backend.up.railway.app` |
| Database (Supabase) | Supabase dashboard |

### Deploy Frontend to Vercel
```bash
cd frontend
npx vercel --prod
```

### Deploy Backend to Railway
```bash
# Install Railway CLI
npm install -g @railway/cli
railway login
railway init
railway up
```

---

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/google` | Exchange Google ID token for JWT |
| GET | `/api/auth/me` | Get current user |

### Tasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | List all tasks for current user |
| POST | `/api/tasks` | Create a new task |
| GET | `/api/tasks/:id` | Get task by ID |
| PUT | `/api/tasks/:id` | Update task |
| DELETE | `/api/tasks/:id` | Delete task |
| PATCH | `/api/tasks/:id/complete` | Mark task complete |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users` | List all users (for assignment) |

---

## License
MIT
