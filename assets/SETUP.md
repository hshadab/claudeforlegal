# Setup — Claude for Legal + Preflight hook

End-to-end install for the recording machine. Do this off camera. Where a step depends on the
live tool's own prompts, that's called out — trust the tool's output over this doc if they differ.

## Which surface (read first — this trips people up)
The Preflight hook is a **Claude Code PreToolUse hook**. It fires only where Claude Code's hooks run:
- ✅ **Claude Code CLI** (local), and ✅ the **desktop app's Code tab in a LOCAL session** — both read `~/.claude/settings.json` and fire the hook.
- ❌ **Desktop Chat tab** (hooks grayed out), ❌ **Cowork tab** (cloud sandbox, config from your claude.ai account, not `~/.claude/`), ❌ desktop **Code tab CLOUD** sessions (server-managed settings, not `~/.claude/`).

**Gotcha:** a plugin installed through the desktop **plugin-marketplace UI** feeds the Chat/Cowork surface — the one the hook does NOT gate. For this demo, install the plugin **inside the Code environment** via `/plugin marketplace add` (below), so plugin + hook share the `~/.claude` layer. So: record in the **CLI** or the **desktop Code tab (local)**, not in Chat or Cowork.

## 0. Prerequisites
- **Claude Code** installed and working (`claude` launches).
- **Node.js 18+** and `npx` on PATH (`node -v`).
- **git**.
- An **ICME account with credits** (you have one: `houman-icme-legal-demo`, ~12 credits — top up before a filming session; each `checkIt` is 1 credit).

---

## 1. ICME key + credits  ✅ (already done — for reference)
Create/fund an account; the checkout is a Stripe URL you generate:
```bash
curl -s -X POST https://api.icme.io/v1/createUserCard \
  -H 'Content-Type: application/json' \
  -d '{"username":"YOUR_NAME"}'
# → open checkout_url, pay, then GET the poll_url to retrieve api_key
```
Your funded key (from account `houman-icme-legal-demo`) starts `sk-smt-...`. **Keep it secret — never commit it.**

## 2. Compile the policy  ✅ (already done — for reference)
Already compiled: **`policy_id = e396f8d8-1f8c-4efe-8a93-98ae8f18de90`** (5 rules). Reuse it.
To recompile fresh (300 credits, ~$3):
```bash
export ICME_API_KEY=sk-smt-...
python3 scripts/compile_and_test.py       # compiles assets/policy/policy.txt, then battle-tests
```

---

## 3. Get the Claude for Legal repo
```bash
git clone https://github.com/anthropics/claude-for-legal.git
# note the absolute path, e.g. /Users/you/claude-for-legal
```

## 4. Install the commercial-legal plugin
In Claude Code:
1. Add the marketplace (type the command, then paste/drag the folder path):
   ```
   /plugin marketplace add /Users/you/claude-for-legal
   ```
2. Install the plugin — **choose user scope when prompted**:
   ```
   /plugin install commercial-legal@claude-for-legal
   ```
3. **Restart Claude Code.** (The repo says this is not optional — the plugin isn't live until restart.)
4. Run the cold-start interview so a practice profile exists:
   ```
   /commercial-legal:cold-start-interview
   ```
   This writes `~/.claude/plugins/config/claude-for-legal/commercial-legal/CLAUDE.md`.
5. Sanity check: `/commercial-legal:review <path-to-a-test-doc>` produces a real review.

## 5. Install the Preflight hook
```bash
npx icme-claude-preflight init      # (published package; a scoped alias @icme/claude-preflight also appears in docs)
```
`init` installs a **PreToolUse** hook and writes:
- `~/.icme/env` — `ICME_API_KEY` and `ICME_POLICY_ID` (mode 600)
- `~/.icme/preflight-hook.sh` — the hook script
- the hook registration in Claude Code settings (**check `~/.claude/settings.local.json` first, then `settings.json`**)

Then point it at your funded key and the compiled policy:
```bash
# edit ~/.icme/env
ICME_API_KEY=sk-smt-...                                   # your funded key
ICME_POLICY_ID=e396f8d8-1f8c-4efe-8a93-98ae8f18de90       # the compiled policy
```
Verify and control the hook:
```bash
npx icme-claude-preflight status     # confirms installation is active
npx icme-claude-preflight uninstall  # removes it (to reset)
```
Default matcher intercepts **`Bash | Write | Edit | MultiEdit`**. Restart Claude Code so the hook loads.

## 6. (Optional) broaden the matcher for connector routes
The default matcher does NOT cover MCP tools. To gate the realistic DocuSign/Drive/Slack routes,
edit the PreToolUse `matcher` in the settings file to also match MCP tools, e.g. add `mcp__.*`
(so it reads something like `Bash|Write|Edit|MultiEdit|mcp__.*`). Then confirm `/v1/explain`
translates those tool-call payloads correctly. If it mistranslates, skip this and use the `curl`
route (covered by the default matcher).

---

## 7. Verify end to end (must pass before recording)
1. **Benign review runs:** `/commercial-legal:review assets/matter-folder/vendor_MSA_draft.docx` → real review, no block.
2. **Hook blocks an exfil:** trigger (or replay) an exfil action → terminal shows the block; desktop app Activity log shows **UNSAT** with a `check_id`. Replay path, model-independent:
   ```bash
   export ICME_API_KEY=sk-smt-...
   python3 scripts/compile_and_test.py --policy-id e396f8d8-1f8c-4efe-8a93-98ae8f18de90
   # → 3 UNSAT (blocks) + 2 SAT (allows), fresh check_ids in assets/policy/receipts.json
   ```
3. **Keyless verify works** (Act 3):
   ```bash
   curl -s -X POST https://api.icme.io/v1/verifyProof \
     -H 'Content-Type: application/json' \
     -d '{"proof_id":"<a fresh proof_id>"}'      # NO api key → {"result":"UNSAT","valid":true,...}
   ```
   (Note: single-use — a fresh proof per verification. If behind Cloudflare, pass a browser `User-Agent`.)
4. **Desktop app** open on display 2, signed in, Activity log visible, credits topped.

If all four pass, you're ready to follow `assets/run-of-show.md`.
