# LinkedIn post body (personal profile, silent demo below)

Posting note: LinkedIn autoplays muted, so the post body carries the intro a
voiceover would. Lead with the first two lines (they show above the "see more"
fold). Keep the paragraphs short. Burn the captions into the video itself; do
not rely on LinkedIn auto-captions, there is no audio for them to read.

---

## Primary version

Most lawyers already use Claude to review contracts. The same agent can also
send, file, and sign. That last part is where the risk lives.

The risk is not a malicious AI talking its way out of a rule. It is a mistake.
Claude gets something wrong, or a lawyer clicks the wrong button late at night,
and a privileged draft is on its way to the other side.

So we built Preflight, a fail-safe that checks every agent action against your
rules before it runs. It checks by math, not by AI judgment, so the same action
gets the same answer every time. It catches the mistake whether a person made
it or the model did.

In the demo below:

Claude for Legal reviews a vendor draft and writes the memo. Real work.

A mistake tries to email that privileged draft to the other side. The fail-safe
checks the action and blocks it. UNSAT. The document stayed in.

An NDA the general counsel approved goes to signature. The fail-safe checks it
and lets it through. SAT. It stops mistakes, not work.

And every check leaves a receipt, a cryptographic proof anyone can verify in
under a second with no key and no login. It proves the check ran. It never
reveals your rules.

The value is what a general counsel can tell the board. Every agent action was
checked before it ran, and here is a receipt the board can verify.

Claude for Legal does the real work. Preflight makes sure the consequential
steps are checked. docs.icme.io.

---

## Shorter alt opening (if you want a punchier hook above the fold)

Lawyers do not lie awake worrying that an AI will outsmart a rule. They worry
about a mistake. The wrong button, late at night, and a privileged draft on its
way out the door.

(then continue from "So we built Preflight..." above)

---

## Notes before you post
- **Wyatt sign-off** is still open on "never misses" and "deterministic
  fail-safe" as capability claims. This body avoids the absolute and says
  "catches the mistake ... every time" and "the same answer every time," which
  is the honest version. Clear the stronger title language with Wyatt before it
  goes public.
- Keep the honest frame if anyone asks in the comments: Preflight checks the
  actions that route through it. Comprehensiveness comes from the org making it
  the enforced send path, the same way email DLP means a lawyer cannot send a
  privileged doc to an outside portal. The lawyer never toggles anything.
- Say tamper-evident, not tamper-proof. Do not say audited (ICME discloses it
  is not yet).
