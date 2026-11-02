// Secure Cloudflare Cron -> GitHub workflow dispatcher for The Kavanaugh Daily.
// No access tokens belong in this source file: use a Cloudflare Secret.
const ZONE = "America/Halifax";
const WORKFLOW = "https://api.github.com/repos/jkav23/kavanaugh-daily/actions/workflows/publish.yml/dispatches";
const EDITION = "https://jkav23.github.io/kavanaugh-daily/news.json";
const HOURS = new Set([7,8,9,15,16,17]);

function localClock(date) {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: ZONE, year:"numeric", month:"2-digit", day:"2-digit",
    hour:"2-digit", hourCycle:"h23"
  }).formatToParts(date);
  const p = Object.fromEntries(parts.map(x=>[x.type,x.value]));
  return {date: p.year+"-"+p.month+"-"+p.day, hour:Number(p.hour)};
}

async function editionIsCurrent(startHour, scheduledAt) {
  try {
    const res = await fetch(EDITION+"?check="+Date.now(), {
      headers:{"Cache-Control":"no-cache"}, cf:{cacheTtl:0}
    });
    if(!res.ok) throw new Error("News HTTP "+res.status);
    const edition = await res.json();
    const published = new Date(edition.updated_at);
    if(Number.isNaN(published.getTime())) throw new Error("Invalid news timestamp");
    const check = localClock(scheduledAt);
    const seen = localClock(published);
    return seen.date===check.date && seen.hour>=startHour &&
           published.getTime() <= Date.now()+60000;
  } catch(e) {
    console.warn("Cannot verify edition; dispatching as precaution:",String(e));
    return false;
  }
}

async function dispatch(env) {
  if(!env.GITHUB_ACTIONS_TOKEN) throw new Error("Add Cloudflare Secret GITHUB_ACTIONS_TOKEN");
  const res = await fetch(WORKFLOW,{
    method:"POST",
    headers:{
      "Authorization":"Bearer "+env.GITHUB_ACTIONS_TOKEN,
      "Accept":"application/vnd.github+json",
      "Content-Type":"application/json",
      "X-GitHub-Api-Version":"2026-03-10",
      "User-Agent":"KavanaughDailyScheduler"
    },
    body:JSON.stringify({ref:"main"})
  });
  if(res.status!==200 && res.status!==204) throw new Error("GitHub dispatch HTTP "+res.status);
  console.log("News publishing request accepted by GitHub");
}

export default {
  async fetch(request,env){
    if(request.method!=="GET") return new Response("Method not allowed",{status:405});
    return Response.json({
      service:"The Kavanaugh Daily scheduler",
      configured:Boolean(env.GITHUB_ACTIONS_TOKEN),
      timezone:ZONE,
      publishingHoursAtlantic:[7,15],
      website:"https://jkav23.github.io/kavanaugh-daily/"
    },{headers:{"Cache-Control":"no-store"}});
  },
  async scheduled(controller,env,ctx){
    // Cloudflare cron is UTC; we check Atlantic clock time so DST is automatic.
    const scheduledAt=new Date(controller.scheduledTime ?? Date.now());
    const {hour}=localClock(scheduledAt);
    if(!HOURS.has(hour)) return;
    const startHour=hour<12?7:15;
    if(await editionIsCurrent(startHour,scheduledAt)){
      console.log("Edition already published for this Atlantic window");
      return;
    }
    await dispatch(env);
  }
};
