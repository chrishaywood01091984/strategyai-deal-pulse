# Builds the behaviour and potential-event dossier cards for the
# "Proof it works" carousel, in the 8 Oct 2026 brand, at the same
# 2400x3200 as the existing catch cards (authored at 1500x2000, x1.6).
import html, json, os, subprocess, sys

OUT = os.path.dirname(os.path.abspath(__file__))

NAVY, LIFT = '#0F1B2D', '#1B2F4D'
INK, MUT = '#16283D', '#5E6E7E'
PUR, DPUR, MID, GRN, LAV = '#7A5CA8', '#7A4FA0', '#3E6491', '#1D9E75', '#C9B6F2'
LINE = '#E2E7EC'
GRAD = f'linear-gradient(90deg,{DPUR} 0%,{MID} 52%,{GRN} 100%)'

FLAG = {
  'GB': '<svg viewBox="0 0 60 30"><clipPath id="c"><path d="M0,0 v30 h60 v-30 z"/></clipPath><clipPath id="t"><path d="M30,15 h30 v15 z v15 h-30 z h-30 v-15 z v-15 h30 z"/></clipPath><g clip-path="url(#c)"><path d="M0,0 v30 h60 v-30 z" fill="#012169"/><path d="M0,0 L60,30 M60,0 L0,30" stroke="#fff" stroke-width="6"/><path d="M0,0 L60,30 M60,0 L0,30" clip-path="url(#t)" stroke="#C8102E" stroke-width="4"/><path d="M30,0 v30 M0,15 h60" stroke="#fff" stroke-width="10"/><path d="M30,0 v30 M0,15 h60" stroke="#C8102E" stroke-width="6"/></g></svg>',
  'SE': '<svg viewBox="0 0 16 10"><rect width="16" height="10" fill="#006AA7"/><rect x="5" width="2" height="10" fill="#FECC00"/><rect y="4" width="16" height="2" fill="#FECC00"/></svg>',
  'FI': '<svg viewBox="0 0 18 11"><rect width="18" height="11" fill="#fff"/><rect x="5" width="3" height="11" fill="#003580"/><rect y="4" width="18" height="3" fill="#003580"/></svg>',
}

