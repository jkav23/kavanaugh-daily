# Cloudflare Scheduler — The Kavanaugh Daily

Cloudflare runs this hourly in UTC, and the JavaScript dispatches an update only at 7 a.m. or 3 p.m. Atlantic, with 8/9 a.m. and 4/5 p.m. retries if the edition has not appeared. It verifies the live news.json date before dispatching. No homepage hosting moves: GitHub Pages remains the public site.

## Step 1 — Connect this Worker through Cloudflare

1. Open https://dash.cloudflare.com/ and go to **Workers & Pages → Create application → GitHub** (or Import Git repository).
2. Authorize Cloudflare to see the GitHub repository **jkav23/kavanaugh-daily** (choose only this repo if available).
3. Enter Worker name **kavanaugh-daily-scheduler** and Root directory **cloudflare-scheduler**.
4. Leave Build command blank if optional; use Deploy command **npx wrangler deploy** if required.
5. Deploy. The included wrangler.jsonc provisions the `0 * * * *` hourly Cron Trigger automatically; don't add a duplicate trigger manually.

## Step 2 — Authorize the Worker to trigger GitHub

1. Open https://github.com/settings/personal-access-tokens/new to create a **fine-grained** personal access token.
2. Resource owner: **jkav23**; repository access: **Only select repositories → kavanaugh-daily**.
3. Repository permission **Actions → Read and write** only. Metadata read is automatically allowed. Give the token an expiry date and plan to rotate it.
4. Copy the generated token **only** into Cloudflare: Worker → Settings → Variables and Secrets → Add → **Secret** (not Text), name **GITHUB_ACTIONS_TOKEN**, paste value, Deploy changes.
5. Do not paste the token in chat, a GitHub file, or a screenshot.

## Step 3 — Check deployment

Open your Worker URL (ending in workers.dev). It should show `"configured":true` if the secret was installed. After the next matching Atlantic hour check the Worker Logs/Cron Events and GitHub Actions: https://github.com/jkav23/kavanaugh-daily/actions/workflows/publish.yml. A Cloudflare-triggered build has event type `workflow_dispatch`.

Once a Cloudflare-triggered build is verified successful, remove the old `schedule` section from GitHub's .github/workflows/publish.yml to prevent redundant jobs, while preserving `workflow_dispatch` and `push`.

GitHub API documentation: https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event
Cloudflare Cron documentation: https://developers.cloudflare.com/workers/configuration/cron-triggers/
