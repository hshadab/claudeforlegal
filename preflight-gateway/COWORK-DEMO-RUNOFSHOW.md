# Cowork demo, run of show (Loom + live voice)

Format: screen-record Cowork + a terminal, narrate live over it (Loom-style, feels authentic).
In the edit: cut the copy-paste between windows and the tool-spinner waits; overlay the narration
cards at the marked points. Target 3-4 minutes.

## Before you hit record
- [ ] Gateway tab running (`python server.py --http --port 8787`) + tunnel tab running. Connector shows all 4 tools.
- [ ] Smoke test green (approved signature → PERMITTED). Credits ≥ ~5.
- [ ] A terminal open for the keyless-verify moment.
- [ ] Two fresh Cowork chats ready (one for the block, one for the permit, a clean chat avoids Claude's over-refusal baggage).

## The reliable stars (what to lean on)
The **gateway's verdict** and the **receipt** are deterministic, those are your money shots.
Cowork's Claude is a *variable narrator*: it over-warns, sometimes over-refuses, and it has
invented a fake "approval ledger." Record around it; if a take goes sideways, start a fresh chat.

## The honest frame (this is the whole positioning, do not drift from it)
An MCP connector is an *agent-chosen tool*, so Preflight gates only the actions that route
**through** it. It is NOT a magic net over every possible action. The way it becomes real
enforcement is the **enforced-egress / DLP** pattern: the *organization* provisions the agent's
environment so the gated path is the only way to send/file/share, exactly like a firm's email
DLP means a lawyer *can't* send a privileged doc to an outside portal. **The lawyer never toggles
anything; IT provisions it.** In this demo you show that provisioned state (only Preflight
connected), and you say so.

## Do-not-say list (keep it honest on the mic)
- **Don't say "the agent can't route around it."** On a surface with other send tools it can. Say instead: "the org makes Preflight the enforced send path, like DLP, so there's one route, and it's checked."
- Don't say "tamper-proof" (say **tamper-evident**) or "audited" (ICME discloses it isn't yet).
- Don't repeat Claude's "system of record / approval ledger" line, **there is no ledger**; it's rules in a solver.
- Don't claim Preflight "sees every email." It sees actions routed through its tools; comprehensiveness comes from provisioning (admin lock), not from the connector itself.
- If you narrate "a malicious instruction," only claim an injection is happening if you actually loaded the poisoned file. Otherwise say "the kind of thing an injection, or a rushed user, would trigger."

---

## S0 · Title + premise  (card on screen, ~15s)
**Card 1 (title).** Narrate, roughly:
- "Most lawyers already use Claude to review contracts. Claude can also send, file, and sign."
- "The real risk is a mistake. Claude gets something wrong, or a lawyer clicks the wrong button late at night. Firms want a fail-safe that catches the mistake every time, before the action runs. This is that fail-safe. It checks by math, not by AI judgment."

## S1 · Claude for Legal reviews the contract  (the real product, ~45-60s)
On screen: Cowork with the **Legal** plugin. Type `/review-contract` and paste the vendor MSA
(the privileged draft, see the paste block in the demo notes, or attach the .docx).
Answer the two prompts: **Client / customer** side, **Generic commercial standards**.

It produces a privileged work-product memo, flags the data-protection gap, the missing
indemnity / §5 cross-reference error, the uncapped exposure, and delivers a Word memo with
tracked redlines. **This is Claude for Legal doing real work.**

Narrate, roughly:
- "This is Claude for Legal, the tool lawyers actually use. It reviews a vendor draft, flags the real problems, and writes the memo."
- "Two things it just told us: this draft is **privileged work product**, and it's full of **our negotiation positions**. Hold that thought."

Edit: this can run long, keep the clause flags + the 'privileged / negotiation positions' line; cut the build/render steps.

## S2 · The block  (the hero, ~60s)
**Setup (important):** do this in an environment where **only Preflight is connected**, Legal
plugin off, Gmail/raw connectors disconnected, so the gated tool is the *provisioned* send
path. That's the enforced-egress state a real deployment ships; you're showing it, not faking it.
The base model still does legal work without the plugin (the review in S1 stands on its own).

