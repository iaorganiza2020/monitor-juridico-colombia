"""Run the private Site monitor from GitHub Actions; standard library only."""

import hashlib
import hmac
import json
import os
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


SITE_URL = "https://juez-cabron-colombia-mcp.jabalo2025.chatgpt.site"


def main() -> int:
    access_token = os.environ.get("SITE_ACCESS_TOKEN", "")
    job_secret = os.environ.get("MONITOR_JOB_SECRET", "")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "")
    event = os.environ.get("GITHUB_EVENT_NAME", "")
    if not access_token or not job_secret:
        print("Faltan secretos SITE_ACCESS_TOKEN o MONITOR_JOB_SECRET.", file=sys.stderr)
        return 1
    if not run_id.isdecimal() or not attempt.isdecimal() or event not in ("schedule", "workflow_dispatch"):
        print("Contexto GitHub Actions inválido.", file=sys.stderr)
        return 1

    dispatch_id = f"{run_id}-{attempt}"
    body = json.dumps({"dispatch_id": dispatch_id, "trigger": event}, separators=(",", ":")).encode()
    for trial in range(1, 4):
        timestamp = str(int(time.time()))
        signature = hmac.new(job_secret.encode(), timestamp.encode() + b"." + body, hashlib.sha256).hexdigest()
        request = Request(
            SITE_URL + "/api/internal/monitor/run",
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "OAI-Sites-Authorization": "Bearer " + access_token,
                "X-Monitor-Timestamp": timestamp,
                "X-Monitor-Signature": "sha256=" + signature,
            },
        )
        try:
            with urlopen(request, timeout=300) as response:
                payload = json.load(response)
                if payload.get("run_id") and payload.get("status") in ("partial", "succeeded"):
                    print(json.dumps({"dispatch_id": dispatch_id, "run_id": payload["run_id"], "status": payload["status"], "trigger": event}))
                    return 0
                if response.status == 202 and trial < 3:
                    time.sleep(10)
                    continue
                print("La respuesta no confirma una ejecución terminada: " + json.dumps(payload), file=sys.stderr)
                return 1
        except HTTPError as exc:
            # Never log headers: they contain service credentials.
            print(f"Intento {trial}: HTTP {exc.code} del Site privado.", file=sys.stderr)
            if exc.code not in (429, 500, 502, 503, 504) or trial == 3:
                return 1
        except URLError as exc:
            print(f"Intento {trial}: error de conexión: {exc.reason}", file=sys.stderr)
            if trial == 3:
                return 1
        time.sleep(5 * trial)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