HEAD = """<!doctype html><html><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Gloock&family=Hanken+Grotesk:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1500px;height:2000px}
body{font-family:'Hanken Grotesk',system-ui,sans-serif;background:#fff;color:%(INK)s;
     font-synthesis:none;-webkit-font-smoothing:antialiased}
h1,h2,h3,.g{font-family:'Gloock',Georgia,serif;font-weight:400}
.wrap{width:1500px;height:2000px;display:flex;flex-direction:column;position:relative;overflow:hidden}
.bar{height:80px;background:linear-gradient(90deg,%(NAVY)s 0%%,%(LIFT)s 100%%);
     display:flex;align-items:center;gap:18px;padding:0 64px;color:#C7D0DC}
.bar .fl{width:44px;height:26px;border-radius:3px;overflow:hidden;display:block;box-shadow:0 0 0 1px rgba(255,255,255,.22)}
.bar .fl svg{width:100%%;height:100%%;display:block}
.dot{width:11px;height:11px;border-radius:50%%;background:%(GRN)s;flex:0 0 auto}
.bar .lab{font-size:19px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:#fff}
.bar .sp{flex:1}
.bar .kind{font-size:17px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:#9FB0C4}
.chipw{font-size:18px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#fff;
       background:%(DPUR)s;padding:10px 20px;border-radius:7px}
.body{flex:1;padding:52px 64px 128px;display:flex;flex-direction:column;gap:30px;overflow:hidden}
.top{display:flex;align-items:flex-start;gap:40px}
.top .l{flex:1;min-width:0}
h1{font-size:76px;line-height:1.02;letter-spacing:-.01em;color:%(INK)s}
.sub{margin-top:12px;font-size:20px;font-weight:700;letter-spacing:.17em;text-transform:uppercase;color:%(MID)s}
.tags{display:flex;gap:12px;margin-top:22px;flex-wrap:wrap}
.tag{font-size:19px;font-weight:600;letter-spacing:.03em;color:%(INK)s;border:1px solid %(LINE)s;
     border-radius:8px;padding:11px 20px;background:#FBFAFD}
.tag b{font-weight:700;color:%(DPUR)s}
.ring{flex:0 0 232px;width:232px;height:232px;position:relative}
.ring svg{width:232px;height:232px;transform:rotate(-90deg)}
.ring .mid{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px}
.ring .n{font-family:'Gloock',Georgia,serif;font-size:76px;line-height:.9;color:%(MID)s}
.ring .n small{font-size:34px}
.ring .u{font-size:15px;font-weight:700;letter-spacing:.13em;text-transform:uppercase;color:%(MUT)s;text-align:center;line-height:1.3}
h2{font-size:58px;line-height:1.12;letter-spacing:-.005em;max-width:1300px}
h2 em{font-style:normal;color:%(PUR)s}
.lede{font-size:26px;line-height:1.55;font-weight:300;color:#2B3A4B;max-width:1340px}
.lede b{font-weight:700;color:%(INK)s}
.src{display:flex;align-items:center;gap:12px;font-size:19px;color:%(MUT)s}
.src i{width:10px;height:10px;border-radius:50%%;background:%(GRN)s;display:block}
.sech{display:flex;align-items:baseline;justify-content:space-between;
      font-size:19px;font-weight:700;letter-spacing:.17em;text-transform:uppercase;color:%(MID)s}
.sech .r{color:%(GRN)s}
.seq{display:flex;flex-direction:column;gap:0;margin-top:14px}
.row{display:flex;align-items:center;gap:20px;padding:11px 0;position:relative}
.row .b{width:19px;height:19px;border-radius:50%%;flex:0 0 auto;box-shadow:0 0 0 4px #fff}
.row .d{width:118px;font-size:23px;font-weight:600;color:%(MID)s}
.row .p{font-size:16px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#fff;
        padding:7px 13px;border-radius:5px;flex:0 0 auto}
.row .e{font-size:24px;color:%(INK)s;flex:1}
.row .a{font-size:19px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:%(MID)s;text-align:right}
.panel{border:1px solid %(LINE)s;border-left:5px solid %(DPUR)s;border-radius:14px;
       background:linear-gradient(100deg,#F7F5FB 0%%,#F3F7F5 100%%);padding:34px 38px}
.panel .ph{display:flex;align-items:baseline;justify-content:space-between;
           font-size:18px;font-weight:700;letter-spacing:.17em;text-transform:uppercase;color:%(PUR)s}
.panel .ph span{color:%(INK)s;letter-spacing:.02em;text-transform:none;font-size:21px}
.panel h3{font-size:40px;line-height:1.22;margin-top:14px;color:%(INK)s}
.panel h3 em{font-style:normal;color:%(GRN)s}
.two{display:flex;gap:26px}
.two>*{flex:1;min-width:0}
.bars{display:flex;flex-direction:column;gap:15px;margin-top:22px}
.bl{display:flex;align-items:center;gap:16px}
.bl .k{width:280px;font-size:19px;font-weight:700;letter-spacing:.09em;text-transform:uppercase;color:%(MUT)s}
.bl .t{flex:1;height:34px;background:#E8EAF0;border-radius:17px;position:relative;overflow:hidden}
.bl .t i{position:absolute;left:0;top:0;bottom:0;border-radius:17px;display:block}
.bl .v{position:absolute;top:0;bottom:0;display:flex;align-items:center;font-size:19px;font-weight:700;white-space:nowrap}
.note{margin-top:20px;font-size:19px;line-height:1.5;color:%(MUT)s}
.tiles{display:flex;gap:20px}
.tile{flex:1;border:1px solid %(LINE)s;border-radius:12px;padding:24px 26px;min-width:0}
.tile .k{font-size:16px;font-weight:700;letter-spacing:.15em;text-transform:uppercase;color:%(MUT)s}
.tile .v{font-family:'Gloock',Georgia,serif;font-size:30px;line-height:1.2;margin-top:10px;color:%(INK)s}
.foot{position:absolute;left:64px;right:64px;bottom:0;height:104px;border-top:1px solid %(LINE)s;display:flex;align-items:center;
      justify-content:space-between;color:%(MUT)s;font-size:19px;letter-spacing:.14em;text-transform:uppercase}
.foot .lg{font-family:'Gloock',Georgia,serif;font-size:34px;letter-spacing:0;text-transform:none;color:%(INK)s}
.clock{margin-top:26px;position:relative;height:96px}
.clock .axis{position:absolute;left:0;right:0;top:34px;height:30px;background:#E8EAF0;border-radius:15px}
.clock .fillx{position:absolute;left:0;top:34px;height:30px;border-radius:15px}
.clock .mark{position:absolute;top:22px;width:3px;height:54px;background:%(INK)s;border-radius:2px}
.clock .cap{position:absolute;top:0;font-size:17px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;white-space:nowrap}
.clock .cap2{position:absolute;top:72px;font-size:17px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;white-space:nowrap}
.who{display:flex;gap:20px;margin-top:20px}
.who .c{flex:1;border:1px solid %(LINE)s;border-radius:11px;background:#fff;padding:20px 22px;display:flex;gap:16px;align-items:center}
.who .av{width:54px;height:54px;border-radius:50%%;flex:0 0 auto;background:%(GRAD)s}
.who .nm{height:15px;width:60%%;border-radius:4px;background:#CED5DE;filter:blur(3.2px);margin-bottom:9px}
.who .rl{font-size:21px;font-weight:700;color:%(INK)s}
.who .rs{font-size:18px;color:%(MUT)s;margin-top:4px}
.close{margin-top:auto;display:flex;align-items:center;gap:22px;border-radius:13px;padding:26px 32px;
       background:linear-gradient(100deg,%(NAVY)s 0%%,%(LIFT)s 100%%);color:#C7D0DC}
.close .k{font-size:17px;font-weight:700;letter-spacing:.17em;text-transform:uppercase;color:%(LAV)s;flex:0 0 auto}
.close .t{font-family:'Gloock',Georgia,serif;font-size:27px;line-height:1.3;color:#fff;flex:1}
</style></head><body><div class="wrap">""" % dict(NAVY=NAVY, LIFT=LIFT, INK=INK, MUT=MUT, PUR=PUR, DPUR=DPUR, MID=MID, GRN=GRN, LINE=LINE, GRAD=GRAD, LAV=LAV)

