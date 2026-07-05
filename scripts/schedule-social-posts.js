#!/usr/bin/env node
/**
 * Schedules OJAS content-calendar posts to Buffer.
 *
 * This script does NOT run without real credentials, and running it has a
 * real effect (it schedules real posts on a real connected account). It has
 * not been executed as part of building this app — no posts have been
 * created anywhere by this codebase.
 *
 * Requirements before this does anything:
 *   1. A real Instagram Business or Creator account, linked to a Facebook Page
 *      (Instagram's API requires this — a personal account cannot be used)
 *   2. A Buffer account with that Instagram account connected via Buffer's
 *      own OAuth flow (buffer.com) — done by the account owner, not by this script
 *   3. A Buffer API access token (from https://buffer.com/developers/api),
 *      set as the BUFFER_ACCESS_TOKEN environment variable
 *   4. The Buffer "profile ID" for the connected Instagram (and/or TikTok)
 *      account, set as BUFFER_PROFILE_IDS (comma-separated if scheduling to
 *      more than one profile)
 *
 * Buffer's public API surface has changed over the years (Publish API vs.
 * newer endpoints) — check https://buffer.com/developers/api for the current
 * endpoint before relying on the exact request shape below; this script
 * targets the general "create an update" pattern Buffer has long supported.
 *
 * Usage:
 *   BUFFER_ACCESS_TOKEN=xxx BUFFER_PROFILE_IDS=yyy node scripts/schedule-social-posts.js
 */

import { readFile } from 'fs/promises';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));

const BUFFER_ACCESS_TOKEN = process.env.BUFFER_ACCESS_TOKEN;
const BUFFER_PROFILE_IDS = (process.env.BUFFER_PROFILE_IDS || '').split(',').filter(Boolean);
const BUFFER_API_BASE = 'https://api.bufferapp.com/1';

async function loadCalendar() {
  const path = join(__dirname, '../docs/social-content-calendar.json');
  const raw = await readFile(path, 'utf-8');
  return JSON.parse(raw);
}

async function scheduleUpdate(profileId, text) {
  const response = await fetch(`${BUFFER_API_BASE}/updates/create.json`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      Authorization: `Bearer ${BUFFER_ACCESS_TOKEN}`
    },
    body: new URLSearchParams({
      'profile_ids[]': profileId,
      text,
      now: 'false' // let Buffer use its queue schedule rather than posting instantly
    })
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Buffer API error (${response.status}): ${body}`);
  }

  return response.json();
}

async function main() {
  if (!BUFFER_ACCESS_TOKEN || BUFFER_PROFILE_IDS.length === 0) {
    console.error(
      'Missing BUFFER_ACCESS_TOKEN or BUFFER_PROFILE_IDS. This script intentionally ' +
      'refuses to run without them — see the header comment for setup steps.'
    );
    process.exit(1);
  }

  const calendar = await loadCalendar();
  console.log(`Loaded ${calendar.length} posts from the content calendar.`);

  for (const post of calendar) {
    const text = `${post.caption}\n\n${post.hashtags.join(' ')}`;
    for (const profileId of BUFFER_PROFILE_IDS) {
      console.log(`Scheduling day ${post.day} to profile ${profileId}...`);
      const result = await scheduleUpdate(profileId, text);
      console.log(`  -> queued, Buffer update id: ${result?.updates?.[0]?.id ?? 'unknown'}`);
    }
  }

  console.log('Done. Check your Buffer queue to confirm timing before it goes live.');
}

main().catch(err => {
  console.error('Failed to schedule posts:', err.message);
  process.exit(1);
});
