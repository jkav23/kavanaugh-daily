#!/usr/bin/env python3
"""Retrieve public Google News RSS headline metadata, without scraping article text."""
import hashlib, html, json, re, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "news.json"
FEEDS = [
 ("Cape Breton","Local",'"Cape Breton" when:7d',13),
 ("Cape Breton","Local",'"New Waterford" when:7d',5),
 ("Cape Breton","Local",'CBRM when:7d',5),
 ("Nova Scotia","Province",'"Nova Scotia" when:3d',10),
 ("Canada","National",'Canada when:2d',10),
 ("World","International",'world news when:1d',10),
 ("Business","Economy",'Canada economy business when:3d',8),
 ("Health","Health",'Canada healthcare health when:4d',8),
 ("Sports","Cape Breton Eagles",'"Cape Breton Eagles" when:7d',6),
 ("Sports","Boston Bruins",'"Boston Bruins" when:3d',6),
 ("Sports","NFL",'NFL when:2d',6),
 ("Sports","MLB",'MLB when:2d',6),
 ("Sports","NBA",'NBA when:2d',6),
 ("Sports","NHL",'NHL when:2d',6),
 ("Sports","MMA",'"UFC" MMA when:3d',7),
 ("Sports","MMA",'"PFL" mixed martial arts when:7d',4),
]
LIMITS = {"Cape Breton":13,"Nova Scotia":10,"Canada":10,"World":10,"Business":8,"Health":8,"Sports":30}
def clean(s):
 return re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]*>"," ",s or ""))).strip()
def main():
 old=json.loads(DEST.read_text()) if DEST.exists() else {"articles":[]}
 grouped={x:[] for x in LIMITS}; seen=set(); success=0
 for section,topic,query,max_count in FEEDS:
  url="https://news.google.com/rss/search?"+urllib.parse.urlencode({"q":query,"hl":"en-CA","gl":"CA","ceid":"CA:en"})
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 personal-news-reader"})
   with urllib.request.urlopen(req,timeout=18) as response: xml=response.read(3000000)
   nodes=ET.fromstring(xml).findall("./channel/item")
   success+=1
  except Exception as e:
   print("Feed unavailable:",query,str(e));continue
  count=0
  for n in nodes:
   title=clean(n.findtext("title"));link=(n.findtext("link") or "").strip()
   se=n.find("source");publisher=clean(se.text if se is not None else "")
   if publisher and title.endswith(" - "+publisher):title=title[:-(len(publisher)+3)]
   if not title or not link.startswith("https://"):continue
   try: published=parsedate_to_datetime(n.findtext("pubDate")).astimezone(timezone.utc)
   except (ValueError,TypeError,OverflowError):continue
   if published<datetime.now(timezone.utc)-timedelta(days=8):continue
   norm=re.sub("[^a-z0-9]","",title.lower())[:110]
   if not norm or norm in seen:continue
   seen.add(norm)
   grouped[section].append({"id":hashlib.sha256((title+publisher).encode()).hexdigest()[:14],"category":section,"topic":topic,"title":title[:240],"source":publisher[:90] or "Publisher via Google News","url":link,"published":published.isoformat().replace("+00:00","Z"),"summary":""})
   count+=1
   if count>=max_count:break
 if not success:
  print("All feeds failed; retaining last edition")
  return
 articles=[]
 for section,limit in LIMITS.items():
  selection=grouped[section]
  selection.sort(key=lambda x:x["published"],reverse=True)
  if not selection:selection=[a for a in old.get("articles",[]) if a.get("category")==section]
  if section=="Sports":
   # Surface every sport (including MMA) instead of letting one busy league crowd others out.
   topics=["Cape Breton Eagles","Boston Bruins","MMA","NHL","NFL","MLB","NBA"]
   balanced=[]
   for round_index in range(4):
    for topic in topics:
     subset=[a for a in selection if a.get("topic")==topic]
     if len(subset)>round_index:
      balanced.append(subset[round_index])
   used={a["id"] for a in balanced}
   selection=balanced+[a for a in selection if a["id"] not in used]
  articles.extend(selection[:limit])
 DEST.write_text(json.dumps({"updated_at":datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z"),"edition_status":"live" if success>=len(FEEDS)*0.6 else "partial","note":"Public RSS headline metadata and outbound publisher links; check original sources for details.","articles":articles},ensure_ascii=False,indent=2)+"\n")
 print("Updated",len(articles),"headlines from",success,"feeds")
if __name__=="__main__":main()
