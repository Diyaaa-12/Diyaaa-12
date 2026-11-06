"""Render the profile design into animated SVG panels for README.md.

GitHub strips <style>, <script> and custom fonts from READMEs, so each part of
the design is drawn as an SVG <foreignObject> holding the original HTML + CSS,
with the fonts embedded. The contribution heatmap uses live GitHub data.

Usage:  python build/build.py            (needs GITHUB_TOKEN for the heatmap)
        python build/build.py --preview  (also writes build/preview.html)
"""
import base64, json, os, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
USER = "Diyaaa-12"
W = 760  # .page max-width from the design

# Panel heights in px, measured from the design rendered at 760px wide.
H = {"top": 300, "pill-linkedin": 37, "pill-github": 37, "pill-email": 37, "body": 1500, "footer": 64}
PILL_W = {"pill-linkedin": 104, "pill-github": 96, "pill-email": 88}  # incl. 10px gap
if (ROOT / "build" / "sizes.json").exists():
    s = json.loads((ROOT / "build" / "sizes.json").read_text())
    H.update(s.get("H", {})); PILL_W.update(s.get("PILL_W", {}))


FONTS_FOR = {"top": "srim", "body": "srim", "footer": "m"}  # s=sans r=serif i=serif italic m=mono; pills default to sans


def font_face(which="srim"):
    f = ASSETS / "fonts"
    b64 = lambda n: base64.b64encode((f / n).read_bytes()).decode()
    faces = {"r": f"""@font-face{{font-family:'Instrument Serif';font-style:normal;font-weight:400;src:url(data:font/woff2;base64,{b64('instrument-serif-regular.woff2')}) format('woff2');}}""",
             "i": f"""@font-face{{font-family:'Instrument Serif';font-style:italic;font-weight:400;src:url(data:font/woff2;base64,{b64('instrument-serif-italic.woff2')}) format('woff2');}}""",
             "s": f"""@font-face{{font-family:'DM Sans';font-style:normal;font-weight:300 500;src:url(data:font/woff2;base64,{b64('dm-sans-var.woff2')}) format('woff2');}}""",
             "m": f"""@font-face{{font-family:'DM Mono';font-style:normal;font-weight:400;src:url(data:font/woff2;base64,{b64('dm-mono-400.woff2')}) format('woff2');}}"""}
    return "".join(faces[c] for c in which)
    return f"""
@font-face{{font-family:'Instrument Serif';font-style:normal;font-weight:400;src:url(data:font/woff2;base64,{b64('instrument-serif-regular.woff2')}) format('woff2');}}
@font-face{{font-family:'Instrument Serif';font-style:italic;font-weight:400;src:url(data:font/woff2;base64,{b64('instrument-serif-italic.woff2')}) format('woff2');}}
@font-face{{font-family:'DM Sans';font-style:normal;font-weight:300 500;src:url(data:font/woff2;base64,{b64('dm-sans-var.woff2')}) format('woff2');}}
@font-face{{font-family:'DM Mono';font-style:normal;font-weight:400;src:url(data:font/woff2;base64,{b64('dm-mono-400.woff2')}) format('woff2');}}
"""


