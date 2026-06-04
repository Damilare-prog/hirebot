# Railway Deployment Guide for Hirebot

Railway deploys each service from your monorepo separately. No docker-compose needed.

## Prerequisites

1. **Railway CLI** (optional but helpful):
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Your code pushed to GitHub**

## Deployment Steps

### Step 1: Create a Railway Project

**Option A: Dashboard (Easiest)**
1. Go to https://railway.app
2. Click **New Project**
3. Select **Empty Project**

**Option B: CLI**
```bash
railway init
```

### Step 2: Add PostgreSQL Database

1. In your Railway project, click **New** → **Database** → **Add PostgreSQL**
2. Railway creates it automatically
3. Click on the Postgres service → **Variables** tab
4. You'll see `DATABASE_URL` — **copy this value**

### Step 3: Add Redis (Optional, for job queues)

1. Click **New** → **Database** → **Add Redis**
2. Copy the `REDIS_URL` value

### Step 4: Deploy the Backend (API)

1. Click **New** → **GitHub Repo**
2. Select your `hirebot` repository
3. After it imports, click on the service to open settings
4. Go to **Settings** tab:
   - **Root Directory**: `api`
   - **Builder**: `Dockerfile`
   - **Dockerfile Path**: `Dockerfile`
5. Go to **Variables** tab, add:
   ```
   DATABASE_URL=<paste from Postgres service>
   GEMINI_API_KEY=<your Google AI Studio key>
   OPENAI_API_KEY=<your OpenAI key>
   SCRAPER_API_KEY=any-random-string
   ```
6. Click **Deploy**

Wait for the build to complete. You'll get a URL like `https://hirebot-api.up.railway.app`

### Step 5: Deploy the Frontend

1. Click **New** → **GitHub Repo**
2. Select your `hirebot` repository again
3. Go to **Settings** tab:
   - **Root Directory**: `frontend`
   - **Builder**: `Nixpacks` (auto-detected)
4. Go to **Variables** tab, add:
   ```
   NEXT_PUBLIC_API_URL=<your API URL from Step 4>
   ```
5. Click **Deploy**

You'll get a URL like `https://hirebot.up.railway.app`

### Step 6: Connect Frontend to Backend

1. Copy your **API service URL** (from Step 4)
2. Go to your **Frontend service** → **Variables**
3. Update `NEXT_PUBLIC_API_URL` to match your API URL
4. Railway will auto-redeploy

### Step 7: Run Database Migrations

1. Go to your **API service** → **Deployments**
2. Click on the latest deployment
3. Click **Logs** tab
4. Look for any errors — the API should auto-create tables on first run

If tables aren't created, you can run migrations manually:
1. Click **New** → **Empty Service**
2. Set the start command to:
   ```
   psql $DATABASE_URL -f infra/migrations/001_init.sql
   ```
3. Or use Railway's built-in database console

## Environment Variables Reference

| Variable | Service | Value |
|----------|---------|-------|
| `DATABASE_URL` | API | From Railway Postgres |
| `GEMINI_API_KEY` | API | From Google AI Studio |
| `OPENAI_API_KEY` | API | From OpenAI Platform |
| `SCRAPER_API_KEY` | API | Any random string |
| `NEXT_PUBLIC_API_URL` | Frontend | Your API service URL |

## Troubleshooting

### "Cannot connect to database"
- Make sure `DATABASE_URL` uses the **internal** Railway URL (contains `.railway.internal`)
- Don't use localhost — services talk over Railway's private network

### "Build failed"
- Check the **Deploy Logs** for the specific service
- Make sure Root Directory is set correctly (`api` or `frontend`)

### "API not found" (404)
- Make sure `NEXT_PUBLIC_API_URL` includes `https://` and no trailing slash
- Example: `https://hirebot-api.up.railway.app`

### Free Tier Limits
- $5 credit/month (~500 hours)
- Sleep after inactivity (wakes on next request, ~30s delay)
- 1GB RAM, shared CPU per service

## Useful Railway CLI Commands

```bash
# Link to project
railway link

# View logs
railway logs

# Open dashboard
railway open

# Deploy current directory
railway up
```

## Next Steps

1. Set up a custom domain (Settings → Domains)
2. Enable auto-deploy on git push
3. Add monitoring (Railway has built-in metrics)
4. Scale up when you have users
