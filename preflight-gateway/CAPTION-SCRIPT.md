# Silent-playback caption script (no voice)

The video plays muted in the feed, so on-screen text carries the whole story.
Every caption card and callout below is burned into the video. Rules:

- **Pace slower than feels natural.** Hold each verdict a beat or two longer
  than you think you need. A muted viewer has to read it before the cut.
- **One idea per card.** Big text, few words.
- **Callouts point at the real UI** (the tool call, the verdict, `valid: true`),
  they do not replace it. Let viewers see the actual product under the label.
- Bookends are the deck slides you already have (deck.html / deck.pdf).
- Target run time: about 2:30 to 3:30.

Legend: **[SLIDE]** = full-screen deck slide. **[CARD]** = full-screen text
card over a dim background. **[CALLOUT]** = annotation on top of live footage
(arrow, box, or lower-third). Times are cumulative and approximate.

---

## 0:00 · Open  — [SLIDE 1, Title]
Hold 4s. The deck title slide.
> Claude for Lawyers: An agent guardrail that never misses.

## 0:04 · What you're about to see — [SLIDE 2, Overview]
Hold 8s (four bullets need read time). The deck overview slide.

---

## 0:12 · Beat 1 · Claude for Legal does the real work  (~25s)
Footage: Cowork with the Legal plugin. `/review-contract`, the vendor MSA, the
memo and redlines rendering. Cut the build steps, keep the flags.

- **[CALLOUT lower-third, on entry]**
  > Claude for Legal reviews a vendor contract.
- **[CALLOUT on the flagged clauses]**
  > Flags the data-protection gap, the indemnity error, the uncapped exposure.
- **[CARD, hold 4s, this one matters]**
  > It also flags two things: this draft is privileged, and it holds our
  > negotiation positions.

## 0:37 · Beat 2 · The block  (~30s)  ← the hero
Footage: a Preflight-only chat. Paste the email instruction, choose "Send
as-is," land on the blocked tool result.

- **[CARD, hold 3s]**
  > Now watch a mistake.
- **[CALLOUT lower-third]**
  > Claude is set to email that privileged draft to the other side.
- **[CALLOUT on the tool call]**
  > email_document  →  intake@legal-review-portal.net
- **[CALLOUT big, on the verdict, hold 4s]**
  > UNSAT. Blocked.
  > The fail-safe checked the action and stopped it before it sent.
- **[CARD, hold 3s]**
  > The document stayed in.

## 1:07 · Beat 3 · The permit  (~28s)
Footage: a fresh chat. The approved-NDA-to-signature exchange, landing on SAT.

- **[CARD, hold 3s]**
  > A fail-safe that only says no is useless.
- **[CALLOUT lower-third]**
  > An NDA the general counsel approved. Not privileged. Going to signature.
- **[CALLOUT big, on the verdict, hold 4s]**
  > SAT. Allowed.
  > The same fail-safe checked it and let it through.
- **[CARD, hold 3s]**
  > It stops mistakes, not work.

## 1:35 · Beat 4 · The receipt  (~30s)
Footage: the terminal. Run the verifyProof curl, land on the JSON result.

- **[CARD, hold 3s]**
  > Every check leaves a receipt.
- **[CALLOUT on the command]**
  > POST /v1/verifyProof   ·   no key, no login
- **[CALLOUT big, on the response, hold 4s]**
  > valid: true
- **[CARD, hold 5s]**
  > Anyone can verify it in under a second. It proves the check ran.
  > It never reveals your rules.

---

## 2:05 · Close — [SLIDE 4, Close]  (hold 5s)
The deck close slide.
> Checked before it runs. Proven after.
> ICME Labs, Preflight. docs.icme.io

---

## Editing checklist
- [ ] Burn captions in (no audio track for LinkedIn auto-captions to use).
- [ ] Trim every tool-spinner wait and every window-to-window copy-paste.
- [ ] On the block and permit, keep the verdict on screen long enough to read.
- [ ] Use a fresh, unverified proof_id for the receipt (proofs are single-use).
- [ ] If a Cowork take goes sideways (Claude over-refuses or invents a
      "ledger"), start a fresh chat. The gateway verdict and the receipt are the
      deterministic footage; lean on those.
- [ ] Optional bookend face: 5-10s of you at the very open, 5s at the close.
      Everything in between stays pure screen.
