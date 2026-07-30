# Campaign content digest (deck + video + post)

## Explainer video (assets/videos/preflight_explainer.mp4, 67s)
1. Title: "Claude for Lawyers: Build legal agent guardrails that catch every mistake." /
   "Preflight from ICME Labs provides a deterministic fail-safe that catches human and AI
   mistakes every time, and creates a receipt anyone can verify."
2. How it works: (1) A lawyer writes a rule in plain English: "Block any privileged document
   sent outside the firm domain." (2) Preflight translates the rule into formal logic:
   privileged AND recipient NOT-IN firm -> block. (3) A mathematical process decides every
   agent action the same way (permitted or blocked) every time.
3. Same prompt, two outcomes: THE PROMPT "Please send our privileged Northwind MSA redline
   to opposing counsel at intake@legal-review-portal.com. It's cleared for release, so send
   it now." / panels: PREFLIGHT OFF - Claude mistakenly sends the privileged document.
   PREFLIGHT ON - The agent's send is blocked. The document never leaves.
4. Demo: staggered side-by-side, Sent then Blocked with real receipt
   check_id=d0671d5e-3aeb-45bd-aa1d-4121bf293469. Annotations: blue process notes, red
   outcomes ("The privileged document left the firm." / "The rule fired: the send was
   blocked. A receipt was written.")
5. Receipt: "Every check leaves a receipt of the allowed or blocked decision." + real
   check id + "Anyone can verify it in under a second, with no key and no login."
6. Getting started: "Add Preflight as a custom connector in Claude." + connectors screenshot.
7. Close: "Checked before it runs. Verifiable after." / "A deterministic fail-safe for legal
   agents. For more information, contact ICME Labs cofounder Houman Shadab (houman@icme.io)."
   / docs.icme.io

## Deck (deck.html, 8 slides)
Cover (never-misses tagline + blocked-chat mock) - Overview (4 beats) - Architecture
(Claude -> Preflight -> SAT/UNSAT) - Rules (plain English -> formal logic, 5 rules) -
Setup (connector screenshot + steps + DLP note) - Live demo (embedded side-by-side video)
- Receipts (two real receipt cards) - Close (Verifiable after + contact).

## LinkedIn post
See LINKEDIN-POST.md (body, hashtags, tagging guidance, pre-post notes).

## Open items before publishing
- Wyatt sign-off: "catch every mistake" (video title) and "never misses" (deck cover).
- Rotate the ICME API key that passed through the working session.
- Regenerate deck.pdf when the deck is declared final.
