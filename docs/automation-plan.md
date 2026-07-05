# OJAS — Automation Plan

A realistic map of what can be automated end-to-end, what needs a human to set up once and then runs itself, and what genuinely requires an owner's ongoing judgment. Read this before assuming anything below "just runs" — the honest version is more useful than an inflated one.

## How to read this doc

Each item is tagged:
- **🤖 Fully automatable** — code/schedule handles it once configured; no human in the loop after setup
- **🔧 Automatable after setup** — needs a human to connect a real account/credential once, then runs on its own
- **🧑 Needs a human, ongoing** — judgment calls, legal exposure, or relationship management that shouldn't be fully delegated

---

## 1. Content Operations

| Task | Automation | Tag |
|---|---|---|
| Reseed recipes/exercises/reviews on fresh deploys | Already automatic — `server/index.js` seeds on first run if tables are empty | 🤖 |
| Add new recipes/exercises at scale | Extend the generator pools in `seedRecipes`/`seedExercises` (server/index.js) — deterministic, no manual authoring needed | 🤖 |
| New blog articles | Can draft via a scheduled prompt (e.g. a weekly trigger asking for a draft in the existing `BlogPage.jsx` format) — but a human should read before publishing anything under the brand's name | 🔧 |
| Review moderation (if real user reviews are ever added) | Automatic profanity/spam filtering is easy to add; genuine abuse/legal complaints need a person | 🔧 |

## 2. Engineering & Deployment

| Task | Automation | Tag |
|---|---|---|
| Build & deploy on push | GitHub Actions workflow: `npm ci && npm run build && npm start`, deploy to your PaaS of choice on every merge to main | 🤖 |
| Database backups | Cron job dumping the SQLite file to object storage (S3/R2/etc.) on a schedule | 🤖 |
| Uptime/error monitoring | A free tier of UptimeRobot/BetterStack pinging `/api/recipes` plus an error-tracking SDK (Sentry) in `server/index.js` | 🤖 |
| Dependency/security updates | Dependabot or Renovate opening PRs automatically; a human still reviews and merges | 🔧 |
| Responding to production incidents | Alerts can page automatically; the actual fix needs a person | 🧑 |

A ready-to-use GitHub Actions example:

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
      - run: npm run build
      # then trigger your host's deploy hook, e.g.:
      # - run: curl -X POST $DEPLOY_HOOK_URL
```

## 3. Marketing & Social

See `docs/social-automation-buffer-plan.md` for the Instagram/TikTok-specific plan. Summary:

| Task | Automation | Tag |
|---|---|---|
| Writing captions/hashtags/scripts | Already done — `docs/social-media-content-calendar.md` has 2 weeks ready; more can be generated the same way | 🤖 |
| Scheduling posts to go live | Buffer's API can auto-publish on a schedule, once a human links the real Instagram/TikTok Business accounts to Buffer via OAuth | 🔧 |
| Responding to comments/DMs | Can draft suggested replies; actually representing the brand publicly needs a person's judgment | 🧑 |
| Ad campaign spend decisions | Can generate ad copy and audience ideas (see `docs/marketing-campaigns.md`); spending real money needs a human approving budget | 🧑 |

## 4. Billing & Subscriptions

The app currently has **no real payment processor** — `/api/subscribe` just writes a plan and expiry date to SQLite. Before any of this is real:

| Task | Automation | Tag |
|---|---|---|
| Charging a card, handling renewals/refunds | Requires integrating a real processor (Razorpay, Stripe) — their webhooks can then automate renewal/expiry updates | 🔧 |
| Dunning emails on failed payment | Automatable once a processor's webhooks are wired in | 🤖 (after setup) |
| Chargebacks, disputes, refund judgment calls | Needs a human — this is real money and real customer relationships | 🧑 |
| Tax/GST compliance, business registration | Legal/financial ownership questions — not something to delegate to an AI, ever | 🧑 |

## 5. Customer Support

| Task | Automation | Tag |
|---|---|---|
| FAQ answers (plan features, how the app works) | A simple rules-based or LLM-backed FAQ bot is realistic to build | 🔧 |
| Account/billing issues | Needs access to real payment/account systems and a person accountable for the outcome | 🧑 |
| Medical questions (given the Health section) | Never automate — the app's own disclaimer says to see a real doctor; a support bot shouldn't attempt to answer these either | 🧑 |

---

## What "fully handing over the business" would actually require

To be direct about the request behind this doc: there is no real business here yet to hand over — no live payment processor, no real customer base, no live social accounts, a single hardcoded demo user. Turning this from a demo into an operating business needs a human to:

1. **Register a real legal entity** (sole proprietorship, LLC, private limited company, etc.) — an AI cannot be the legal owner of a business
2. **Open a business bank account and connect a real payment processor** — needs KYC/verification tied to a real person or entity
3. **Create and verify real social media Business accounts** (Instagram/TikTok/Meta Business Manager) — platform ToS requires a real account owner
4. **Decide on pricing, refund policy, terms of service, and privacy policy** — legal documents a human needs to stand behind
5. **Own customer relationships and support escalations** — someone accountable when something goes wrong

Once steps 1-3 exist, most of what's *inside* those systems (scheduling posts, sending renewal emails, redeploying on push, restocking a content calendar) can be automated the way this document describes. The ownership and judgment layer can't be.
