# Renomi + n8n

Two importable workflows, from a one-shot clipper to a full channel autopilot.
Both talk to your own Renomi instance: set the base URL in the HTTP nodes to
wherever it runs (`http://localhost:8000` when n8n is on the same machine).
You need your own Gemini key on the instance and your own
[Upload-Post](https://www.upload-post.com/) account for the posting steps.

| Workflow | What it does | Credentials |
|---|---|---|
| `renomi-clip-and-notify.json` | A video URL goes in through a form, clips come back on a signed webhook. No polling. | none |
| `renomi-content-machine.json` | Your YouTube channel on autopilot: daily clipping, approval buttons in Telegram, drip-scheduled posting, weekly analytics digest. | Telegram bot |

## Shared setup

1. In n8n: **Workflows → Import from file** → pick the workflow.
2. Point the HTTP nodes at your instance. There is no credential to create:
   the API has no authentication. If you have put yours behind a gate, add a
   **Header Auth** credential for whatever it expects.
3. Open the **Clips ready (webhook)** node, copy its production URL, and paste
   it as `webhook_url` inside the **Start Renomi job** node body.
4. Optional: change `webhook_secret`. Renomi signs the webhook body with
   HMAC-SHA256 and sends it as `X-Renomi-Signature: sha256=<hex>`; verify
   it in a Code node with:

   ```javascript
   const crypto = require('crypto');
   const expected = 'sha256=' + crypto
     .createHmac('sha256', 'change-me')
     .update(JSON.stringify($json.body))
     .digest('hex');
   ```

## The Content Machine

`renomi-content-machine.json` runs your channel in four acts:

1. **Watch** — once a day it reads your channel's RSS feed
   (`https://www.youtube.com/feeds/videos.xml?channel_id=UC...`) and clips
   **one** video: the newest upload if there is one, otherwise the next
   unprocessed video from your back catalog. One video a day keeps API spend
   and machine load predictable.
2. **Approve from your phone** — every finished clip lands in Telegram with
   ✅ Publish / ❌ Skip buttons. Clips over Telegram's ~20 MB URL limit fall
   back to a link message with the same buttons.
3. **Drip-publish** — each approved clip takes the next free daily slot and is
   scheduled through `POST /api/social/post` to every account you connected in
   Renomi (TikTok, Instagram, YouTube). Approve five clips today, fill five
   days of content. The slot comes from the queue the server actually holds
   (`GET /api/social/scheduled`), so two clips approved seconds apart cannot
   book the same one.
4. **Sunday digest** — the machine reads the analytics of what it published
   (`GET /api/social/analytics/*`) and reports total impressions, per-platform
   split, and your best post of the week.

Machine-specific setup, all inside sticky notes on the canvas:

- Put your channel id in the **Channel RSS feed** node.
- Create a Telegram bot with [@BotFather](https://t.me/BotFather), add the
  `Telegram bot` credential, and replace `YOUR_TELEGRAM_CHAT_ID` in the
  notification nodes (message your bot, then check
  `api.telegram.org/bot<token>/getUpdates` for your chat id).
- Connect your social accounts in Upload-Post and set `UPLOAD_POST_API_KEY` on
  the instance — the posting step uses it directly; no extra social credentials
  in n8n.

Note: the machine remembers which videos it already processed in n8n workflow
static data, which only persists for **production** executions — test runs in
the editor won't advance it. Scheduling deliberately does *not* use that
mechanism (see act 3).

## Webhook payload

```json
{
  "event": "job.completed",
  "job_id": "…",
  "status": "completed",
  "clips": [
    { "index": 0, "title": "…", "video_url": "…", "download_url": "…" }
  ]
}
```

Failed jobs fire the same webhook with `"event": "job.failed"` and an `error`
field, so the flow never hangs waiting.

`download_url` is absent in this edition — there is no object store behind it.
Fetch `video_url` from the instance before its retention window
(`JOB_RETENTION_SECONDS`, 24h by default) expires.

## Publishing and analytics API

Direct posting: `POST /api/social/post` (accepts `scheduled_date`, ISO-8601).
Publishing queue: `GET /api/social/scheduled`, and
`DELETE /api/social/scheduled/{job_id}` to cancel one before it goes out.
Analytics of what you published: `GET /api/social/analytics` (profile totals),
`GET /api/social/analytics/posts` (per-post metrics),
`GET /api/social/analytics/impressions` (windowed totals, `period=last_week`).
Full API reference: `/docs` on your instance. Agent-native version of the same
pipeline: the MCP server at `/mcp`.