TAIL = "</div></body></html>"

def ring(pct, big, small, unit, col_from=DPUR, col_to=GRN):
    C = 2 * 3.141592653589793 * 100
    off = C * (1 - pct)
    return f'''<div class="ring"><svg viewBox="0 0 232 232">
      <defs><linearGradient id="rg" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="{col_from}"/><stop offset=".55" stop-color="{MID}"/><stop offset="1" stop-color="{col_to}"/></linearGradient></defs>
      <circle cx="116" cy="116" r="100" fill="none" stroke="#EDEFF4" stroke-width="15"/>
      <circle cx="116" cy="116" r="100" fill="none" stroke="url(#rg)" stroke-width="15" stroke-linecap="round"
              stroke-dasharray="{C:.1f}" stroke-dashoffset="{off:.1f}"/></svg>
      <div class="mid"><div class="n">{big}{f"<small>{small}</small>" if small else ""}</div><div class="u">{unit}</div></div></div>'''

def bar_row(k, frac, label, colour):
    w = max(frac, 0.04) * 100
    inside = w >= 30
    pos = (f'left:calc({w:.1f}% - 14px);transform:translateX(-100%);color:#fff' if inside
           else f'left:calc({w:.1f}% + 14px);color:{INK}')
    return (f'<div class="bl"><div class="k">{html.escape(k)}</div><div class="t">'
            f'<i style="width:{w:.1f}%;background:{colour}"></i>'
            f'<span class="v" style="{pos}">{label}</span></div></div>')

def tile(k, v):
    return f'<div class="tile"><div class="k">{html.escape(k)}</div><div class="v">{v}</div></div>'

def foot():
    return ('<div class="foot"><span class="lg">StrategyAI</span>'
            '<span>See it while it is still forming</span><span>strategyai.co.uk</span></div>')