# ---- Design CSS (verbatim from the HTML design; :root -> .r, vw clamps fixed at desktop size) ----
LIGHT = """--bg:#faf9fc;--bg2:#f3eef9;--fg:#2a1f3d;--fg-muted:#7a6e8a;--cloud1:#e8dff5;--cloud2:#fce4f0;--cloud3:#dceeff;--cloud4:#fdecd6;
--accent:#b89fd8;--accent2:#e8a4c8;--pill-bg:rgba(184,159,216,0.14);--pill-bd:rgba(184,159,216,0.4);--card-bg:rgba(255,255,255,0.72);
--card-bd:rgba(184,159,216,0.22);--tag-bg:rgba(232,223,245,0.7);"""
DARK = """--bg:#17121f;--bg2:#1f1829;--fg:#ece7f5;--fg-muted:#9b8fb0;--cloud1:#2e1f4a;--cloud2:#3d1f38;--cloud3:#1a2a45;--cloud4:#3a2518;
--accent:#c4aae8;--accent2:#e8a4c8;--pill-bg:rgba(196,170,232,0.12);--pill-bd:rgba(196,170,232,0.3);--card-bg:rgba(30,22,46,0.8);
--card-bd:rgba(196,170,232,0.18);--tag-bg:rgba(46,31,74,0.8);"""
CSS = """
.r{--f-display:'Instrument Serif',Georgia,serif;--f-body:'DM Sans',system-ui,sans-serif;--f-mono:'DM Mono','Courier New',monospace;}
.r,.r *,.r *::before,.r *::after{box-sizing:border-box;margin:0;}
.r{background:var(--bg);color:var(--fg);font-family:var(--f-body);font-size:15px;line-height:1.65;width:__W__px;}
.hero{padding-top:64px;}
.eyebrow{font-family:var(--f-mono);font-size:11px;letter-spacing:0.18em;text-transform:uppercase;color:var(--fg-muted);margin-bottom:16px;display:flex;align-items:center;gap:10px;}
.eyebrow::before{content:'';display:inline-block;width:24px;height:1px;background:var(--accent);flex-shrink:0;}
.name{font-family:var(--f-display);font-size:72px;font-weight:400;line-height:1.08;letter-spacing:-0.02em;text-wrap:balance;color:var(--fg);margin-bottom:20px;}
.name em{font-style:italic;color:var(--accent);}
.tagline{font-size:17px;font-weight:300;color:var(--fg-muted);max-width:480px;margin-bottom:32px;line-height:1.6;}
.cursor{display:inline-block;width:2px;height:1em;background:var(--accent2);margin-left:2px;vertical-align:text-bottom;animation:blink 1.1s step-end infinite;}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0}}
.pillwrap{display:inline-block;padding-right:10px;}
.link-pill{display:inline-flex;align-items:center;gap:7px;padding:8px 16px;border-radius:100px;font-size:13px;font-weight:500;background:var(--pill-bg);border:1px solid var(--pill-bd);color:var(--fg);text-decoration:none;}
.link-pill svg{flex-shrink:0;}
.body{padding-top:56px;}
.building-card{background:var(--card-bg);border:1px solid var(--card-bd);border-radius:20px;padding:24px 28px;margin-bottom:48px;display:flex;align-items:flex-start;gap:20px;}
.building-dot{flex-shrink:0;width:10px;height:10px;border-radius:50%;background:var(--accent2);margin-top:6px;animation:pulse 2.4s ease-in-out infinite;box-shadow:0 0 0 0 rgba(232,164,200,0.4);}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(232,164,200,0.5);}70%{box-shadow:0 0 0 10px rgba(232,164,200,0);}100%{box-shadow:0 0 0 0 rgba(232,164,200,0);}}
.building-label{font-family:var(--f-mono);font-size:10px;letter-spacing:0.14em;text-transform:uppercase;color:var(--accent2);margin-bottom:4px;}
.building-title{font-family:var(--f-display);font-size:20px;font-weight:400;margin-bottom:4px;}
.building-desc{font-size:13px;color:var(--fg-muted);}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:48px;}
.card{background:var(--card-bg);border:1px solid var(--card-bd);border-radius:20px;padding:24px;}
.card-label{font-family:var(--f-mono);font-size:10px;letter-spacing:0.14em;text-transform:uppercase;color:var(--fg-muted);margin-bottom:14px;}
.tag-grid{display:flex;flex-wrap:wrap;gap:8px;}
.tag{font-family:var(--f-mono);font-size:12px;padding:5px 12px;border-radius:100px;background:var(--tag-bg);color:var(--fg);border:1px solid var(--card-bd);letter-spacing:0.03em;}
.heatmap-wrap{background:var(--card-bg);border:1px solid var(--card-bd);border-radius:20px;padding:28px;margin-bottom:48px;}
.heatmap-header{display:flex;align-items:baseline;gap:12px;margin-bottom:20px;}
.heatmap-title{font-family:var(--f-display);font-size:22px;font-weight:400;}
.heatmap-grid{display:flex;gap:3px;flex-wrap:nowrap;padding-bottom:4px;}
.heatmap-col{display:flex;flex-direction:column;gap:3px;}
.heatmap-cell{width:10px;height:10px;border-radius:2px;background:var(--bg2);flex-shrink:0;animation:cellin 0.4s both;animation-delay:calc(var(--i) * 0.3s / 371);}
@keyframes cellin{from{opacity:0}to{opacity:1}}
.heatmap-cell.e{visibility:hidden;}
.heatmap-cell[data-v="1"]{background:rgba(184,159,216,0.3);}
.heatmap-cell[data-v="2"]{background:rgba(184,159,216,0.55);}
.heatmap-cell[data-v="3"]{background:rgba(184,159,216,0.8);}
.heatmap-cell[data-v="4"]{background:var(--accent);}
.heatmap-stats{display:flex;gap:28px;margin-top:20px;flex-wrap:wrap;}
.stat-item{display:flex;flex-direction:column;gap:2px;}
.stat-n{font-family:var(--f-display);font-size:28px;font-weight:400;color:var(--fg);font-variant-numeric:tabular-nums;}
.stat-label{font-family:var(--f-mono);font-size:10px;letter-spacing:0.12em;text-transform:uppercase;color:var(--fg-muted);}
@property --n{syntax:'<integer>';initial-value:0;inherits:false;}
.count{--n:var(--t);counter-reset:n var(--n);animation:countup var(--d) ease-out 0.4s both;}
.count::after{content:counter(n);}
@keyframes countup{from{--n:0}to{--n:var(--t)}}
.contrib-list{display:flex;flex-direction:column;gap:10px;}
.contrib-item{display:flex;align-items:center;gap:12px;font-size:13px;color:var(--fg-muted);line-height:1.4;}
.contrib-item::before{content:'';flex-shrink:0;width:6px;height:6px;border-radius:50%;background:var(--accent);}
.contrib-item strong{color:var(--fg);font-weight:500;}
.section-head{font-family:var(--f-display);font-size:38px;font-weight:400;letter-spacing:-0.02em;line-height:1.1;margin-bottom:20px;text-wrap:balance;}
.section-head em{font-style:italic;color:var(--accent);}
.about{margin-bottom:48px;}
.about p{font-size:15px;color:var(--fg-muted);max-width:580px;margin-bottom:14px;}
.about p:last-child{margin-bottom:0;}
.about strong{color:var(--fg);font-weight:500;}
.cloud-band{position:relative;margin-bottom:44px;height:72px;overflow:visible;}
.cloud-band svg{width:100%;height:72px;display:block;overflow:visible;}
@keyframes cloudFloat1{0%,100%{transform:translateX(0px)translateY(0px);}50%{transform:translateX(10px)translateY(-6px);}}
@keyframes cloudFloat2{0%,100%{transform:translateX(0px)translateY(0px);}50%{transform:translateX(-8px)translateY(-4px);}}
@keyframes cloudFloat3{0%,100%{transform:translateX(0px)translateY(0px);}50%{transform:translateX(12px)translateY(-8px);}}
.cloud-band .fc1{animation:cloudFloat1 7s ease-in-out infinite;}
.cloud-band .fc2{animation:cloudFloat2 9s ease-in-out infinite;}
.cloud-band .fc3{animation:cloudFloat3 11s ease-in-out infinite;}
.footer{padding-top:40px;border-top:1px solid var(--card-bd);display:flex;align-items:center;justify-content:space-between;gap:20px;flex-wrap:wrap;}
.footer-left{font-family:var(--f-mono);font-size:11px;letter-spacing:0.1em;color:var(--fg-muted);}
.footer-email{font-family:var(--f-mono);font-size:12px;color:var(--fg-muted);text-decoration:none;border-bottom:1px solid var(--card-bd);padding-bottom:1px;}
@media(prefers-reduced-motion:reduce){.cloud-band .fc1,.cloud-band .fc2,.cloud-band .fc3,.building-dot,.cursor,.heatmap-cell,.count{animation:none;}}
""".replace("__W__", str(W))

