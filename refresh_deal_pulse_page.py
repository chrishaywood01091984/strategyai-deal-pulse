#!/usr/bin/env python3
"""
Refresh the Deal Pulse dashboard data from ma_deals.

Calls the public RPC `deal_pulse_snapshot()` and rewrites the embedded data
block (between the DP-DATA:START / DP-DATA:END markers) plus the KPI strip in
index.html, so the dashboard + the PDF rendered from it stay fresh and match
the monthly email. No secrets needed — uses the public anon key.

Usage:  python refresh_deal_pulse_page.py
"""
import json, os, re, sys, urllib.request

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://gvdfeqzhizlzpybdibca.supabase.co").rstrip("/")
ANON = os.environ.get("SUPABASE_ANON_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd2ZGZlcXpoaXpsenB5YmRpYmNhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY1ODY5NTUsImV4cCI6MjA5MjE2Mjk1NX0.8qXLc9stWvkIBuMAzfmwk25fZH99_a96cXPZto77K1I")
HTML = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")

GOLD, COOL = "#c9a84c", "#3b6ea8"
PAT_LABEL = {"post_acq_pmi":"Post-Acq PMI","pe_day_one":"PE Day-One","pe_bolt_on":"PE Bolt-On",
    "platform_build":"Platform Build","carve_out":"Carve-Out","pre_exit_prep":"Pre-Exit Prep",
    "cross_border_entry":"Cross-Border Entry","sector_disruption":"Sector Disruption"}
BUYER_LABEL = {"strategic":"Strategic","pe":"Private Equity","other":"Other","sovereign":"Sovereign","family_office":"Family Office"}
BUYER_COL = {"Strategic":GOLD,"Private Equity":COOL,"Other":"#5d7186","Sovereign":"#8b6914","Family Office":"#3a4a5e"}
REGION_COL = {"EMEA":GOLD,"North America":COOL,"APAC":"#7a8aa0","GCC":"#4a5a6e"}
VBAND_LABEL = {"sub_50m":"<$50m","50_200m":"$50–200m","200_500m":"$200–500m","500m_1b":"$500m–1bn","1b_5b":"$1–5bn","5b_plus":"$5bn+"}
VBAND_ORDER = ["sub_50m","50_200m","200_500m","500m_1b","1b_5b","5b_plus"]

def plabel(slug): return PAT_LABEL.get(slug, (slug or "").replace("_"," ").title())

def fmt_val(usd, disclosed):
    if not disclosed or not usd: return "Undisclosed"
    usd = float(usd)
    if usd >= 1e9: return f"${usd/1e9:.1f}bn"
    if usd >= 1e6: return f"${round(usd/1e6)}m"
    return f"${round(usd):,}"

