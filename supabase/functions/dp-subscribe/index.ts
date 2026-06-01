// dp-subscribe — Deal Pulse signup (double opt-in). Public endpoint (verify_jwt=false).
// Email template on the StrategyAI brand pack (navy #0d1b2a / gold #c9a84c / Georgia serif + mono labels).
import { serve } from "https://deno.land/std@0.224.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.4";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const RESEND_API_KEY = Deno.env.get("RESEND_API_KEY") || "";
const FROM = "StrategyAI <admin@strategyai.co.uk>";
const FN_BASE = `${SUPABASE_URL}/functions/v1`;

const CORS = { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "POST, OPTIONS", "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type" };
function esc(s: string){return String(s||"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]!));}

function brandEmail(opts:{preheader:string,kicker?:string,title:string,body:string,ctaText?:string,ctaUrl?:string,foot?:string}){
  const cta = opts.ctaText && opts.ctaUrl ? `<table role="presentation"><tr><td style="padding:6px 0 4px;"><a href="${opts.ctaUrl}" style="background:#c9a84c;color:#0d1b2a;font-family:Consolas,Menlo,monospace;font-size:11px;letter-spacing:.12em;text-transform:uppercase;font-weight:bold;padding:14px 24px;border-radius:5px;display:inline-block;text-decoration:none;">${esc(opts.ctaText)}</a></td></tr></table>` : "";
  const kicker = opts.kicker ? `<div style="font-family:Consolas,Menlo,monospace;font-size:9px;letter-spacing:.26em;text-transform:uppercase;color:#9fb0c0;margin-bottom:14px;">${esc(opts.kicker)}</div>` : "";
  return `<!DOCTYPE html><html lang="en-GB"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>${esc(opts.title)}</title></head>
<body style="margin:0;padding:0;background:#0a1422;"><div style="display:none;max-height:0;overflow:hidden;opacity:0;color:#0a1422;font-size:1px;">${esc(opts.preheader)}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#0a1422;"><tr><td align="center" style="padding:30px 12px;">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background:#0d1b2a;border:1px solid #1f3654;border-radius:10px;overflow:hidden;">
<tr><td style="padding:20px 32px;border-bottom:1px solid #1f3654;"><table role="presentation" width="100%"><tr><td style="font-family:Georgia,'Times New Roman',serif;font-size:18px;color:#ffffff;font-weight:bold;letter-spacing:.3px;">Strategy<span style="color:#c9a84c;font-style:italic;">AI</span></td><td align="right" style="font-family:Consolas,Menlo,monospace;font-size:9px;letter-spacing:.22em;text-transform:uppercase;color:#c9a84c;">&#9679; &nbsp;Deal Pulse &middot; EMEA M&amp;A</td></tr></table></td></tr>
<tr><td style="padding:30px 32px 8px;">${kicker}<h1 style="font-family:Georgia,'Times New Roman',serif;font-size:25px;line-height:1.2;font-weight:normal;color:#ffffff;margin:0 0 14px;">${esc(opts.title)}</h1><div style="font-family:Georgia,serif;font-size:14px;line-height:1.65;color:#d7cdb6;">${opts.body}</div></td></tr>
<tr><td style="padding:8px 32px 28px;">${cta}</td></tr>
<tr><td style="padding:18px 32px;border-top:1px solid #1f3654;font-family:Arial,Helvetica,sans-serif;font-size:11px;color:#6f8398;line-height:1.55;">${opts.foot||"StrategyAI &middot; Live mandate intelligence for advisory partners."}</td></tr>
</table></td></tr></table></body></html>`;
}

serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });
  if (req.method !== "POST") return new Response(JSON.stringify({ success:false, error:"Method not allowed" }), { status:405, headers:{...CORS,"Content-Type":"application/json"} });
  try {
    const body = await req.json().catch(()=>({}));
    const name = (body.name||"").toString().trim();
    const email = (body.email||"").toString().trim().toLowerCase();
    const consent = body.consent === true || body.consent === "true";
    const hp = (body.website||"").toString().trim();
    if (hp) return new Response(JSON.stringify({ success:true }), { status:200, headers:{...CORS,"Content-Type":"application/json"} });
    if (!name || name.length>120) return new Response(JSON.stringify({ success:false, error:"Please enter your name." }), { status:400, headers:{...CORS,"Content-Type":"application/json"} });
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return new Response(JSON.stringify({ success:false, error:"Please enter a valid email." }), { status:400, headers:{...CORS,"Content-Type":"application/json"} });
    if (!consent) return new Response(JSON.stringify({ success:false, error:"Please tick the consent box to continue." }), { status:400, headers:{...CORS,"Content-Type":"application/json"} });

    const ip = (req.headers.get("x-forwarded-for")||"").split(",")[0].trim() || null;
    const ua = req.headers.get("user-agent") || null;
    const sb = createClient(SUPABASE_URL, SERVICE_KEY);
    const { data: existing } = await sb.from("deal_pulse_subscribers").select("id,status,confirm_token").eq("email", email).maybeSingle();
    let confirmToken: string; let alreadyActive = false;
    if (existing) {
      if (existing.status === "active") { alreadyActive = true; confirmToken = existing.confirm_token; }
      else { const { data: upd } = await sb.from("deal_pulse_subscribers").update({ name, status:"pending", consent_marketing:true, consent_ts:new Date().toISOString(), consent_ip:ip, consent_user_agent:ua, updated_at:new Date().toISOString() }).eq("id", existing.id).select("confirm_token").single(); confirmToken = upd!.confirm_token; }
    } else {
      const { data: ins, error: insErr } = await sb.from("deal_pulse_subscribers").insert({ name, email, status:"pending", consent_marketing:true, consent_ts:new Date().toISOString(), consent_ip:ip, consent_user_agent:ua, source:(body.source||"deal_pulse").toString().slice(0,40) }).select("confirm_token").single();
      if (insErr) throw insErr; confirmToken = ins!.confirm_token;
    }
    if (alreadyActive) return new Response(JSON.stringify({ success:true, message:"You're already subscribed — thanks! The next edition lands on the 1st." }), { status:200, headers:{...CORS,"Content-Type":"application/json"} });

    const confirmUrl = `${FN_BASE}/dp-confirm?t=${confirmToken}`;
    const html = brandEmail({ preheader:"One click to confirm and get your EMEA M&A report.", kicker:"Confirm your subscription", title:"Confirm your Deal Pulse report", body:`<p style="margin:0 0 14px;">Hi ${esc(name.split(/\s+/)[0])},</p><p style="margin:0 0 14px;">Thanks for requesting the <span style="color:#ffffff;">StrategyAI Deal Pulse</span>, our six-month read on EMEA M&amp;A mandate activity. Confirm your email below and we'll send your report straight over, plus the refreshed edition on the first of each month.</p>`, ctaText:"Confirm and get the report →", ctaUrl:confirmUrl, foot:"You received this because you requested the Deal Pulse report at strategyai.co.uk. If that wasn't you, simply ignore this email and you won't be added." });
    const r = await fetch("https://api.resend.com/emails", { method:"POST", headers:{ Authorization:`Bearer ${RESEND_API_KEY}`, "Content-Type":"application/json" }, body: JSON.stringify({ from:FROM, to:email, reply_to:"admin@strategyai.co.uk", subject:"Confirm your Deal Pulse report", html }) });
    if (!r.ok) { const e = await r.text(); console.error("Resend error", r.status, e); return new Response(JSON.stringify({ success:false, error:"Could not send confirmation email. Please try again." }), { status:502, headers:{...CORS,"Content-Type":"application/json"} }); }
    return new Response(JSON.stringify({ success:true, message:"Almost there — check your inbox to confirm and receive your report." }), { status:200, headers:{...CORS,"Content-Type":"application/json"} });
  } catch (err:any) { console.error("dp-subscribe crash", err); return new Response(JSON.stringify({ success:false, error:"Something went wrong. Please try again." }), { status:500, headers:{...CORS,"Content-Type":"application/json"} }); }
});
