# Automating Instagram (and TikTok) Posting via Buffer

The honest version first: **I cannot post to Instagram on your behalf right now.** No AI assistant can, without you completing the account setup below — this isn't a limitation specific to this session, it's how Instagram's and Buffer's platforms are designed to work. Here's exactly what's needed, and what I've built to make the "automated" part as close to one-click as possible once you've done the human parts.

## Why this can't be fully automatic from here

1. **Instagram requires a Business or Creator account linked to a Facebook Page** to allow any third-party posting tool — a personal account can't be automated this way, by Meta's design (anti-spam/consent measure).
2. **Buffer connects to that account via OAuth**, which requires you (the account owner) to log in and approve the connection in your own browser. No API key can substitute for this — it's the point of OAuth.
3. **A Buffer API access token is generated from your own Buffer account** and is tied to your account's permissions. I don't have and shouldn't have a way to generate or use one without you providing it.

None of this is a policy choice on my part — it's literally how these platforms enforce that automation happens with the account owner's explicit, ongoing consent.

## What you'd need to do (one-time, human steps)

1. Convert/create an Instagram **Business** or **Creator** account
2. Link it to a **Facebook Page** (required by Meta for any API access)
3. Sign up for **Buffer** (buffer.com) — free tier supports a handful of scheduled posts/month, paid tiers scale up
4. In Buffer, connect the Instagram account (and TikTok, which Buffer also supports) via its "Connect a channel" flow — this is the OAuth step only you can do
5. Generate a Buffer API access token at [buffer.com/developers/api](https://buffer.com/developers/api)
6. Find your Buffer "profile ID" for the connected account (Buffer's API/dashboard shows this once connected)

## What I've built for the "automated" half

- **`docs/social-content-calendar.json`** — a structured version of the first week of `docs/social-media-content-calendar.md`, in a format a script can read directly (more days can be added the same way)
- **`scripts/schedule-social-posts.js`** — a Node.js script that reads that JSON and calls Buffer's API to queue each post. It **refuses to run** unless `BUFFER_ACCESS_TOKEN` and `BUFFER_PROFILE_IDS` are set as real environment variables — there's no fallback path that fakes success

Once you've done the six setup steps above:

```bash
BUFFER_ACCESS_TOKEN=your_real_token \
BUFFER_PROFILE_IDS=your_real_profile_id \
node scripts/schedule-social-posts.js
```

This queues the posts into Buffer's schedule — it does not bypass Buffer's own posting queue/timing, so you can review what's about to go out before it's live.

## On "Buffer AI"

Buffer has its own built-in AI Assistant (inside their app) for generating/rewriting captions — that's a feature of their product, not something I integrate with via a separate API in this script. If you want AI-assisted caption variants, either use Buffer's built-in assistant directly, or ask me to generate more caption variants into `social-content-calendar.json` the same way the first five days were written — I can keep expanding that file; I just can't make Buffer itself call out to me mid-schedule.

## Keeping this running long-term

Once real credentials exist, the actual "automation" (running the script on a schedule) can be:
- A GitHub Actions scheduled workflow (`on: schedule`, weekly) that runs `node scripts/schedule-social-posts.js` with the tokens stored as repo secrets
- Or a scheduled trigger in whatever environment you're running this session from, if you want me to re-run it periodically as new calendar entries are added

Either way, the credentials live in your infrastructure, not in a conversation with me — that's the safer pattern regardless of who's operating it.
