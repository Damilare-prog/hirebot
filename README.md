# Hirebot — AI Job Hunter Platform

A production-ready AI-powered job hunting platform. Upload your CV, get semantic job matching, and auto-apply with AI-generated cover letters.

## Architecture

```
hirebot/
├── frontend/     Next.js 14 + Tailwind (your UI)
├── api/          FastAPI + PostgreSQL + pgvector
├── scraper/      Playwright (job discovery + auto-apply)
├── shared/       TypeScript types & schemas
└── infra/        Docker, migrations
```

## Quick Start

1. **Clone & configure:**
   ```bash
   cp .env.example .env
   # Add your ANTHROPIC_API_KEY and OPENAI_API_KEY
   ```

2. **Start everything:**
   ```bash
   docker-compose up --build
   ```

3. **Access:**
   - Frontend: http://localhost:3000
   - API docs: http://localhost:8000/docs
   - Database: localhost:5432

## How It Works

### 1. CV Parsing (Claude API)
- Upload PDF/DOCX/TXT
- Claude extracts: skills, experience, education, contact info, writing style
- Profile stored in PostgreSQL with vector embedding

### 2. Job Matching (OpenAI Embeddings)
- Scraper hits LinkedIn, Greenhouse, Lever, Workday, Remote.co every few hours
- Job descriptions embedded with `text-embedding-3-small`
- Cosine similarity against user profile = match score (0-100)

### 3. Auto-Apply (Playwright)
- User clicks "Quick apply" → modal shows AI-filled form + generated cover letter
- Human reviews → confirms → Playwright submits to ATS
- Supports Greenhouse, Lever, Workday (extensible)

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/profiles/upload-cv` | Parse CV, create profile |
| GET | `/profiles/{id}` | Get profile |
| GET | `/jobs/` | List jobs with match scores |
| POST | `/jobs/ingest` | Scraper pushes new jobs |
| POST | `/applications/prepare` | Generate cover letter, map fields |
| POST | `/applications/{id}/submit` | Queue for auto-submission |

## Tech Stack

- **Frontend:** React 18, Next.js 14, Tailwind CSS, Tabler Icons
- **Backend:** Python 3.11, FastAPI, SQLAlchemy, pgvector
- **AI:** Claude 3 Sonnet (CV parsing + cover letters), OpenAI embeddings
- **Scraper:** Playwright, BullMQ (job queues), Redis
- **Database:** PostgreSQL 15 with pgvector extension
- **Infra:** Docker, docker-compose

## Production Checklist

- [ ] Add authentication (Clerk/Auth0 + JWT)
- [ ] Set up S3/CloudFront for CV storage
- [ ] Configure BullMQ + Redis for background jobs
- [ ] Add proxy rotation for scraper (ScrapingBee/Bright Data)
- [ ] Implement rate limiting & retry logic
- [ ] Add monitoring (Sentry, Datadog)
- [ ] Set up CI/CD (GitHub Actions)
- [ ] Configure SSL & custom domain
- [ ] Add email notifications for application status
- [ ] Implement LinkedIn OAuth for authenticated scraping

## License

MIT


## Quick Deploy with Railway

For the easiest deployment experience, use Railway:

```bash
# 1. Push to GitHub
git push origin main

# 2. Go to railway.app → New Project → Deploy from GitHub

# 3. Add PostgreSQL database (one click)

# 4. Deploy API service (Root Directory: api)

# 5. Deploy Frontend service (Root Directory: frontend)

# 6. Set environment variables in Railway dashboard
```

See [RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md) for detailed instructions.