# ── Behaviour cards ──────────────────────────────────────────────────────────
# Source: lane1_companies (Companies House behaviours) + deal_precursors, measured
# on 125 UK deals against SIC-matched controls, 9 Oct 2026. Nothing is invented:
# every lift, count and median lead time below is the model's own output.
BEH = [
  dict(key='winvia', co='Winvia Entertainment Plc', cty='GB', loc='United Kingdom · Travel & Leisure',
       lead=248, nproven=3, kind='NO DEAL YET',
       h2='No deal has been announced. Winvia is already doing <em>three of the things that come first.</em>',
       lede='Three filings in nine days, all at Companies House, all public. Separately each is ordinary. '
            'Together they are the pattern we measured across <b>125 completed UK deals</b> — and the earliest '
            'of them typically lands <b>eight months</b> before anything is announced.',
       srcline='3 behaviours · Companies House · first seen 15 Sep 2026',
       rows=[('23 Sep','NEW CHARGE','New charge registered','4.9&times;',DPUR),
             ('16 Sep','OFFICE MOVE','Registered office move','11.9&times;',MID),
             ('15 Sep','CHARGE SATISFIED','Charge satisfied','7.1&times;',GRN)],
       lifts=[('Registered office move',11.88,'11.9&times;',MID),
              ('Charge satisfied',7.09,'7.1&times;',GRN),
              ('New charge registered',4.88,'4.9&times;',DPUR),
              ('A company with no deal coming',1.0,'1.0&times;','#8295A8')],
       liftnote='How much more common each filing is in the run-up to a deal than in a matched control company. '
                'Measured on 125 completed UK deals, 9 Oct 2026.',
       whenrows=[('Registered office move',248,404,'16 of 125 deals'),
                 ('New charge registered',223,349,'25 of 125 deals'),
                 ('Charge satisfied',44,232,'21 of 125 deals')],
       tiles=[('Behaviours proven','Three, in nine days'),('Strongest lift','11.9&times; · office move'),
              ('Typical warning','248 days before a deal'),('Watch expires','25 Oct 2027')],
       roles=[('Chief Financial Officer','Signs the charges and the office change'),
              ('Company Secretary','Files everything above at Companies House')],
       close='There is no process to join and no banker to get past. That is the point of calling now.'),
  dict(key='isembard', co='Isembard', cty='GB', loc='United Kingdom · Software',
       lead=248, nproven=2, kind='NO DEAL YET',
       h2='Isembard moved its registered office. That one filing is <em>twelve times more common before a deal.</em>',
       lede='A month earlier it registered a new charge. Two filings, one month apart, both from the short list '
            'of things that show up before a company is bought — and the office move is the single strongest '
            'precursor in the whole set, typically <b>eight months ahead</b>.',
       srcline='2 behaviours · Companies House · first seen 1 Sep 2026',
       rows=[('1 Oct','OFFICE MOVE','Registered office move','11.9&times;',MID),
             ('1 Sep','NEW CHARGE','New charge registered','4.9&times;',DPUR)],
       lifts=[('Registered office move',11.88,'11.9&times;',MID),
              ('New charge registered',4.88,'4.9&times;',DPUR),
              ('A company with no deal coming',1.0,'1.0&times;','#8295A8')],
       liftnote='How much more common each filing is in the run-up to a deal than in a matched control company. '
                'Measured on 125 completed UK deals, 9 Oct 2026.',
       whenrows=[('Registered office move',248,404,'16 of 125 deals'),
                 ('New charge registered',223,349,'25 of 125 deals')],
       tiles=[('Behaviours proven','Two, one month apart'),('Strongest lift','11.9&times; · office move'),
              ('Typical warning','248 days before a deal'),('Watch expires','9 Nov 2027')],
       roles=[('Chief Executive','Owns the move and the funding structure behind it'),
              ('Company Secretary','Files everything above at Companies House')],
       close='One filing, eight months of notice. Most of the market will read about this next summer.'),
  dict(key='hived', co='HIVED', cty='GB', loc='United Kingdom · Transportation',
       lead=223, nproven=2, kind='NO DEAL YET',
       h2='A new charge, then a shareholder resolution. HIVED is filing <em>what targets file.</em>',
       lede='A shareholder resolution on 18 September, a new charge on 5 October. The resolution alone shows up '
            'in <b>48 of the 125 deals</b> we measured, usually five months out; the charge is rarer and '
            'earlier still. No deal has been announced.',
       srcline='2 behaviours · Companies House · first seen 18 Sep 2026',
       rows=[('5 Oct','NEW CHARGE','New charge registered','4.9&times;',DPUR),
             ('18 Sep','RESOLUTION','Shareholder resolution filed','3.8&times;',MID)],
       lifts=[('New charge registered',4.88,'4.9&times;',DPUR),
              ('Shareholder resolution filed',3.79,'3.8&times;',MID),
              ('A company with no deal coming',1.0,'1.0&times;','#8295A8')],
       liftnote='How much more common each filing is in the run-up to a deal than in a matched control company. '
                'Measured on 125 completed UK deals, 9 Oct 2026.',
       whenrows=[('New charge registered',223,349,'25 of 125 deals'),
                 ('Shareholder resolution filed',160,274,'48 of 125 deals')],
       tiles=[('Behaviours proven','Two, seventeen days apart'),('Strongest lift','4.9&times; · new charge'),
              ('Typical warning','223 days before a deal'),('Watch expires','19 Sep 2027')],
       roles=[('Chief Financial Officer','Signs the charge and the resolution'),
              ('Board Chair','Puts the resolution to shareholders')],
       close='Two filings, seventeen days apart. Neither made the news, and both are on the public record.'),
]

