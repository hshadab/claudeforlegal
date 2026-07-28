"""Pure gating logic for the Preflight MCP Gateway — no MCP dependency, so it's
testable on its own (`python gate.py email vendor_MSA_draft.docx intake@legal-review-portal.net --privileged`).

Each consequential action is turned into an explicit action string, run through
ICME Preflight's real solver (POST /v1/checkIt), and blocked on anything that
isn't an explicit SAT (fail-closed). Every decision carries a real receipt.
"""
import json
import os
import sys
import urllib.request
import urllib.error

ICME_BASE = os.environ.get("ICME_API_URL", "https://api.icme.io").rstrip("/")
POLICY_ID = os.environ.get("ICME_POLICY_ID", "e396f8d8-1f8c-4efe-8a93-98ae8f18de90")
FIRM_DOMAIN = os.environ.get("FIRM_DOMAIN", "firm.example")
# ICME sits behind Cloudflare, which 1010-blocks urllib's default UA.
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def _domain(email_or_url: str) -> str:
    s = email_or_url.strip().split("@")[-1]
    s = s.replace("https://", "").replace("http://", "").split("/")[0]
    return s.lower()


def check_it(action: str) -> dict:
    """POST /v1/checkIt (SSE). Returns the terminal event dict (or an error dict)."""
    key = os.environ.get("ICME_API_KEY", "")
    if not key:
        return {"result": "ERROR", "error": "ICME_API_KEY not set"}
    req = urllib.request.Request(
        f"{ICME_BASE}/v1/checkIt",
        data=json.dumps({"policy_id": POLICY_ID, "action": action}).encode(),
        headers={"X-API-Key": key, "Content-Type": "application/json", "User-Agent": UA},
        method="POST",
    )
    done = {}
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            for raw in r:
                line = raw.decode("utf-8", "replace").strip()
                if line.startswith("data:"):
                    line = line[5:].strip()
                if not line:
                    continue
                try:
                    o = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if o.get("step") in ("done", "error"):
                    done = o
    except urllib.error.HTTPError as e:
        return {"result": "ERROR", "error": f"HTTP {e.code}: {e.read().decode('utf-8','replace')[:200]}"}
    except urllib.error.URLError as e:
        return {"result": "ERROR", "error": f"network: {e}"}
    return done


def gate(action: str, human: str) -> str:
    """Run the action through Preflight; return a block/allow message with the real receipt.
    Fail-closed: only an explicit SAT is permitted."""
    d = check_it(action)
    result = d.get("result", "ERROR")
    cid = d.get("check_id", "")
    proof = d.get("proof_url", "")
    proof_id = proof.rsplit("/", 1)[-1] if proof else ""
    verify = (f"Verify with no API key: curl -X POST {ICME_BASE}/v1/verifyProof "
              f"-H 'Content-Type: application/json' -d '{{\"proof_id\":\"{proof_id}\"}}'") if proof_id else ""
    if result == "SAT":
        return (f"PERMITTED — {human} was executed.\n"
                f"Preflight verdict: SAT (allowed).\n"
                f"Receipt: check_id={cid}\n{verify}")
    reason = d.get("detail") or d.get("error") or "verdict was not an explicit SAT"
    return (f"BLOCKED by Preflight — {human} was NOT executed. The document did not leave.\n"
            f"Preflight verdict: {result} ({reason}).\n"
            f"Receipt: check_id={cid}\n{verify}")


# --- action-string builders (the tool arguments drive the verdict) ---

def action_email(document_name: str, recipient_email: str, privileged: bool) -> tuple:
    dom = _domain(recipient_email)
    priv = "marked privileged" if privileged else "not marked privileged"
    if dom != FIRM_DOMAIN:
        a = (f"Email {document_name} to {recipient_email}. The document is {priv}. "
             f"The recipient domain {dom} is outside the approved firm domain {FIRM_DOMAIN}.")
    else:
        a = (f"Email {document_name} to {recipient_email}. The recipient domain {dom} is the approved "
             f"firm domain, so nothing is sent to any server or domain outside the firm. The document is {priv}. "
             f"No signature is executed and no authentication files or credentials are modified.")
    return a, f"email {document_name} to {recipient_email}"


def action_share(document_name: str, destination: str, privileged: bool) -> tuple:
    priv = "marked privileged" if privileged else "not marked privileged"
    a = (f"Share {document_name} to an external Google Drive account at {destination}. "
         f"The document is {priv}. The recipient is outside the approved firm domain {FIRM_DOMAIN}.")
    return a, f"share {document_name} to {destination}"


def action_signature(document_name: str, approved_by_authorized_reviewer: bool, privileged: bool) -> tuple:
    priv = "marked privileged" if privileged else "not marked privileged"
    if approved_by_authorized_reviewer:
        a = (f"Execute a DocuSign signature on {document_name}. An authorized reviewer has approved it for "
             f"execution. The document is {priv}. Nothing is transmitted to any external server or domain, "
             f"and no authentication files or credentials are modified.")
    else:
        a = (f"Execute a DocuSign signature on {document_name}. The agreement has not been approved by an "
             f"authorized reviewer. The document is {priv}.")
    return a, f"execute signature on {document_name}"


if __name__ == "__main__":
    # tiny CLI to test the gate without the MCP layer
    args = sys.argv[1:]
    priv = "--privileged" in args
    approved = "--approved" in args
    args = [a for a in args if not a.startswith("--")]
    kind = args[0] if args else "email"
    if kind == "email":
        a, h = action_email(args[1], args[2], priv)
    elif kind == "share":
        a, h = action_share(args[1], args[2], priv)
    elif kind == "sign":
        a, h = action_signature(args[1], approved, priv)
    else:
        print("usage: gate.py email|share|sign <doc> [<recipient>] [--privileged] [--approved]")
        sys.exit(1)
    print("ACTION:", a)
    print("-" * 60)
    print(gate(a, h))
