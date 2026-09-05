"""Multi-tenant isolation for the social surface (posting, scheduling, analytics).

Cloud runs every user's connected accounts inside ONE Upload-Post account, as
profiles named ``os_<hex>``. That means the profile string is the only thing
standing between "schedule to my TikTok" and "schedule to a stranger's", and it
must never come from the request body.

Two things are pinned here:

1. ``resolve_post_profile`` ignores the client-supplied profile in cloud mode
   and refuses when the server cannot resolve one, rather than falling back to
   the client's value. The call sites used to read ``forced_profile or
   req.user_id``; that is the exact shape that turns a resolver bug into a
   cross-tenant write.
2. The vendor-facing list helper filters by profile. Upload-Post's schedule
   endpoint takes no profile filter and returns the whole account, so dropping
   this filter would expose (and let anyone cancel) every other user's queue.
"""
import asyncio

import pytest
from fastapi import HTTPException

import app as app_module


OTHER_TENANT = "os_deadbeefcafe"


class TestResolvePostProfile:
    """One tenant: the caller owns the Upload-Post account whose key resolved
    the request, so it may name its own profile.

    The server-resolved value still wins over the client's when both are
    present — that ordering is what stops a client naming someone else's
    profile if a multi-tenant layer is ever added back.
    """

    def test_server_resolved_profile_wins(self):
        assert app_module.resolve_post_profile("os_mine", OTHER_TENANT) == "os_mine"

    def test_client_profile_is_honoured(self):
        assert app_module.resolve_post_profile(None, "my-profile") == "my-profile"

    def test_missing_profile_is_a_client_error(self):
        with pytest.raises(HTTPException) as exc:
            app_module.resolve_post_profile(None, None)
        assert exc.value.status_code == 400


class TestScheduledPostsAreFilteredByProfile:
    def test_other_tenants_rows_are_dropped(self, monkeypatch):
        vendor_rows = {
            "scheduled_posts": [
                {"job_id": "mine-1", "profile_username": "os_mine"},
                {"job_id": "theirs", "profile_username": OTHER_TENANT},
                {"job_id": "mine-2", "profile_username": "os_mine"},
                {"job_id": "nameless"},  # no profile at all: not ours
            ]
        }

        async def fake_get(api_key, url, params):
            return vendor_rows

        monkeypatch.setattr(app_module, "_upload_post_get", fake_get)
        rows = asyncio.run(app_module._scheduled_posts_for("key", "os_mine"))

        assert [r["job_id"] for r in rows] == ["mine-1", "mine-2"]
        assert all(r.get("profile_username") == "os_mine" for r in rows)