MAXLIFT = 12.5
def behaviour_html(d):
    rows = ''.join(
      f'<div class="row"><span class="b" style="background:{c}"></span><span class="d">{dt}</span>'
      f'<span class="p" style="background:{c}">{tg}</span><span class="e">{html.escape(ev)}</span>'
      f'<span class="a">{lift} more common</span></div>' for dt, tg, ev, lift, c in d['rows'])
    lifts = ''.join(bar_row(k, v / MAXLIFT, lab, c) for k, v, lab, c in d['lifts'])
    when = ''.join(
      f'<div class="bl"><div class="k">{html.escape(k)}</div><div class="t">'
      f'<i style="width:{p75/560*100:.1f}%;background:#D8DEEA"></i>'
      f'<i style="width:{med/560*100:.1f}%;background:{GRAD}"></i>'
      f'<span class="v" style="right:16px;color:{INK}">{med}d median</span></div></div>'
      for k, med, p75, _ in d['whenrows'])
    whennote = ' · '.join(f'{k}: {n}' for k, _, _, n in d['whenrows'])
    who = ''.join(
      f'<div class="c"><span class="av"></span><div><div class="nm"></div>'
      f'<div class="rl">{html.escape(r)}</div><div class="rs">{html.escape(s)}</div></div></div>'
      for r, s in d['roles'])
    return HEAD + f'''
<div class="bar"><span class="fl">{FLAG[d['cty']]}</span><span class="dot"></span>
  <span class="lab">Behaviour spotted &middot; as at 10 Oct 2026</span><span class="sp"></span>
  <span class="kind">{d['kind']}</span><span class="chipw">{d['lead']} days of warning</span></div>
<div class="body">
  <div class="top"><div class="l"><h1>{html.escape(d['co'])}</h1><div class="sub">{d['loc']}</div>
    <div class="tags"><span class="tag"><b>{d['nproven']}</b> proven behaviours</span>
      <span class="tag">Companies House &middot; public filings</span>
      <span class="tag">Measured on <b>125</b> completed UK deals</span></div></div>
    {ring(min(d['lead']/365,1), d['lead'], '', 'days of<br>warning')}</div>
  <h2>{d['h2']}</h2>
  <p class="lede">{d['lede']}</p>
  <div class="src"><i></i>{html.escape(d['srcline'])}</div>
  <div><div class="sech"><span>What we have seen</span><span class="r">No deal announced</span></div>{rows}</div>
  <div class="two">
    <div class="panel"><div class="ph"><span style="letter-spacing:.17em;text-transform:uppercase;font-size:18px">How unusual this is</span></div>
      <div class="bars">{lifts}</div><p class="note">{d['liftnote']}</p></div>
    <div class="panel" style="border-left-color:{GRN}"><div class="ph"><span style="letter-spacing:.17em;text-transform:uppercase;font-size:18px">How early it lands</span></div>
      <div class="bars">{when}</div><p class="note">Median days before the deal, with the 75th percentile behind it in grey. {whennote}.</p></div>
  </div>
  <div class="tiles">{''.join(tile(k, v) for k, v in d['tiles'])}</div>
  <div><div class="sech"><span>Route in &middot; who to call</span><span style="color:{MUT};letter-spacing:.02em;text-transform:none;font-weight:400;font-size:19px">Named on the signal &middot; redacted here</span></div>
    <div class="who">{who}</div></div>
  <div class="close"><span class="k">What this is for</span><span class="t">{d['close']}</span></div>
</div>{foot()}'''  + TAIL

