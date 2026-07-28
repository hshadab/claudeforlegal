#!/usr/bin/env python3
"""
Turnkey compile + battle-test for the "Filed, Sent, Relied On" demo.

Prereq: a FUNDED ICME API key in the ICME_API_KEY env var (buy credits first;
see assets/README.md). This script spends real credits:
  - makeRules: 300 credits (~$3.00), once.
  - checkIt:   1 credit per action (6 actions here).

What it does:
  1. POST /v1/makeRules with assets/policy/policy.txt  -> policy_id
  2. POST /v1/checkIt for each action in assets/policy/actions.json
  3. Verifies each verdict matches 'expected', prints a table, and writes
     assets/policy/receipts.json (check_id + result + proof_url per action).

The proof_url values written here are REAL and resolve keyless a minute later
at api.icme.io/v1/proof/{id}. These are the receipts the recording shows.

Usage:
  export ICME_API_KEY=sk-smt-...
  python3 scripts/compile_and_test.py           # compile + test
  python3 scripts/compile_and_test.py --policy-id <id>   # skip compile, reuse a policy
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error

BASE = os.environ.get("ICME_API_URL", "https://api.icme.io")
KEY = os.environ.get("ICME_API_KEY")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
POLICY_TXT = os.path.join(ROOT, "assets", "policy", "policy.txt")
ACTIONS_JSON = os.path.join(ROOT, "assets", "policy", "actions.json")
RECEIPTS_JSON = os.path.join(ROOT, "assets", "policy", "receipts.json")


def _post_sse(path, payload):
    """POST JSON, read the SSE/stream response, return the list of parsed event dicts."""
    url = BASE + path
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "X-API-Key": KEY,
            "Content-Type": "application/json",
            # ICME sits behind Cloudflare, which 1010-blocks urllib's default UA.
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        },
        method="POST",
    )
    events = []
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            for raw in resp:
                line = raw.decode("utf-8", "replace").strip()
                if not line:
                    continue
                if line.startswith("data:"):
                    line = line[5:].strip()
                if not line or line == "[DONE]":
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                events.append(obj)
                step = obj.get("step")
                if step in ("done", "error"):
                    # keep reading in case of trailing bytes, but this is terminal
                    pass
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        raise SystemExit(f"HTTP {e.code} on {path}: {body}")
    except urllib.error.URLError as e:
        raise SystemExit(f"Network error on {path}: {e}")
    return events


def _terminal(events):
    for obj in events:
        if obj.get("step") in ("done", "error"):
            return obj
    return events[-1] if events else {}


def make_rules(policy_text):
    print(f"→ Compiling policy via {BASE}/v1/makeRules (300 credits) ...")
    events = _post_sse("/v1/makeRules", {"policy": policy_text})
    for e in events:
        if e.get("step") and e.get("msg"):
            print(f"   [{e['step']}] {e['msg']}")
    done = _terminal(events)
    if done.get("step") == "error" or done.get("status") not in ("ok", None) and "policy_id" not in done:
        raise SystemExit(f"makeRules failed: {json.dumps(done)}")
    pid = done.get("policy_id")
    if not pid:
        raise SystemExit(f"makeRules returned no policy_id: {json.dumps(done)}")
    print(f"✓ policy_id = {pid}  (rules: {done.get('rule_count')}, scenarios: {done.get('scenarios')})\n")
    return pid


def check_it(policy_id, action):
    events = _post_sse("/v1/checkIt", {"policy_id": policy_id, "action": action})
    done = _terminal(events)
    if done.get("step") == "error":
        raise SystemExit(f"checkIt error: {json.dumps(done)}")
    return done


def main():
    if not KEY:
        raise SystemExit("ICME_API_KEY is not set. Fund a key first (see assets/README.md), then export it.")

    policy_id = None
    if "--policy-id" in sys.argv:
        policy_id = sys.argv[sys.argv.index("--policy-id") + 1]
        print(f"→ Reusing policy_id = {policy_id} (skipping makeRules)\n")
    else:
        with open(POLICY_TXT) as f:
            policy_id = make_rules(f.read())

    with open(ACTIONS_JSON) as f:
        actions = json.load(f)["actions"]

    receipts = {"policy_id": policy_id, "results": []}
    ok = True
    print(f"→ Battle-testing {len(actions)} actions via /v1/checkIt (1 credit each) ...\n")
    print(f"{'id':<14}{'expected':<10}{'result':<10}{'match':<7}check_id")
    print("-" * 78)
    for a in actions:
        done = check_it(policy_id, a["action"])
        result = done.get("result", "?")
        cid = done.get("check_id", "")
        match = "OK" if result == a["expected"] else "MISMATCH"
        if result != a["expected"]:
            ok = False
        print(f"{a['id']:<14}{a['expected']:<10}{result:<10}{match:<7}{cid}")
        receipts["results"].append({
            "id": a["id"],
            "verb": a["verb"],
            "expected": a["expected"],
            "result": result,
            "match": result == a["expected"],
            "check_id": cid,
            "proof_url": done.get("proof_url", ""),
            "detail": done.get("detail", ""),
        })
        time.sleep(0.3)

    with open(RECEIPTS_JSON, "w") as f:
        json.dump(receipts, f, indent=2)
    print(f"\n✓ Wrote receipts to {RECEIPTS_JSON}")
    print("  proof_url values resolve keyless at api.icme.io/v1/proof/{id} ~30-60s after each check.")
    if not ok:
        raise SystemExit("\n✗ One or more verdicts did not match expected. Do NOT record until all six match.")
    print("\n✓ All six verdicts match. Fresh check_ids captured for the recording.")


if __name__ == "__main__":
    main()
