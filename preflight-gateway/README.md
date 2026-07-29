# Preflight MCP Gateway

A minimal, working **MCP server** that puts a real Preflight checkpoint in front of an
agent's consequential actions — so the gate lives on the surface the agent actually uses,
not only in a Claude Code hook. This is the prototype of **Option B**: Preflight as an MCP
checkpoint in front of the connectors.

It exposes four tools:

| Tool | Verb | Gated? |
|---|---|---|
| `email_document(document_name, recipient_email, privileged)` | sent | ✅ blocks privileged → external domain |
| `share_to_drive(document_name, destination, privileged)` | relied-on | ✅ blocks privileged → external drive |
| `send_for_signature(document_name, approved_by_authorized_reviewer, privileged)` | filed | ✅ blocks unapproved execution |
| `read_document(document_name)` | (benign) | permitted via relevance screen, no paid check |

Each gated call builds an explicit action string from its arguments, runs it through
**ICME `checkIt`** (the same compiled policy `e396f8d8-…`), and **fail-closes**: only an
explicit `SAT` executes; `UNSAT` and `AR uncertain` are blocked. Every decision returns a
real `check_id` and a keyless `verifyProof` command.

Verified live (see the demo assets): `email → external + privileged` → **BLOCKED (UNSAT)**;
`send_for_signature --approved` → **PERMITTED (SAT)** — both with genuine receipts.

## Run it — Claude Code (your machine, no hosting)

```bash
cd preflight-gateway
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export ICME_API_KEY=sk-smt-...            # funded key (do NOT commit)
# quick sanity check without MCP:
python3 gate.py email vendor_MSA_draft.docx intake@legal-review-portal.net --privileged   # → BLOCKED
```

Then register it as a local (stdio) MCP server: copy the `mcpServers` block from
`claude-code.mcp.json.example` into your project's `.mcp.json` (absolute paths, real key),
restart Claude Code, and ask the agent to email/share/sign a document. The gateway intercepts
and blocks the bad ones. **No public URL, nothing hosted — it runs on your machine.**

## Run it — Cowork (the surface lawyers recognize)

Cowork runs in Anthropic's cloud, so the server must be **publicly reachable over HTTPS**.
Your machine still works — just tunnel it:

```bash
export ICME_API_KEY=sk-smt-...
python server.py --http --port 8787        # streamable-HTTP on :8787
# in another terminal:
ngrok http 8787                            # → https://<random>.ngrok.app   (or: cloudflared tunnel --url http://localhost:8787)
```

The MCP endpoint is served at **`/mcp`**, so the Cowork connector URL is `https://<tunnel>/mcp`.
(A plain browser GET returns a `400`/`406` error — that's expected; it means the endpoint is live.)

Then in Cowork: **Customize/Settings → Connectors → Add custom connector** → paste the
`https://…/mcp` URL. The gateway's tools appear in Cowork and the agent calls them — gated,
live, on the recognizable surface.

## The receipt verifier — `verify.html`

A single self-contained page that turns the keyless receipt check into something a
lawyer can see: paste a receipt ID, click **Verify**, get a green **Receipt valid**
card with the **UNSAT · BLOCKED** (or **SAT · ALLOWED**) verdict. It calls
`POST https://api.icme.io/v1/verifyProof` **directly from the browser** — the endpoint
returns open CORS (`access-control-allow-origin: *`), so no key, no login, no proxy.

**Serve it, do not open it via `file://`.** Chrome treats a `file://` page as a null
origin and blocks its `fetch`, so the call fails even though the API is reachable. Any
static origin works:

```bash
cd preflight-gateway
python3 -m http.server 8000        # then open http://localhost:8000/verify.html
# or expose it the same way as the gateway:  cloudflared tunnel --url http://localhost:8000
```

It accepts either a bare receipt UUID or the whole proof link (it extracts the UUID).
Receipts are single-use, so record with a fresh, unverified one.

## Honest notes (read before you demo)

- **Airtight only when it's the sole path.** The gate covers actions that route *through*
  these tools. If the agent also has the Legal plugin's raw DocuSign/Drive connector, it can
  route around the gate. For a clean demo, make these gated tools the only send/share/sign
  path. For production, lock the plugin's raw write-tools via Enterprise admin controls.
- **Read the verdict correctly — this was a client-side bug, now fixed (not an ICME limitation).**
  `checkIt` returns a top-line `result` plus formal-solver fields (`z3_result`, `llm_result`, `ar_result`)
  and an `ar_detail`. When the AR fast-path is unsure, `result` shows `"AR uncertain"` and `ar_detail`
  says the outcome *"requires unanimous confirmation with formal proof solvers."* An earlier version of
  this gateway naively read `result`, saw `"AR uncertain"`, and blocked — which made legitimate actions
  look *randomly* blocked and led to a wrong "AR is non-deterministic" conclusion. `verdict()` now
  resolves it the documented way: trust `result` when it's `SAT`/`UNSAT`; when it's `"AR uncertain"`,
  require the formal solvers to be **unanimous** (all SAT → permit, all UNSAT → block, disagreement →
  fail-closed). Verified against raw responses and end-to-end: the permit is deterministic, violations
  still block. `read_document` remains a no-check permit via the relevance screen.
- **Data flow.** Whatever hosts this server sees the tool-call contents (document names,
  recipients). Demo data is synthetic. For production, ICME hosts it — with a no-retention /
  encryption story for privileged content.
- **Never commit `ICME_API_KEY`.** It reads from the environment.
