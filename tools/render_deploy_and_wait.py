"""Deploy one reviewed commit to the staging web service and wait for Render."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

API = "https://api.render.com/v1"
TERMINAL_FAILURES = {"build_failed", "update_failed", "canceled", "deactivated"}


def request(method: str, path: str, body: dict | None = None) -> dict:
    token = os.environ.get("RENDER_API_KEY", "")
    if not token:
        raise RuntimeError("RENDER_API_KEY is required")
    data = json.dumps(body).encode() if body is not None else None
    call = urllib.request.Request(
        API + path,
        data=data,
        method=method,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(call, timeout=30) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"Render API request failed status={error.code}") from None


def main() -> int:
    service_id = os.environ.get("RENDER_DEPLOY_SERVICE_ID", "") or os.environ.get("RENDER_STAGING_SERVICE_ID", "")
    commit = os.environ.get("JUDICIAL3_RELEASE_COMMIT_SHA", "").lower()
    if not service_id.startswith("srv-") or len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        print("RENDER_DEPLOY_BLOCKED reason=staging_service_or_commit_missing")
        return 2
    try:
        deploy = request("POST", f"/services/{service_id}/deploys", {"commitId": commit, "clearCache": "do_not_clear"})
        deploy_id = str(deploy.get("id", ""))
        if not deploy_id.startswith("dep-"):
            raise RuntimeError("Render API did not return a deploy id")
        print(f"RENDER_DEPLOY_CREATED id={deploy_id}")
        deadline = time.monotonic() + 1800
        while time.monotonic() < deadline:
            deploy = request("GET", f"/services/{service_id}/deploys/{deploy_id}")
            status = str(deploy.get("status", "unknown"))
            deployed_commit = str((deploy.get("commit") or {}).get("id", "")).lower()
            if deployed_commit and deployed_commit != commit:
                print(f"RENDER_DEPLOY_FAILED id={deploy_id} reason=commit_mismatch")
                return 1
            if status == "live":
                print(f"RENDER_DEPLOY_FINISHED id={deploy_id} status=live")
                return 0
            if status in TERMINAL_FAILURES:
                print(f"RENDER_DEPLOY_FAILED id={deploy_id} status={status}")
                return 1
            time.sleep(10)
        print(f"RENDER_DEPLOY_FAILED id={deploy_id} reason=timeout")
        return 1
    except Exception as error:
        print(f"RENDER_DEPLOY_FAILED reason={type(error).__name__}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