ICON = {
    "linkedin": "M19 3A2 2 0 0121 5V19A2 2 0 0119 21H5A2 2 0 013 19V5A2 2 0 015 3H19M18.5 18.5V13.2A3.26 3.26 0 0015.24 9.94C14.39 9.94 13.4 10.46 12.92 11.24V10.13H10.13V18.5H12.92V13.57C12.92 12.8 13.54 12.17 14.31 12.17A1.4 1.4 0 0115.71 13.57V18.5H18.5M6.88 8.56A1.68 1.68 0 008.56 6.88C8.56 5.95 7.81 5.19 6.88 5.19A1.69 1.69 0 005.19 6.88C5.19 7.81 5.95 8.56 6.88 8.56M8.27 18.5V10.13H5.5V18.5H8.27Z",
    "github": "M12 2A10 10 0 002 12c0 4.42 2.87 8.17 6.84 9.5.5.08.66-.23.66-.5v-1.69c-2.77.6-3.36-1.34-3.36-1.34-.46-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.87 1.52 2.34 1.07 2.91.83.09-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.92 0-1.11.38-2 1.03-2.71-.1-.25-.45-1.29.1-2.64 0 0 .84-.27 2.75 1.02.79-.22 1.65-.33 2.5-.33.85 0 1.71.11 2.5.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.35.2 2.39.1 2.64.65.71 1.03 1.6 1.03 2.71 0 3.82-2.34 4.66-4.57 4.91.36.31.69.92.69 1.85V21c0 .27.16.59.67.5C19.14 20.16 22 16.42 22 12A10 10 0 0012 2z",
    "email": "M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4-8 5-8-5V6l8 5 8-5v2z",
}
LABEL = {"linkedin": "LinkedIn", "github": "GitHub", "email": "Email"}

