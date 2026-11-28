import json,urllib.request,urllib.parse,re,time,sys
UA="OffsideStoriesDoc/1.0 (football documentary research; low volume)"
T=json.load(open(sys.argv[1])) if len(sys.argv)>1 else ["File:Claudio Ranieri appeals for a decision (25027423845).jpg","File:Claudio Ranieri watches on (24731897220).jpg",
"File:Leicester City FC - Southampton FC 03-Apr-2016, King Power Stadium 02.jpg","File:Riyad Mahrez.jpg",
"File:Mahrez free kick 1 (16476351346).jpg","File:Mahrez free kick 2 (16501343842).jpg","File:Jamie Vardy 18 Ağustos 2019.jpg",
"File:Kasper Schmeichel & Wes Morgan (14997463076).jpg","File:Leicester Clock Tower c1909.jpg"]
p=urllib.parse.urlencode({"action":"query","titles":"|".join(T),"prop":"imageinfo","iiprop":"url|size|extmetadata","iiextmetadatafilter":"LicenseShortName|Artist|DateTimeOriginal","format":"json","maxlag":"5"})
for a in range(12):
    try:
        d=json.load(urllib.request.urlopen(urllib.request.Request("https://commons.wikimedia.org/w/api.php?"+p,headers={"User-Agent":UA}),timeout=30)); break
    except Exception as e: print("wait",e,flush=True); time.sleep(30)
out={}
for pg in d["query"]["pages"].values():
    ii=pg["imageinfo"][0]; m=ii["extmetadata"]
    out[pg["title"]]=dict(url=ii["url"],w=ii["width"],h=ii["height"],lic=m["LicenseShortName"]["value"],artist=re.sub("<[^>]+>","",m.get("Artist",{}).get("value","")).strip(),page=ii["descriptionurl"],date=m.get("DateTimeOriginal",{}).get("value","")[:10])
    print(pg["title"][5:60].ljust(56),out[pg["title"]]["lic"],"|",out[pg["title"]]["artist"][:40],ii["width"],ii["height"])
json.dump(out,open("commons-meta.json","w"),indent=1,ensure_ascii=False)
