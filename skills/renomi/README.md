# Renomi as an Agent Skill

`SKILL.md` plus `reference.md` are an
[Agent Skill](https://github.com/agentskills/agentskills): an open standard
adopted by 26+ agent products, so this one folder installs in Claude Code,
OpenClaw, Hermes, Codex, Gemini CLI, Cursor and VS Code without changes.

It teaches an agent to turn a long video into vertical 9:16 clips through the
Renomi API: which options actually produce good clips, which responses look
like errors but are not, and when to stop and ask the user.

## Setup

Run a Renomi instance and point the agent at it with `RENOMI_API_URL`
(default `http://localhost:8000`). There is no API key: the instance has no
authentication, so whatever can reach it can use it. You need your own Google
Gemini key on the instance, and an [Upload-Post](https://www.upload-post.com/)
account for the publishing steps.

If the host speaks MCP, add the server too so the agent gets typed tools instead
of raw HTTP:

```bash
claude mcp add --transport http renomi http://localhost:8000/mcp
```

The skill works either way: with MCP it calls the tools, without it it calls the
REST API documented in `reference.md`.

## Install

**Claude Code.** Copy the folder into `~/.claude/skills/` for every project, or
a project's `.claude/skills/` for one:

```bash
cp -r skills/renomi ~/.claude/skills/
```

**OpenClaw.** Copy it into your OpenClaw `skills/` directory, or install from
git with `openclaw add <owner>/<repo>`.

**Hermes.** Skills live in `~/.hermes/skills/`; installing from the marketplace
runs a security scan first.

**Anything else.** Drop the folder wherever that agent reads skills from.

## Related

- `cli/` is the same API as a zero-dependency CLI: `renomi process <url> --wait`.
- `examples/n8n/` has the same pipeline as importable n8n workflows, including a
  daily channel autopilot with Telegram approval.
- `http://localhost:8000/docs` on a running instance is the full API reference.