# ── Potential event cards ────────────────────────────────────────────────────
# Source: techeu_capital_state, the funding-clock model. Every figure below is
# read straight off the row: months since the last equity round, the expected
# gap for that company's cohort, the cohort size, and the 24-month outcome mix.
EVT = [
  dict(key='zepz', co='Zepz', cty='GB', loc='United Kingdom · Fintech',
       over=295, months=24.1, exp=14.4, overm=9.7, cohort=295, raised='€806m', rounds=8,
       last='7 Oct 2024', lastamt='€243m', pressure=98, state='RAISE WINDOW OPEN',
       h2='Twenty-four months since the last round. Its cohort <em>goes back at fourteen.</em>',
       lede='Eight rounds and <b>€806m</b> raised, then nothing since October 2024 — and debt taken on in the '
            'meantime. Companies with this shape, at this point in the clock, raised again inside two years '
            '<b>29% of the time</b>, and were acquired <b>12%</b> of the time: nearly five times the base rate.',
       srcline='295 days past its cohort\'s expected gap · 295 comparable companies',
       outcomes=[('Raises again',29.1,GRN),('Gets acquired',11.7,DPUR),('Takes debt',8.4,MID),('Goes quiet',50.8,'#8295A8')],
       lift='4.8&times; the base rate of acquisition',
       reasons=['Four or more rounds already raised','24 months since the last equity round','Debt raised since'],
       investors='Accel',
       tiles=[('Capital pressure','98 out of 100'),('Rounds to date','8 · €806m'),
              ('Last equity round','7 Oct 2024 · €243m'),('Cohort','295 comparable companies')],
       roles=[('Chief Financial Officer','Runs the raise and the lender conversations'),
              ('Chief Executive','Owns the decision between a round and a sale')],
       close='Nobody has announced anything. The clock is the announcement.'),
  dict(key='voi', co='Voi', cty='SE', loc='Sweden · Transportation',
       over=457, months=31.0, exp=15.9, overm=15.0, cohort=313, raised='€376m', rounds=4,
       last='12 Mar 2024', lastamt='€23m', pressure=99, state='OVERDUE',
       h2='Fifteen months past due, on the highest capital pressure <em>in the whole cohort.</em>',
       lede='Thirty-one months since the last equity round, against an expected gap of sixteen. Debt has been '
            'raised since. Of <b>313 comparable companies</b> at this point, <b>30%</b> raised again within '
            'two years and <b>11%</b> were acquired — four times the base rate.',
       srcline='457 days past its cohort\'s expected gap · 313 comparable companies',
       outcomes=[('Raises again',29.8,GRN),('Gets acquired',11.1,DPUR),('Takes debt',9.2,MID),('Goes quiet',49.9,'#8295A8')],
       lift='4.1&times; the base rate of acquisition',
       reasons=['Four or more rounds already raised','30 to 36 months since the last equity round','Debt raised since'],
       investors='Balderton Capital, Creandum, VNV Global, The Raine Group, Project A',
       tiles=[('Capital pressure','99 out of 100'),('Rounds to date','4 · €376m'),
              ('Last equity round','12 Mar 2024 · €23m'),('Cohort','313 comparable companies')],
       roles=[('Chief Financial Officer','Owns the runway and the next structure'),
              ('Board Chair','Where a sale gets decided rather than a round')],
       close='Fifteen months late, with debt taken on since. Something has to happen, and someone will advise on it.'),
  dict(key='firstvet', co='FirstVet', cty='SE', loc='Sweden · Consumer',
       over=362, months=27.5, exp=15.6, overm=11.9, cohort=332, raised='€73m', rounds=4,
       last='24 Jun 2024', lastamt='€20m', pressure=77, state='OVERDUE',
       h2='A year past due, with four rounds behind it and <em>a long gap before this one.</em>',
       lede='Twenty-eight months since the last equity round, against an expected sixteen — and the gap before '
            'that one was long too, which is the pattern that matters most. Of <b>332 comparable companies</b>, '
            '<b>22%</b> raised again within two years and <b>10%</b> were acquired.',
       srcline='362 days past its cohort\'s expected gap · 332 comparable companies',
       outcomes=[('Raises again',21.6,GRN),('Gets acquired',10.2,DPUR),('Takes debt',7.1,MID),('Goes quiet',58.5,'#8295A8')],
       lift='2.6&times; the base rate of acquisition',
       reasons=['Four or more rounds already raised','24 months since the last equity round','A long gap before the last round too'],
       investors='Mubadala Capital, OMERS Ventures, Cathay Innovation, TELUS Global Ventures',
       tiles=[('Capital pressure','77 out of 100'),('Rounds to date','4 · €73m'),
              ('Last equity round','24 Jun 2024 · €20m'),('Cohort','332 comparable companies')],
       roles=[('Chief Financial Officer','Runs the raise and the lender conversations'),
              ('Chief Executive','Owns the decision between a round and a sale')],
       close='A year past due on a cohort of 332. This is a conversation you can have before the process starts.'),
]

