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

Then in Cowork: **Settings → Connectors → Add custom connector** → paste the `https://…`
tunnel URL. The gateway's tools appear in Cowork and the agent calls them — gated, live, on
the recognizable surface.

## Honest notes (read before you demo)

- **Airtight only when it's the sole path.** The gate covers actions that route *through*
  these tools. If the agent also has the Legal plugin's raw DocuSign/Drive connector, it can
  route around the gate. For a clean demo, make these gated tools the only send/share/sign
  path. For production, lock the plugin's raw write-tools via Enterprise admin controls.
- **Fail-closed can false-positive.** Benign actions that come back `AR uncertain` (the solver
  says Satisfiable but ICME's Automated Reasoning abstains) are blocked. Use well-formed action
  assertions for the permit beat; the approved-signature path passes cleanly.
- **Data flow.** Whatever hosts this server sees the tool-call contents (document names,
  recipients). Demo data is synthetic. For production, ICME hosts it — with a no-retention /
  encryption story for privileged content.
- **Never commit `ICME_API_KEY`.** It reads from the environment.