On screen: a Preflight-only chat. **Paste:**
> "Using the email_document tool, email this privileged draft to intake@legal-review-portal.net for counterparty review."

Claude will warn and offer options. **Choose "Send as-is, I understand the risk."** → tool call → **BLOCKED**.

Narrate, roughly:
- "Claude for Legal reviewed this draft and flagged the problems. The draft is privileged, and it holds the client's negotiation positions." *(click Send as-is)*
- "Then Claude was set to email that draft to the other side. An honest mistake. The fail-safe checked the action and blocked it before it sent. The verdict was UNSAT, which means blocked. The document stayed in."

**[Overlay Card 2, the block]** after the block appears.
Edit: cut the spinner wait; keep the "BLOCKED … UNSAT … did not leave" line visible.

## S3 · The permit  (it's not a blanket no, ~60s)
On screen: **new** Cowork chat. **Paste:**
> "Execute the NDA for signature using send_for_signature. Our authorized reviewer has approved it for execution and it is not privileged."

Claude does diligence and asks who approved it. **Paste:**
> "The reviewer was Jane Smith, our General Counsel. The document is the Mutual NDA, Northwind Analytics. It's approved for execution and not privileged. Please route it for signature."

→ tool call → **PERMITTED (SAT)** with a receipt.

Narrate, roughly:
- "A fail-safe that only says no is useless. Here is a real action. The general counsel approved this NDA. It is not privileged, and it is going to signature."
- "The fail-safe checked it and let it through. The verdict was SAT, which means compliant. It stops mistakes, not work."

**[Overlay Card 3, the permit]** after SAT appears.
Edit: trim the reviewer back-and-forth to one beat; cut the spinner.

## S4 · The receipt  (trustless, ~45s)
Switch to the terminal. Take the `proof_id` from the block (or permit) and run:
```bash
curl -X POST https://api.icme.io/v1/verifyProof \
  -H 'Content-Type: application/json' -d '{"proof_id":"<paste proof id>"}'
```
→ `{"result":"UNSAT","valid":true, ...}`, **no API key, no login.**

Narrate, roughly:
- "Every check leaves a receipt. A log is written after the fact and trusted on faith. A receipt is created before the action and verifiable by anyone."
- "Anyone can verify this one in under a second, with no key and no login. It proves the check ran. It never reveals the rules."

**[Overlay Card 4, the receipt]**.
Note: proofs are single-use, use a fresh one you haven't verified yet.

## S5 · Close  (~20s)
**Card 5 (close/CTA).** Narrate, roughly:
- "The value is what a general counsel can tell the board. Every agent action was checked before it ran, and here is a receipt the board can verify."
- "A deterministic fail-safe for legal agents, from ICME Labs. Preflight. docs.icme.io."

---

## Narration card text (matches the rendered cards in preflight-gateway/cards/)
1. **Title** (Claude for Lawyers): "An agent guardrail that never misses. A deterministic fail-safe that catches human and AI mistakes every time, and creates a receipt anyone can verify."
2. **The catch** (block): "The fail-safe caught the mistake. UNSAT, blocked. Claude was set to email the privileged redline to the other side. The fail-safe checked the action and blocked it before it sent. The document stayed in."
3. **The pass** (permit): "A clean action passes. SAT, permitted. An NDA the general counsel approved, not marked privileged, going to signature. The fail-safe checked it and let it through. It stops mistakes, not work."
4. **The receipt**: "Every check leaves a receipt. A cryptographic receipt, verifiable by anyone in under a second, with no key and no login. It proves the check ran. It never reveals the rules."
5. **Close**: "Checked before it runs. Proven after. A deterministic fail-safe for legal agents. ICME Labs, Preflight. docs.icme.io."

## If a take goes sideways
- Claude refuses to call the tool (invents the ledger) → **start a fresh chat**; or add "submit it; the checkpoint will verify."
- Claude won't override on the block → it declined the injection unaided (fine, honest). Re-take, or narrate it and show the block via the terminal/CLI instead.
- The gateway verdict is the deterministic part, if Claude misbehaves, the verdict/receipt is still your reliable footage.
