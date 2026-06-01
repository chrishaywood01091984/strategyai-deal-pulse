// dp-confirm — double opt-in. GET ?t=<confirm_token>. Activates, emails report, REDIRECTS to a real branded page.
// Email template on the StrategyAI brand pack (navy #0d1b2a / gold #c9a84c / Georgia serif + mono labels).
import { serve } from "https://deno.land/std@0.224.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.4";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const RESEND_API_KEY = Deno.env.get("RESEND_API_KEY") || "";
const FROM = "StrategyAI <admin@strategyai.co.uk>";
const FN_BASE = `${SUPABASE_URL}/functions/v1`;
const PDF_URL = `${SUPABASE_URL}/storage/v1/object/public/deal-pulse/report.pdf`;
const PAGE_URL = "https://strategyai.co.uk/deal-insights";
const ML_URL = "https://strategyai.co.uk/mandate-lens";
const CONFIRMED_URL = "https://chrishaywood01091984.github.io/strategyai-deal-pulse/confirmed.html";

function esc(s: string){return String(s||"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]!));}

function welcomeEmail(name:string, unsubUrl:string){
  const first = esc((name||"there").split(/\s+/)[0]);
  return `<!DOCTYPE html><html lang="en-GB"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Your Deal Pulse report</title></head>
<body style="margin:0;padding:0;background:#0a1422;"><div style="display:none;max-height:0;overflow:hidden;opacity:0;color:#0a1422;font-size:1px;">Your six-month EMEA M&amp;A snapshot is ready to download.</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#0a1422;"><tr><td align="center" style="padding:30px 12px;">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background:#0d1b2a;border:1px solid #1f3654;border-radius:10px;overflow:hidden;">
<tr><td style="padding:20px 32px;border-bottom:1px solid #1f3654;"><table role="presentation" width="100%"><tr><td style="font-family:Georgia,'Times New Roman',serif;font-size:18px;color:#ffffff;font-weight:bold;letter-spacing:.3px;">Strategy<span style="color:#c9a84c;font-style:italic;">AI</span></td><td align="right" style="font-family:Consolas,Menlo,monospace;font-size:9px;letter-spacing:.22em;text-transform:uppercase;color:#c9a84c;">&#9679; &nbsp;Deal Pulse &middot; EMEA M&amp;A</td></tr></table></td></tr>
<tr><td style="padding:30px 32px 6px;"><div style="font-family:Consolas,Menlo,monospace;font-size:9px;letter-spacing:.26em;text-transform:uppercase;color:#9fb0c0;margin-bottom:14px;">You're confirmed</div><h1 style="font-family:Georgia,'Times New Roman',serif;font-size:26px;line-height:1.18;font-weight:normal;color:#ffffff;margin:0 0 12px;">You're in. Here's your <span style="color:#c9a84c;font-style:italic;">report.</span></h1>
<p style="font-family:Georgia,serif;font-size:14px;line-height:1.65;color:#d7cdb6;margin:0 0 12px;">Hi ${first}, thanks for confirming. Your snapshot covers six months of EMEA M&amp;A: sector momentum, deal flow, where the advisory mandates are forming, and the live mandate board.</p>
<p style="font-family:Georgia,serif;font-size:14px;line-height:1.65;color:#d7cdb6;margin:0;">You'll get the refreshed edition on the <span style="color:#ffffff;">first of each month</span>.</p></td></tr>
<tr><td style="padding:22px 32px 8px;"><table role="presentation" cellpadding="0" cellspacing="0"><tr><td style="padding-right:10px;"><a href="${PDF_URL}" style="background:#c9a84c;color:#0d1b2a;font-family:Consolas,Menlo,monospace;font-size:11px;letter-spacing:.12em;text-transform:uppercase;font-weight:bold;padding:14px 22px;border-radius:5px;display:inline-block;text-decoration:none;">Download the report &rarr;</a></td><td><a href="${PAGE_URL}" style="color:#c9a84c;font-family:Consolas,Menlo,monospace;font-size:11px;letter-spacing:.12em;text-transform:uppercase;padding:13px 20px;border:1px solid #c9a84c;border-radius:5px;display:inline-block;text-decoration:none;">View live dashboard</a></td></tr></table>
<div style="font-family:Georgia,serif;font-size:12px;color:#9fb0c0;margin-top:14px;font-style:italic;">Want to see where mandates are <span style="color:#c9a84c;">forming</span> next, not where they landed? <a href="${ML_URL}" style="color:#c9a84c;text-decoration:none;">Open Mandate Lens &rarr;</a></div></td></tr>
<tr><td style="padding:20px 32px;border-top:1px solid #1f3654;font-family:Arial,Helvetica,sans-serif;font-size:11px;color:#6f8398;line-height:1.6;">StrategyAI &middot; Live mandate intelligence for advisory partners. You are receiving this because you subscribed to Deal Pulse at strategyai.co.uk.<br><a href="${unsubUrl}" style="color:#9fb0c0;text-decoration:underline;">Unsubscribe</a></td></tr>
</table></td></tr></table></body></html>`;
}

serve(async (req: Request) => {
  const url = new URL(req.url);
  const token = url.searchParams.get("t") || "";
  const redirect = (loc:string)=> new Response(null,{status:303,headers:{Location:loc}});
  if (!token) return redirect(PAGE_URL);
  try {
    const sb = createClient(SUPABASE_URL, SERVICE_KEY);
    const { data: sub } = await sb.from("deal_pulse_subscribers").select("id,name,email,status,unsub_token").eq("confirm_token", token).maybeSingle();
    if (!sub) return redirect(PAGE_URL);
    if (sub.status === "unsubscribed") return redirect(PAGE_URL);
    if (sub.status !== "active") {
      await sb.from("deal_pulse_subscribers").update({ status:"active", confirmed_at:new Date().toISOString(), updated_at:new Date().toISOString() }).eq("id", sub.id);
      const unsubUrl = `${FN_BASE}/dp-unsubscribe?t=${sub.unsub_token}`;
      try { await fetch("https://api.resend.com/emails",{method:"POST",headers:{Authorization:`Bearer ${RESEND_API_KEY}`,"Content-Type":"application/json"},body:JSON.stringify({from:FROM,to:sub.email,reply_to:"admin@strategyai.co.uk",subject:"Your Deal Pulse report — EMEA M&A, last 6 months",html:welcomeEmail(sub.name,unsubUrl),headers:{"List-Unsubscribe":`<${unsubUrl}>, <mailto:unsubscribe@strategyai.co.uk?subject=Unsubscribe>`,"List-Unsubscribe-Post":"List-Unsubscribe=One-Click"}})}); } catch(e){ console.error("welcome send fail",e); }
    }
    return redirect(CONFIRMED_URL);
  } catch (err:any) { console.error("dp-confirm crash", err); return redirect(PAGE_URL); }
});