def fetch():
    req = urllib.request.Request(f"{SUPABASE_URL}/rest/v1/rpc/deal_pulse_snapshot",
        data=b"{}", method="POST",
        headers={"apikey": ANON, "Authorization": f"Bearer {ANON}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read().decode())

def build_block(s):
    heat = [{"s":h["s"],"t":h["t"],"r":h["r"],"p":h["p"],"pct":h.get("pct") or 0} for h in s["heat"]]
    flow = [{"m":f["m"],"d":f["d"],"v":f["v"]} for f in s["flow"]]
    tape = [{"s":t["s"],"pct":t.get("pct") or 0,"d":t["d"]} for t in s["tape"]]
    patterns = [{"n":plabel(p["n"]),"c":p["c"],"trig":p["trig"]} for p in s["patterns"]]
    trig = [{"s":t["s"],"n":t["n"]} for t in s["trig"]]
    geo = [{"c":g["c"],"n":g["n"]} for g in s["geo"]]
    region = [{"c":r["c"],"n":r["n"],"col":REGION_COL.get(r["c"],"#5d7186")} for r in s["region"]]
    buyer = [{"c":BUYER_LABEL.get(b["c"],b["c"]),"n":b["n"],"col":BUYER_COL.get(BUYER_LABEL.get(b["c"],b["c"]),"#5d7186")} for b in s["buyer"]]
    league = [{"n":l["n"],"d":l["d"],"v":f"${float(l['v_bn']):.1f}bn","t":f"{l['sectors']} sectors"} for l in s["league"]]
    vb = {v["b"]: v["n"] for v in s["vbands"]}
    vbands = [{"b":VBAND_LABEL[k],"n":vb[k]} for k in VBAND_ORDER if k in vb]
    deals = [{"b":d["b"],"t":d["t"],"sec":d["sec"],"geo":d["geo"],
              "val":fmt_val(d.get("val_usd"),d.get("disclosed")),"trig":d.get("trig") or 0,
              "pat":plabel(d.get("pat")),"angle":d.get("angle") or "",
              "win":"Advisory window open · 6–14 weeks"} for d in s["deals"]]
    def c(name,obj): return f"const {name}={json.dumps(obj,ensure_ascii=False)};"
    return "\n".join([
        c("months",s["months"]), c("HEAT",heat), c("FLOW",flow), c("TAPE",tape),
        c("PATTERNS",patterns), c("TRIG",trig), c("GEO",geo), c("REGION",region),
        c("BUYER",buyer), c("LEAGUE",league), c("VBANDS",vbands), c("DEALS",deals),
    ])

def main():
    s = fetch()
    k = s["kpis"]
    block = build_block(s)
    html = open(HTML, encoding="utf-8").read()

    # 1) swap the data block between markers
    html, n = re.subn(r"(/\* DP-DATA:START[^\n]*\*/\n)[\s\S]*?(\n/\* DP-DATA:END \*/)",
                      lambda m: m.group(1) + block + m.group(2), html)
    if n != 1: sys.exit(f"ERROR: DP-DATA markers matched {n} times (expected 1)")

    # 2) KPI strip values + sublabels
    subs = [
        (r'(Deals Tracked</div><div class="v" data-count=")\d+', rf'\g<1>{k["deals"]}'),
        (r'(<small>\$</small><span data-count=")\d+',            rf'\g<1>{k["val_bn"]}'),
        (r'(Sectors Live</div><div class="v" data-count=")\d+',  rf'\g<1>{k["sectors"]}'),
        (r'(High-Conviction</div><div class="v" data-count=")\d+', rf'\g<1>{k["high_conv"]}'),
        (r'(Mandate Patterns</div><div class="v" data-count=")\d+', rf'\g<1>{k["patterns"]}'),
        (r'\d+ disclosed · \$[\d.]+bn avg', f'{k["disclosed"]} disclosed · ${k["avg_bn"]:.2f}bn avg'),
        (r'across \d+ countries', f'across {k["countries"]} countries'),
    ]
    for pat, rep in subs:
        html, c = re.subn(pat, rep, html)
        if c < 1: print(f"WARN: KPI pattern not matched: {pat}")

    # 3) momentum-derived bits that live outside the data block (hottest KPI, ticker, tape blurb)
    short = lambda x: (x or "").split(" & ")[0]
    by_pct = sorted([h for h in s["heat"] if h.get("pct") is not None], key=lambda h: h["pct"], reverse=True)
    by_vol = sorted(s["heat"], key=lambda h: h["t"], reverse=True)
    if by_pct:
        hot = by_pct[0]; hn, hp = short(hot["s"]), hot["pct"]
        html = re.sub(r'(<div class="k">Hottest Sector</div><div class="v"[^>]*>)[^<]+(</div>)', rf'\g<1>{hn}\g<2>', html, count=1)
        html = re.sub(r'▲ \+\d+% · last 3mo vs prior', f'▲ +{hp}% · last 3mo vs prior', html, count=1)
        def tick(h):
            p = h["pct"]; return f"['{short(h['s'])}','{'▲ +' if p>=0 else '▼ −'}{abs(p)}%']"
        items_str = "\n  " + ",\n  ".join(tick(h) for h in by_pct) + ",\n "
        html = re.sub(r'const items=\[[\s\S]*?\n \];', f'const items=[{items_str}];', html, count=1)
        if len(by_pct) >= 3:
            blurb = ("Six-month trajectory for every tracked sector at a glance. "
                     f"{short(by_pct[0]['s'])}, {short(by_pct[1]['s'])} and {short(by_pct[2]['s'])} are "
                     f"accelerating hardest into the recent quarter; {short(by_vol[0]['s'])} remains the deepest market by volume.")
            html = re.sub(r'Six-month trajectory for every tracked sector at a glance\.[^<]*', blurb, html, count=1)

    # 4) hardcoded figures scattered through the hand-built prose + two JS donut/legend totals
    wf, wt = s.get("win_from"), s.get("win_to")
    reg = {r["c"]: r["n"] for r in s["region"]}
    emea = reg.get("EMEA", k["deals"])
    uk = s["geo"][0] if s["geo"] else None
    uk_pct = round(uk["n"] * 100 / k["deals"]) if uk and k["deals"] else 0
    vb = {v["b"]: v["n"] for v in s["vbands"]}
    under500 = vb.get("sub_50m", 0) + vb.get("50_200m", 0) + vb.get("200_500m", 0)
    above1b = vb.get("1b_5b", 0) + vb.get("5b_plus", 0)
    prose = [
        (r'(Intelligence window <b>)[^<]+(</b>)', rf'\g<1>{wf} — {wt}\g<2>'),
        (r'<b>\d+</b> deals tracked', f'<b>{k["deals"]}</b> deals tracked'),
        (r'\d+ announced transactions and \$\d+bn', f'{k["deals"]} announced transactions and ${k["val_bn"]}bn'),
        (r'EMEA accounts for \d+ of \d+ deals', f'EMEA accounts for {emea} of {k["deals"]} deals'),
        (r'(<b>)[^<]+ alone is \d+% of tracked deals(</b>)',
         (rf'\g<1>{uk["c"]} alone is {uk_pct}% of tracked deals\g<2>') if uk else None),
        (r'long tail of \d+ countries', f'long tail of {k["countries"]} countries'),
        (r'\d+ disclosed deals under \$500m', f'{under500} disclosed deals under $500m'),
        (r'\d+ above \$1bn', f'{above1b} above $1bn'),
        (r'\d+ EMEA transactions, [0-9A-Za-z ]+ – [0-9A-Za-z ]+\.', f'{k["deals"]} EMEA transactions, {wf} – {wt}.'),
        (r'Disclosed value covers \d+ deals', f'Disclosed value covers {k["disclosed"]} deals'),
        (r',\s*REGION,\s*773\)', ',REGION,REGION.reduce((a,c)=>a+c.n,0))'),
        (r'const tot=773;', 'const tot=BUYER.reduce((a,c)=>a+c.n,0);'),
    ]
    for pat, rep in prose:
        if rep is None: continue
        html, c = re.subn(pat, rep, html)
        if c < 1: print(f"WARN: prose pattern not matched: {pat}")

    open(HTML, "w", encoding="utf-8").write(html)
    print(f"refreshed: {k['deals']} deals, ${k['val_bn']}bn, {len(s['deals'])} board, {len(s['heat'])} sectors, gen {s.get('generated_at')}")

if __name__ == "__main__":
    main()