CLOUDS = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 72" fill="none" preserveAspectRatio="xMidYMid meet">
<g class="fc1" opacity="0.82"><rect x="18" y="52" width="136" height="18" rx="9" fill="var(--cloud2)"/><circle cx="42" cy="50" r="18" fill="var(--cloud2)"/><circle cx="68" cy="40" r="24" fill="var(--cloud2)"/><circle cx="98" cy="44" r="20" fill="var(--cloud2)"/><circle cx="122" cy="50" r="16" fill="var(--cloud2)"/><circle cx="68" cy="40" r="18" fill="var(--cloud1)" opacity="0.5"/><circle cx="98" cy="44" r="14" fill="var(--cloud1)" opacity="0.4"/></g>
<g class="fc2" opacity="0.78"><rect x="296" y="52" width="188" height="18" rx="9" fill="var(--cloud3)"/><circle cx="318" cy="50" r="16" fill="var(--cloud3)"/><circle cx="346" cy="38" r="26" fill="var(--cloud3)"/><circle cx="382" cy="34" r="28" fill="var(--cloud3)"/><circle cx="418" cy="40" r="22" fill="var(--cloud3)"/><circle cx="446" cy="50" r="16" fill="var(--cloud3)"/><circle cx="346" cy="38" r="20" fill="var(--cloud1)" opacity="0.45"/><circle cx="382" cy="34" r="22" fill="var(--cloud1)" opacity="0.4"/><circle cx="418" cy="40" r="16" fill="var(--cloud1)" opacity="0.35"/><rect x="476" y="58" width="64" height="12" rx="6" fill="var(--cloud2)" opacity="0.5"/><circle cx="488" cy="57" r="10" fill="var(--cloud2)" opacity="0.5"/><circle cx="506" cy="52" r="13" fill="var(--cloud2)" opacity="0.5"/><circle cx="524" cy="56" r="10" fill="var(--cloud2)" opacity="0.5"/></g>
<g class="fc3" opacity="0.80"><rect x="582" y="52" width="162" height="18" rx="9" fill="var(--cloud4)"/><circle cx="604" cy="50" r="16" fill="var(--cloud4)"/><circle cx="630" cy="40" r="22" fill="var(--cloud4)"/><circle cx="658" cy="34" r="26" fill="var(--cloud4)"/><circle cx="688" cy="40" r="20" fill="var(--cloud4)"/><circle cx="712" cy="50" r="16" fill="var(--cloud4)"/><circle cx="630" cy="40" r="16" fill="var(--cloud2)" opacity="0.45"/><circle cx="658" cy="34" r="20" fill="var(--cloud2)" opacity="0.4"/><circle cx="688" cy="40" r="14" fill="var(--cloud2)" opacity="0.35"/></g>
<line x1="0" y1="70" x2="760" y2="70" stroke="url(#divGrad)" stroke-width="0.8"/>
<defs><linearGradient id="divGrad" x1="0" y1="0" x2="760" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0%" stop-color="var(--accent)" stop-opacity="0"/><stop offset="20%" stop-color="var(--accent)" stop-opacity="0.35"/><stop offset="80%" stop-color="var(--accent)" stop-opacity="0.35"/><stop offset="100%" stop-color="var(--accent)" stop-opacity="0"/></linearGradient></defs>
</svg>"""


def contributions():
    tok = os.environ.get("GITHUB_TOKEN")
    if not tok:
        cached = ROOT / "build" / "contributions.json"
        return json.loads(cached.read_text()) if cached.exists() else None
    q = {"query": '{ user(login:"%s"){ contributionsCollection { contributionCalendar { totalContributions weeks { contributionDays { date contributionCount contributionLevel weekday } } } } } }' % USER}
    req = urllib.request.Request("https://api.github.com/graphql", data=json.dumps(q).encode(),
                                 headers={"Authorization": "bearer " + tok, "User-Agent": "profile-readme-build"})
    cal = json.load(urllib.request.urlopen(req))["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    (ROOT / "build" / "contributions.json").write_text(json.dumps(cal))
    return cal


def heatmap(cal):
    LV = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
    cols, i = [], 0
    for w in cal["weeks"][-53:]:
        by_day = {d["weekday"]: d for d in w["contributionDays"]}
        cells = []
        for wd in range(7):
            d = by_day.get(wd)
            if d is None:
                cells.append('<div class="heatmap-cell e"></div>')
                continue
            v = LV[d["contributionLevel"]]
            tip = f'{d["contributionCount"]} on {d["date"]}'
            cells.append(f'<div class="heatmap-cell" title="{tip}" style="--i:{i}"' + (f' data-v="{v}"' if v else "") + "></div>")
            i += 1
        cols.append('<div class="heatmap-col">' + "".join(cells) + "</div>")
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    return "".join(cols), cal["totalContributions"], sum(1 for d in days if d["contributionCount"] > 0)


def stat(n, ms):
    # Counts up like the original; CSS counters can't add thousands separators, so large numbers are static.
    if n < 1000:
        return f'<span class="stat-n count" style="--t:{n};--d:{ms}ms"></span>'
    return f'<span class="stat-n">{n:,}</span>'


def fragments(cal):
    grid, total, active = heatmap(cal)
    pills = {}
    for k in ("linkedin", "github", "email"):
        pills["pill-" + k] = (f'<span class="pillwrap"><span class="link-pill"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="{ICON[k]}"/></svg>'
                              f'{LABEL[k]}</span></span>')
    return {
        "top": """<section class="hero"><p class="eyebrow">AI · Systems · Open Source</p>
