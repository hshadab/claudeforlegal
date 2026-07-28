import os, subprocess, glob

OUT = "/home/user/claudeforlegal/preflight-gateway/cards"
os.makedirs(OUT, exist_ok=True)
CHROME = sorted(glob.glob("/opt/pw-browsers/chromium*/chrome-linux/chrome"))[0]

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
html,body{margin:0;background:#070f2b}
.card{width:1280px;height:720px;position:relative;overflow:hidden;
  background:radial-gradient(120% 120% at 80% -10%, #0d1c48 0%, #0A1535 48%, #070f2b 100%);
  font-family:'Inter',system-ui,sans-serif;padding:80px 90px;display:flex;flex-direction:column;justify-content:center}
.kicker{font:600 20px/1 'Oswald',sans-serif;letter-spacing:.34em;text-transform:uppercase;color:#7BA5FF;margin-bottom:28px}
.kicker.red{color:#fa3246}.kicker.grn{color:#5ED9A1}
h1{font:600 62px/1.06 'Oswald',sans-serif;color:#fff;letter-spacing:-.01em;max-width:1040px}
h1 .em{color:#7BA5FF}.h1red{color:#fa3246}.h1grn{color:#5ED9A1}
.chip{display:inline-block;margin-top:30px;padding:12px 22px;border-radius:8px;font:700 22px/1 'Oswald',sans-serif;letter-spacing:.06em}
.chip.red{background:rgba(250,50,70,.12);border:1px solid #fa3246;color:#ff8794}
.chip.grn{background:rgba(94,217,161,.12);border:1px solid #5ED9A1;color:#5ED9A1}
.chip.mono{background:rgba(123,165,255,.10);border:1px solid #7BA5FF;color:#cfe0ff;font-family:'JetBrains Mono',monospace;font-size:24px;font-weight:500;letter-spacing:0}
.sub{font:400 27px/1.5 'Inter',sans-serif;color:#9db4e6;max-width:960px;margin-top:30px}
.sub b{color:#e8eeff;font-weight:600}
.wm{position:absolute;left:90px;bottom:46px;font:600 18px/1 'Oswald',sans-serif;letter-spacing:.28em;color:#7BA5FF}
.wm span{color:#6b81b8}
.cta{position:absolute;right:90px;bottom:44px;font:500 18px/1 'JetBrains Mono',monospace;color:#9db4e6}
"""

CARDS = [
    dict(name="1-title", kc="", kicker="Preflight × Claude for Legal",
         h1='A checkpoint the agent<br>can’t <span class="em">talk its way around.</span>',
         chip="", sub='Runs underneath Claude for Legal, on the surface lawyers actually use.'),
    dict(name="2-block", kc="red", kicker="The block",
         h1='Claude <span class="em">asks.</span><br>The checkpoint <span class="h1red">enforces.</span>',
         chip='<div class="chip red">UNSAT · BLOCKED</div>',
         sub='A privileged draft, headed to an outside party. You can override Claude — you <b>cannot</b> override the checkpoint. The document did not leave.'),
    dict(name="3-permit", kc="grn", kicker="The permit",
         h1='Same checkpoint.<br><span class="h1grn">Different answer.</span>',
         chip='<div class="chip grn">SAT · PERMITTED</div>',
         sub='An approved, non-privileged NDA going to signature. Not a blanket no — it checks the <b>real action</b> against the rules.'),
    dict(name="4-receipt", kc="", kicker="The receipt",
         h1='Verify it yourself.<br><span class="em">No key. No login.</span>',
         chip='<div class="chip mono">valid: true</div>',
         sub='Every decision leaves a zero-knowledge proof. Anyone can check it — without trusting me or the firm — and it <b>never reveals the rules</b>.'),
    dict(name="5-close", kc="", kicker="",
         h1='The model asks.<br>The checkpoint <span class="em">enforces.</span><br>The proof is <span class="em">yours to check.</span>',
         chip="", sub='ICME Labs — Preflight for agent accountability.'),
]

for c in CARDS:
    kc = (" " + c["kc"]) if c["kc"] else ""
    kicker = f'<div class="kicker{kc}">{c["kicker"]}</div>' if c["kicker"] else ""
    cta = '<div class="cta">docs.icme.io · let’s talk</div>' if c["name"]=="5-close" else ""
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head>
<body><div class="card">{kicker}<h1>{c['h1']}</h1>{c['chip']}<div class="sub">{c['sub']}</div>
<div class="wm">ICME <span>LABS</span></div>{cta}</div></body></html>"""
    hp = f"/tmp/card_{c['name']}.html"
    open(hp, "w").write(html)
    png = f"{OUT}/demo-card-{c['name']}.png"
    subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--hide-scrollbars",
                    "--force-device-scale-factor=1", "--window-size=1280,720",
                    f"--screenshot={png}", f"file://{hp}"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("rendered", png)
print("done")
