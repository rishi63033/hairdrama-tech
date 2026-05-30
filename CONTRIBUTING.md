# Contributing to HairDrama Tech Task Manager

Thanks for contributing! Here's how we work as a team.

## Branching

- `main` — production-ready code only, don't push directly here
- `dev` — our main working branch, all PRs go here first
- Feature branches should be named like `feature/task-filters` or `fix/email-bug`

## Getting Started

1. Fork or clone the repo
2. Create a new branch from `dev`
3. Make your changes
4. Open a PR against `dev` with a short description of what you did

## Running Locally

See the [README](./README.md) for full setup instructions.

Quick version:
```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
cp .env.example .env       # fill in your values
python run.py

# Frontend (separate terminal)
cd frontend
npm install
cp .env.local.example .env.local   # fill in your values
npm run dev
```

## Code Style

- **Backend (Python)**: Keep it readable, add comments for anything non-obvious
- **Frontend (TypeScript)**: Prefer named exports, keep components small
- No need to be super strict about formatting — just be consistent with the existing code

## Environment Variables

**Never commit `.env` or `.env.local` files.** They're already in `.gitignore`.

If you add a new env variable, update both `.env.example` (backend) and `.env.local.example` (frontend) so others know what they need.

## Pull Requests

- Keep PRs focused — one feature or fix per PR
- Write a short description of what changed and why
- If you're fixing a bug, mention how to reproduce it

## Questions?

Just ping the team on WhatsApp or open a GitHub issue.
