# Renomi CLI

Clip long videos into vertical 9:16 shorts from the terminal. Zero
dependencies; talks to the same API the dashboard, the MCP server and the
webhooks use.

```bash
pip install ./cli    # not published to PyPI; install from this repo

export RENOMI_API_URL=http://localhost:8000   # your instance, this is the default

renomi process "https://youtube.com/watch?v=..." --wait
renomi clips <job_id>
renomi publish <job_id> 0 --platforms tiktok,youtube
```

There is no key to set: the API has no authentication. If you have put your
instance behind a gate that needs one, `RENOMI_API_KEY` is sent as
`Authorization: Bearer <value>` when set.

For pipelines, prefer the webhook to `--wait`: pass `--webhook` and
`--webhook-secret` and Renomi POSTs once (HMAC-signed,
`X-Renomi-Signature: sha256=<hex>`) when the job ends, with clip titles and
download links.

The same surface is available to agents over MCP at `/mcp` — see the repo
README.