<h1 class="name">Hello, I'm <em>Diya.</em></h1>
<p class="tagline">I build systems that think, from agentic AI platforms to multi-agent workflows.<span class="cursor"></span></p></section>""",
        **pills,
        "body": f"""<div class="body">
<div class="building-card"><div class="building-dot"></div><div>
<p class="building-label">Currently building</p><p class="building-title">BrainAtlas</p><p class="building-desc">A private project — details soon.</p></div></div>
<section class="about"><h2 class="section-head">A little about <em>me</em></h2>
<p>I'm a <strong>CSE (AI) student at KIET Group of Institutions</strong>, building things at the intersection of AI systems and open-source software. I'm drawn to work where the problem is clearly defined and the solution actually ships.</p>
<p>Outside of personal projects, I contribute to open-source — from agentic AI tools and FastAPI blueprints to kernel-adjacent projects. I'm drawn to work that has a clear reason to exist.</p></section>
<div class="cloud-band">{CLOUDS}</div>
<div class="grid-2"><div class="card"><p class="card-label">Tech Stack</p><div class="tag-grid">
<span class="tag">Python</span><span class="tag">LangGraph</span><span class="tag">FastAPI</span><span class="tag">LangChain</span><span class="tag">React</span><span class="tag">Node.js</span><span class="tag">Docker</span><span class="tag">PostgreSQL</span><span class="tag">Redis</span></div></div>
<div class="card"><p class="card-label">Open Source</p><div class="contrib-list">
<div class="contrib-item"><span><strong>openllmetry</strong> — semconv span attributes</span></div>
<div class="contrib-item"><span><strong>fastapi-agent-blueprint</strong> — middleware tests</span></div>
<div class="contrib-item"><span><strong>meridian</strong> — Tailwind v4 migration + vault actions</span></div>
<div class="contrib-item"><span><strong>Argus</strong> — Trivy &amp; Grype ingestion adapters</span></div>
<div class="contrib-item"><span><strong>pocket_pixel</strong> — cookie-based auth</span></div>
<div class="contrib-item"><span><strong>formbricks</strong> — randomise question order</span></div></div></div></div>
<div class="heatmap-wrap"><div class="heatmap-header"><h2 class="heatmap-title">A year of building.</h2></div>
<div class="heatmap-grid">{grid}</div>
<div class="heatmap-stats">
<div class="stat-item">{stat(total, 1200)}<span class="stat-label">Contributions</span></div>
<div class="stat-item">{stat(active, 900)}<span class="stat-label">Active days</span></div>
<div class="stat-item"><span class="stat-n">40+</span><span class="stat-label">Repositories</span></div></div></div>
</div>""",
        "footer": """<footer class="footer"><span class="footer-left">diyaaa-12 · github.com</span>
