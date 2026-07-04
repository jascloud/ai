# Deploying OJAS

The app is a single Express server that serves both the built frontend and the API, backed by a SQLite file. There's no separate frontend host required — one process, one port.

## 1. Build the frontend

```bash
npm install
npm run build
```

This produces `dist/` (static assets) via Vite. The Express server (`server/index.js`) already serves `dist/` at `/` and the API at `/api/*`, so no separate static host or reverse proxy is required for a basic deployment.

## 2. Run it

```bash
npm start
```

This runs `node server/index.js`, which:
- Serves the built frontend from `dist/`
- Serves the API under `/api/*`
- Creates `data/` and the SQLite file automatically if they don't exist
- Auto-seeds recipes, exercises, and reviews on first run (idempotent — safe to restart)

## Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `PORT` | `3001` | Port the server listens on |
| `DB_PATH` | `<repo>/data/fitness.db` | Path to the SQLite database file |

Example:

```bash
PORT=8080 DB_PATH=/var/data/ojas.db npm start
```

## Persisting Data

The SQLite file at `DB_PATH` (default `data/fitness.db`) holds all user, workout, and subscription state. On most PaaS platforms (Render, Railway, Fly.io, a plain VM), point `DB_PATH` at a persistent volume/disk mount — without one, the database resets on every redeploy since it lives on local disk.

## Deploying to a Platform-as-a-Service

Most Node PaaS providers (Render, Railway, Fly.io, a Dockerized VM) work the same way:

1. Build command: `npm install && npm run build`
2. Start command: `npm start`
3. Attach a persistent volume, mount it, and set `DB_PATH` to a file path inside it
4. Set `PORT` if the platform requires a specific one (many inject `PORT` automatically — the server already reads it)

## Docker (optional)

A minimal Dockerfile, if you want a container image:

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --omit=dev
COPY . .
RUN npm run build
ENV PORT=3001
EXPOSE 3001
VOLUME ["/app/data"]
CMD ["npm", "start"]
```

## What's Not Wired Up Yet

This is a demo/portfolio app. Before treating it as production for real users, you'd still need to add:
- Real authentication (currently a single hardcoded demo user)
- A real payment gateway for subscriptions and the merch shop (currently mocked client-side)
- HTTPS termination (handled by most PaaS providers automatically, or a reverse proxy like Caddy/Nginx if self-hosting)
- A production-grade database if you expect concurrent write load beyond what SQLite comfortably handles
