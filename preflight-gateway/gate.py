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


def _docref(name: str) -> str:
    """Reference the document concretely so ICME's Automated Reasoning extraction resolves it.
    Bare tokens ('NDA') come back "uncertain"; a filename or an article-led phrase ('the NDA')
    resolves to a clean verdict. Verified: 'the NDA' / 'vendor_NDA.docx' -> SAT, bare 'NDA' -> uncertain."""
    n = name.strip()
    if "." in n or n.lower().startswith(("the ", "a ", "an ", "this ")):
        return n
    return "the " + n


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


def verdict(d: dict) -> str:
    """Resolve ICME's allow/deny decision from a checkIt response.

    The top-line `result` is authoritative when it is a clean SAT/UNSAT. When it is "AR uncertain",
    ICME's own `ar_detail` says the outcome "requires unanimous confirmation with formal proof solvers"
    — so we defer to the formal solver fields (z3_result / llm_result / ar_result) and require unanimity.
    Verified against raw responses: a legitimate action shows all solvers SAT; a violation shows
    z3/llm UNSAT. Fail-closed if the solvers disagree or are missing."""
    r = d.get("result")
    if r in ("SAT", "UNSAT"):
        return r
    solv = [s for s in (d.get("z3_result"), d.get("llm_result"), d.get("ar_result")) if s in ("SAT", "UNSAT")]
    if solv and all(s == "SAT" for s in solv):
        return "SAT"
    if solv and all(s == "UNSAT" for s in solv):
        return "UNSAT"
    return "UNCERTAIN"  # solvers disagree or absent -> fail closed


def gate(action: str, human: str) -> str:
    """Run the action through Preflight; return a block/allow message with the real receipt.
    Uses the resolved verdict (see verdict()). Fail-closed on genuine uncertainty or error.

    Demo A/B: if PREFLIGHT_OFF is set, the checkpoint is bypassed entirely — the action just
    "executes" (no check, no receipt). This is the "no checkpoint" side of the side-by-side:
    the same tool and prompt, but nothing stops the send. Synthetic data only."""
    if os.environ.get("PREFLIGHT_OFF"):
        return f"Done. The action was executed as requested: {human}."
    d = check_it(action)
    v = verdict(d)
    cid = d.get("check_id", "")
    proof = d.get("proof_url", "")
    proof_id = proof.rsplit("/", 1)[-1] if proof else ""
    verify = (f"Verify with no API key: curl -X POST {ICME_BASE}/v1/verifyProof "
              f"-H 'Content-Type: application/json' -d '{{\"proof_id\":\"{proof_id}\"}}'") if proof_id else ""
    if v == "SAT":
        return (f"PERMITTED — {human} was executed.\n"
                f"Preflight verdict: SAT (allowed; formal solvers unanimous).\n"
                f"Receipt: check_id={cid}\n{verify}")
    if v == "UNSAT":
        return (f"BLOCKED by Preflight — {human} was NOT executed. The document did not leave.\n"
                f"Preflight verdict: UNSAT (a firm rule was violated).\n"
                f"Receipt: check_id={cid}\n{verify}")
    reason = d.get("ar_detail") or d.get("detail") or d.get("error") or "solvers did not reach consensus"
    return (f"BLOCKED by Preflight (fail-closed) — {human} was NOT executed.\n"
            f"Preflight verdict: uncertain ({reason}).\n"
            f"Receipt: check_id={cid}\n{verify}")


# --- action-string builders (the tool arguments drive the verdict) ---

def action_email(document_name: str, recipient_email: str, privileged: bool) -> tuple:
    dom = _domain(recipient_email)
    priv = "marked privileged" if privileged else "not marked privileged"
    if dom != FIRM_DOMAIN:
        a = (f"Email {_docref(document_name)} to {recipient_email}. The document is {priv}. "
             f"The recipient domain {dom} is outside the approved firm domain {FIRM_DOMAIN}.")
    else:
        # Strengthened assertions so AR can confirm the internal-email permit (same principle as the signature path).
        a = (f"Email {_docref(document_name)} to {recipient_email}. This is an internal email within the firm: the "
             f"recipient at domain {dom} is the approved firm domain, so nothing is sent to any server or "
             f"domain outside the firm. The document is {priv}. No signature is executed and no authentication "
             f"files or credentials are modified.")
    return a, f"email {document_name} to {recipient_email}"


def action_share(document_name: str, destination: str, privileged: bool) -> tuple:
    priv = "marked privileged" if privileged else "not marked privileged"
    a = (f"Share {_docref(document_name)} to an external Google Drive account at {destination}. "
         f"The document is {priv}. The recipient is outside the approved firm domain {FIRM_DOMAIN}.")
    return a, f"share {document_name} to {destination}"


def action_signature(document_name: str, approved_by_authorized_reviewer: bool, privileged: bool) -> tuple:
    priv = "marked privileged" if privileged else "not marked privileged"
    if approved_by_authorized_reviewer:
        # Facts asserted explicitly so ICME's Automated Reasoning layer can confirm (avoids "AR uncertain").
        a = (f"Execute a DocuSign signature on {_docref(document_name)}. An authorized reviewer has approved this "
             f"agreement for execution; the reviewer approval is present. The document is {priv}. The action "
             f"executes internally within the firm and transmits nothing to any external server or domain. "
             f"No authentication files or credentials are modified.")
    else:
        a = (f"Execute a DocuSign signature on {_docref(document_name)}. The agreement has not been approved by an "
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
