"""Create and monitor the dedicated Render migration one-off job without printing secrets."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

API = "https://api.render.com/v1"


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
    service_id = os.environ.get("RENDER_JOB_SERVICE_ID", "") or os.environ.get("RENDER_MIGRATOR_SERVICE_ID", "")
    command = os.environ.get("JUDICIAL3_RENDER_JOB_COMMAND", "npm run db:migrate")
    allowed_commands = {"npm run db:migrate", "npx tsx tools/postgres_acceptance.ts"}
    if not service_id.startswith("srv-"):
        print("RENDER_JOB_BLOCKED reason=service_id_missing")
        return 2
    if command not in allowed_commands:
        print("RENDER_JOB_FAILED reason=command_not_allowed")
        return 2
    try:
        job = request("POST", f"/services/{service_id}/jobs", {"startCommand": command})
        job_id = str(job.get("id", ""))
        if not job_id.startswith("job-"):
            raise RuntimeError("Render API did not return a job id")
        print(f"RENDER_JOB_CREATED id={job_id}")
        deadline = time.monotonic() + 1800
        while time.monotonic() < deadline:
            job = request("GET", f"/services/{service_id}/jobs/{job_id}")
            status = str(job.get("status", "unknown"))
            if status in {"succeeded", "failed", "canceled"}:
                print(f"RENDER_JOB_FINISHED id={job_id} status={status}")
                return 0 if status == "succeeded" else 1
            time.sleep(10)
        print(f"RENDER_JOB_FAILED id={job_id} reason=timeout")
        return 1
    except Exception as error:
        print(f"RENDER_JOB_FAILED reason={type(error).__name__}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