def event_html(d):
    MAXM = 36.0
    expx, nowx = d['exp'] / MAXM * 100, min(d['months'], MAXM) / MAXM * 100
    clock = f'''<div class="clock">
      <div class="axis"></div>
      <div class="fillx" style="width:{expx:.1f}%;background:#CBD3E0"></div>
      <div class="fillx" style="left:{expx:.1f}%;width:{nowx-expx:.1f}%;background:{GRAD}"></div>
      <div class="mark" style="left:{expx:.1f}%"></div>
      <div class="mark" style="left:calc({nowx:.1f}% - 3px)"></div>
      <div class="cap" style="left:{expx:.1f}%;transform:translateX(-50%);color:{MUT}">Cohort expects a round &middot; {d['exp']}m</div>
      <div class="cap2" style="left:calc({nowx:.1f}% - 3px);transform:translateX(-100%);color:{DPUR}">Today &middot; {d['months']}m, {d['overm']} months late</div>
      <div class="cap2" style="left:0;color:{MUT}">{d['last']} &middot; last round</div></div>'''
    outs = ''.join(bar_row(k, v / 60.0, f'{v}%', c) for k, v, c in d['outcomes'])
    reasons = ''.join(f'<div class="row" style="padding:9px 0"><span class="b" style="background:{DPUR}"></span>'
                      f'<span class="e">{html.escape(r)}</span></div>' for r in d['reasons'])
    who = ''.join(
      f'<div class="c"><span class="av"></span><div><div class="nm"></div>'
      f'<div class="rl">{html.escape(r)}</div><div class="rs">{html.escape(s)}</div></div></div>'
      for r, s in d['roles'])
    return HEAD + f'''
<div class="bar"><span class="fl">{FLAG[d['cty']]}</span><span class="dot"></span>
  <span class="lab">Event expected &middot; as at 10 Oct 2026</span><span class="sp"></span>
  <span class="kind">{d['state']}</span><span class="chipw">{d['over']} days past due</span></div>
<div class="body">
  <div class="top"><div class="l"><h1>{html.escape(d['co'])}</h1><div class="sub">{d['loc']}</div>
    <div class="tags"><span class="tag"><b>{d['rounds']}</b> rounds &middot; {d['raised']} raised</span>
      <span class="tag">Capital pressure <b>{d['pressure']}</b>/100</span>
      <span class="tag">Against <b>{d['cohort']}</b> comparable companies</span></div></div>
    {ring(min(d['overm']/24,1), d['over'], '', 'days past<br>due')}</div>
  <h2>{d['h2']}</h2>
  <p class="lede">{d['lede']}</p>
  <div class="src"><i></i>{html.escape(d['srcline'])}</div>
  <div><div class="sech"><span>The funding clock</span><span class="r">{d['overm']} months late</span></div>{clock}</div>
  <div class="two">
    <div class="panel"><div class="ph"><span style="letter-spacing:.17em;text-transform:uppercase;font-size:18px">What this cohort did next</span></div>
      <div class="bars">{outs}</div>
      <p class="note">Share of {d['cohort']} comparable companies by outcome within 24 months. Acquisition runs at {d['lift']}.</p></div>
    <div class="panel" style="border-left-color:{GRN}"><div class="ph"><span style="letter-spacing:.17em;text-transform:uppercase;font-size:18px">Why it is on the clock</span></div>
      {reasons}
      <p class="note">Backers on the cap table: {html.escape(d['investors'])}.</p></div>
  </div>
  <div class="tiles">{''.join(tile(k, v) for k, v in d['tiles'])}</div>
  <div><div class="sech"><span>Route in &middot; who to call</span><span style="color:{MUT};letter-spacing:.02em;text-transform:none;font-weight:400;font-size:19px">Named on the signal &middot; redacted here</span></div>
    <div class="who">{who}</div></div>
  <div class="close"><span class="k">What this is for</span><span class="t">{d['close']}</span></div>
</div>{foot()}''' + TAIL

if __name__ == '__main__':
    jobs = [(f"{d['key']}-behaviour", behaviour_html(d)) for d in BEH] + \
           [(f"{d['key']}-event", event_html(d)) for d in EVT]
    for name, doc in jobs:
        p = os.path.join(OUT, name + '.html')
        open(p, 'w').write(doc)
        print('wrote', p)