<span class="footer-email">diyamaheshwari124@gmail.com</span></footer>""",
    }


def svg(name, frag, theme, fonts):
    w = PILL_W.get(name, W)
    h = H[name]
    vars_ = LIGHT if theme == "light" else DARK
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<foreignObject x="0" y="0" width="{w}" height="{h}">
<div xmlns="http://www.w3.org/1999/xhtml" class="r" style="{vars_.replace(chr(10), '')}background:transparent;width:{w}px;">
<style><![CDATA[{fonts}{CSS}]]></style>
{frag}
</div></foreignObject></svg>
"""


def main():
    cal = contributions()
    if cal is None:
        sys.exit("No GITHUB_TOKEN and no cached build/contributions.json")
    fonts = font_face()
    frags = fragments(cal)
    out = ASSETS / "readme"
    out.mkdir(parents=True, exist_ok=True)
    for name, frag in frags.items():
        for theme in ("light", "dark"):
            (out / f"{name}-{theme}.svg").write_text(svg(name, frag, theme, font_face(FONTS_FOR.get(name, "s"))), encoding="utf-8")
    if "--preview" in sys.argv:
        # Plain HTML with the same CSS, for measuring panel sizes in a browser.
        blocks = "".join(f'<div class="m" id="{n}" style="width:{PILL_W.get(n, W)}px"><div class="r" style="{LIGHT.replace(chr(10), "")}width:auto">{f}</div></div>' for n, f in frags.items())
        (ROOT / "build" / "preview.html").write_text(f"<!doctype html><meta charset=utf-8><style>{fonts}{CSS}.m{{display:block;width:fit-content;margin-bottom:40px}}#pill-linkedin,#pill-github,#pill-email{{width:auto!important}}#pill-linkedin .r,#pill-github .r,#pill-email .r{{width:auto}}</style><body style='margin:0;background:#faf9fc'>{blocks}", encoding="utf-8")
    print(f"built {len(frags) * 2} SVGs; contributions={cal['totalContributions']}")


if __name__ == "__main__":
    main()
