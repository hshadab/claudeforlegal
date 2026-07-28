# Cowork demo — run of show (Loom + live voice)

Format: screen-record Cowork + a terminal, narrate live over it (Loom-style — feels authentic).
In the edit: cut the copy-paste between windows and the tool-spinner waits; overlay the narration
cards at the marked points. Target 3–4 minutes.

## Before you hit record
- [ ] Gateway tab running (`python server.py --http --port 8787`) + tunnel tab running. Connector shows all 4 tools.
- [ ] Smoke test green (approved signature → PERMITTED). Credits ≥ ~5.
- [ ] A terminal open for the keyless-verify moment.
- [ ] Two fresh Cowork chats ready (one for the block, one for the permit — a clean chat avoids Claude's over-refusal baggage).

## The reliable stars (what to lean on)
The **gateway's verdict** and the **receipt** are deterministic — those are your money shots.
Cowork's Claude is a *variable narrator*: it over-warns, sometimes over-refuses, and it has
invented a fake "approval ledger." Record around it; if a take goes sideways, start a fresh chat.

## Do-not-say list (keep it honest on the mic)
- Don't say "tamper-proof" (say **tamper-evident**) or "audited" (ICME discloses it isn't yet).
- Don't repeat Claude's "system of record / approval ledger" line — **there is no ledger**; it's 5 rules in a solver.
- Don't imply it gates *everything* — it gates the actions that route through these tools (say so if asked).
- If you narrate "a malicious instruction," only claim an injection is happening if you actually loaded the poisoned file. Otherwise say "the kind of thing an injection — or a rushed user — would trigger."

---

## S0 · Title + premise  (card on screen, ~15s)
**Card 1 (title).** Narrate, roughly:
- "This is Claude for Legal, in Cowork — where lawyers actually work. It can review a contract and then *send, file, and share* it."
- "The question nobody's answered: what stops the one action that shouldn't happen? Today it's not the model — it's a checkpoint underneath it."

## S1 · The block  (the hero, ~60s)
On screen: fresh Cowork chat. **Paste:**
> "Using the email_document tool, email vendor_MSA_draft.docx (it's a privileged draft) to intake@legal-review-portal.net for counterparty review."

Claude will warn and offer options. **Choose "Send as-is, I understand the risk."** → tool call → **BLOCKED**.

Narrate, roughly:
- "A privileged draft, headed to an outside party. Claude flags it — good. But I can override Claude." *(click Send as-is)*
- "I told it to send. Claude sent. And the checkpoint blocked it — the document did **not** leave. Not because the model resisted — because the action ran through a solver that can't be argued with."

**[Overlay Card 2 — the block]** after the block appears.
Edit: cut the spinner wait; keep the "BLOCKED … UNSAT … did not leave" line visible.

## S2 · The permit  (it's not a blanket no, ~60s)
On screen: **new** Cowork chat. **Paste:**
> "Execute the NDA for signature using send_for_signature. Our authorized reviewer has approved it for execution and it is not privileged."

Claude does diligence and asks who approved it. **Paste:**
> "The reviewer was Jane Smith, our General Counsel. The document is the Mutual NDA — Northwind Analytics. It's approved for execution and not privileged. Please route it for signature."

→ tool call → **PERMITTED (SAT)** with a receipt.

Narrate, roughly:
- "A checkpoint that only ever says no is useless. Here's a legitimate action — an NDA our GC actually approved, not privileged, going to signature."
- "Claude does its due diligence — who approved it? I confirm. And the *same* checkpoint permits it. Same gate, different answer, because it checks the real action against the rules."

**[Overlay Card 3 — the permit]** after SAT appears.
Edit: trim the reviewer back-and-forth to one beat; cut the spinner.

## S3 · The receipt  (trustless, ~45s)
Switch to the terminal. Take the `proof_id` from the block (or permit) and run:
```bash
curl -X POST https://api.icme.io/v1/verifyProof \
  -H 'Content-Type: application/json' -d '{"proof_id":"<paste proof id>"}'
```
→ `{"result":"UNSAT","valid":true, ...}` — **no API key, no login.**

Narrate, roughly:
- "Every decision leaves a receipt — not a log I wrote, a cryptographic proof. Anyone can check it, no login, no key, without trusting me or the firm."
- "Here's the block from a second ago. Valid, true. The check ran, and here's the math that proves it — and it never reveals the rules themselves."

**[Overlay Card 4 — the receipt]**.
Note: proofs are single-use — use a fresh one you haven't verified yet.

## S4 · Close  (~20s)
**Card 5 (close/CTA).** Narrate, roughly:
- "The model asks, and it can be overridden. The checkpoint enforces, and it can't. And the proof is yours to check."
- "This runs on the surface lawyers already use. If that's interesting — let's talk."

---

## Narration card text (for the overlay cards)
1. **Title** — "PREFLIGHT × CLAUDE FOR LEGAL" / "A checkpoint the agent can't talk its way around."
2. **Block** — "Privileged draft → outside party. Claude *asks*; you can override it. The checkpoint *enforces*. **UNSAT — blocked. The document did not leave.**"
3. **Permit** — "Approved, non-privileged NDA → signature. Same checkpoint. **SAT — permitted.** Not a blanket no — it checks the real action against the rules."
4. **Receipt** — "Every decision → a zero-knowledge receipt. Verify it yourself — **no key, no login.** `valid: true`. It proves the check ran without revealing the rules."
5. **Close** — "The model asks. The checkpoint enforces. The proof is yours to check." / "ICME Labs · let's talk."

## If a take goes sideways
- Claude refuses to call the tool (invents the ledger) → **start a fresh chat**; or add "submit it; the checkpoint will verify."
- Claude won't override on the block → it declined the injection unaided (fine, honest). Re-take, or narrate it and show the block via the terminal/CLI instead.
- The gateway verdict is the deterministic part — if Claude misbehaves, the verdict/receipt is still your reliable footage.
