"""Reel 008 - 'MUMMY NE GAME DELETE KAR DIYA' (approved script, verbatim subtitles)."""
import math, sys, os, json, re
import numpy as np, cairo, soundfile as sf, colorsys
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from draw import *
from reelkit import *
import sfx

AUD="audio/reel008"; OUT=sys.argv[1] if len(sys.argv)>1 and not sys.argv[1].startswith("--") else "out/reel008.mp4"
PREVIEW="--preview" in sys.argv; BPM=128; HB=60/BPM/4
DIALOGUE=[
 ("01","golu","BHAI GTA 6 TOH KHELNA HAI… PAR ITNE PAISO KA KARU KYA?!"),
 ("02","nikki","Toh paise jama kar na!"),
 ("03","golu","TAB TAK GTA 7 AA JAYEGA!"),
 ("04","raju","Abe budget gamer! Itna tension kyun le raha hai?"),
 ("05","golu","TOH KYA FREE MEIN MILEGA?!"),
 ("06","raju","Cheap PC Games Store pe GTA 6 ke PS5 access options available hain!"),
 ("07","raju","ONE MONTH — ₹1,300!"),
 ("08","golu","AUR LIFETIME?!"),
 ("09","raju","OFFLINE LIFETIME — ₹2,000! ONLINE LIFETIME — ₹3,000!"),
 ("10","nikki","Aur conditions?"),
 ("11","raju","Access details, activation process aur requirements order se pehle website pe check kar lena!"),
 ("12","golu","BHAI AB GTA 6 KA SAPNA POORA HOGA!"),
 ("13","raju","DM karo ‘GTA 6’ ya visit karo cheappcgames.in.net!"),
 ("14","all","HAPPY GAMING!"),
]
HL=re.compile(r"^(GTA|6|7|PAISO|PAISE|JAMA|BUDGET|GAMER|TENSION|FREE|CHEAP|PC|GAMES|STORE|PS5|ACCESS|OPTIONS|ONE|MONTH|LIFETIME|OFFLINE|ONLINE|₹1,300|₹2,000|₹3,000|CONDITIONS|DETAILS|ACTIVATION|PROCESS|REQUIREMENTS|WEBSITE|SAPNA|POORA|DM|‘GTA|6’|CHEAPPCGAMES\.IN\.NET|HAPPY|GAMING)$")
def chunks_of(text):
    words=text.upper().replace("…","… ").replace("—","").split(); out=[]; cur=[]
    for w in words:
        cur.append(w)
        if len(cur)>=3 or (w.endswith(("!","?",",",".","…")) and len(cur)>=2) or len(w)>14:
            out.append(cur); cur=[]
    if cur: out.append(cur)
    return [" ".join(("*"+w+"*") if HL.match(w.strip("!?,.…")) else w for w in c) for c in out]
def q(t): return math.ceil(t/HB)*HB
def safe_load(path, cap=0.2, thr_db=-50):
    a,sr=sf.read(path,dtype="float32")
    if a.ndim>1: a=a.mean(1)
    x=np.linspace(0,len(a)/sr,int(len(a)*SR/sr),endpoint=False); a=np.interp(x,np.arange(len(a))/sr,a).astype(np.float32)
    hop=SR//100; e=np.array([np.sqrt(np.mean(a[i:i+hop]**2)) for i in range(0,len(a)-hop,hop)])
    thr=10**(thr_db/20)*e.max(); s_=e<thr; nz=np.where(~s_)[0]; a0,a1=nz[0],nz[-1]
    segs=[]; cur=max(0,a0*hop-int(0.04*SR)); i=a0
    while i<a1:
        if s_[i]:
            j=i
            while j<a1 and s_[j]: j+=1
            if (j-i)/100>cap+0.02: segs.append(a[cur:i*hop+int(cap*SR/2)]); cur=j*hop-int(cap*SR/2)
            i=j
        else: i+=1
    segs.append(a[cur:a1*hop+int(0.1*SR)]); out=segs[0]; f=int(0.01*SR)
    for g in segs[1:]:
        if len(out)>f and len(g)>f: xx=np.linspace(0,1,f); out=np.concatenate([out[:-f],out[-f:]*(1-xx)+g[:f]*xx,g[f:]])
        else: out=np.concatenate([out,g])
    return out/np.abs(out).max()*0.9

tl=[]; caps=[]; t=q(0.3)
GAP={"01":0.12,"02":0.08,"03":0.15,"04":0.1,"05":0.15,"06":0.1,"07":0.12,"08":0.08,"09":0.15,"10":0.08,"11":0.15,"12":0.1,"13":0.15}
for lid,spk,text in DIALOGUE:
    if spk=="all":
        parts=[("golu",safe_load(f"{AUD}/13a.wav")),("raju",safe_load(f"{AUD}/13b.wav")),("nikki",safe_load(f"{AUD}/13c.wav"))]
        d=max(len(a) for _,a in parts)/SR
        for s_,a in parts: tl.append(dict(id=lid+s_,spk=s_,chunks=[],start=t,end=t+len(a)/SR,audio=a*0.75))
    else:
        a=safe_load(f"{AUD}/{lid}.wav"); d=len(a)/SR; tl.append(dict(id=lid,spk=spk,chunks=[],start=t,end=t+d,audio=a))
    caps.append(dict(id=lid,spk=spk,text=text,chunks=chunks_of(text),start=t,end=t+d))
    t=q(t+d+GAP.get(lid,0.12))
C={c["id"]:c for c in caps}
END_CARD=C["14"]["end"]+0.9; END=END_CARD+5.2
mx=Mixer(tl,END,["golu","raju","nikki"]); NF=mx.NF
print("duration",round(END,2))
def frac(lid,f): c=C[lid]; return c["start"]+f*(c["end"]-c["start"])
S_B=C["02"]["start"]; S_B2=C["03"]["start"]; S_C=C["04"]["start"]; S_C2=C["05"]["start"]; S_D=C["06"]["start"]; S_D2=C["08"]["start"]; S_D3=C["09"]["start"]; S_E=C["10"]["start"]; S_E2=C["11"]["start"]; S_F=C["12"]["start"]; S_F2=C["13"]["start"]; S_G=C["14"]["start"]
STARTS=[S_B,S_B2,S_C,S_C2,S_D,S_D2,S_E,S_E2,S_F,S_F2,S_G,END_CARD]
def pause_end(lid,which=0):
    a=[x for x in tl if x["id"]==lid][0]["audio"]; hop=SR//100
    e=np.array([np.sqrt(np.mean(a[i:i+hop]**2)) for i in range(0,len(a)-hop,hop)]); thr=0.06*e.max(); sil=e<thr; gaps=[]; i=10
    while i<len(sil)-5:
        if sil[i]:
            j=i
            while j<len(sil) and sil[j]: j+=1
            if j-i>=6: gaps.append((i,j))
            i=j
        else: i+=1
    gaps=sorted(gaps,key=lambda g:-(g[1]-g[0]))[:3]; gaps=sorted(gaps)
    return [C[lid]["start"]+g[1]*hop/SR for g in gaps]
P1=(pause_end("07") or [frac("07",0.5)])[0]
pp=pause_end("09"); P2=pp[0] if pp else frac("09",0.3); P3=pp[-1] if len(pp)>1 else frac("09",0.8)
if P3-P2<0.8: P3=frac("09",0.78)
GTA_T=frac("01",0.25); BROKE_T=frac("01",0.75); GTA7=frac("03",0.45); FREE_T=frac("05",0.4); CHK=[frac("11",0.05),frac("11",0.22),frac("11",0.42)]; DREAM=frac("12",0.3); DM_T=frac("13",0.15); URL_T=frac("13",0.55)
mx.add(sfx.boom(),GTA_T,0.9); mx.add(sfx.sad_trombone(),BROKE_T,0.6)
for s in STARTS: mx.add(sfx.whoosh(),s-0.1,0.65)
mx.add(sfx.boing(),GTA7,0.6); mx.add(sfx.pop(),S_C+0.6,0.7); mx.add(sfx.boom(),FREE_T,0.7)
mx.add(sfx.riser(0.5),P1-0.5,0.8)
for p in (P1,P2,P3): mx.add(sfx.boom(),p-0.03,1.15); mx.add(sfx.chaching(),p,0.55)
for c_ in CHK: mx.add(sfx.pop(),c_,0.7)
mx.add(sfx.sparkle(),DREAM,0.9); mx.add(sfx.ding(),DM_T,0.7); mx.add(sfx.sparkle(),S_G,0.9); mx.add(sfx.chaching(),END_CARD+0.3,0.7)
music=sfx.synthwave_track(END+1,bpm=118)
os.makedirs("out",exist_ok=True); mx.render("out/reel008_mix.wav",music=music,music_gain=0.42)

def img_surface(path,wmax=None,crop=None):
    im=Image.open(path).convert("RGBA")
    if crop: im=im.crop(crop)
    if wmax: r=wmax/im.width; im=im.resize((int(im.width*r),int(im.height*r)),Image.LANCZOS)
    a=np.array(im).astype(np.float32); al=a[...,3:4]/255
    bgra=np.ascontiguousarray(np.dstack([a[...,2:3]*al,a[...,1:2]*al,a[...,0:1]*al,a[...,3:4]]).astype(np.uint8))
    return (cairo.ImageSurface.create_for_data(memoryview(bgra),cairo.FORMAT_ARGB32,im.width,im.height,im.width*4),bgra,im.width,im.height)
HDR=img_surface("assets/site_home.png",470,crop=(0,0,1075,640))
PROOF=img_surface("assets/site_home.png",470,crop=(0,3380,1075,3820))
def blink(t,seed): return ((t+seed)%3.2)<0.12
bob=lambda t,f,ph=0,a=6: a*math.sin(t*2*math.pi*f+ph)
def k_in(t,t0,d=0.3,over=0.0): return max(0.01,ease_out_back((t-t0)/d)*(1+over-over*ease_out((t-t0)/(d*0.7))))
def check_badge(ctx,x,y,r):
    ellipse(ctx,x,y,r,r); fill_stroke(ctx,hexc("#2EC45A"),4)
    ctx.move_to(x-r*0.45,y); ctx.line_to(x-r*0.1,y+r*0.38); ctx.line_to(x+r*0.5,y-r*0.35)
    ctx.set_source_rgb(1,1,1); ctx.set_line_width(max(2,r*0.22)); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
def x_badge(ctx,x,y,r):
    ellipse(ctx,x,y,r,r); fill_stroke(ctx,hexc("#E63946"),4)
    for a,b in [((-1,-1),(1,1)),((-1,1),(1,-1))]:
        ctx.move_to(x+a[0]*r*0.4,y+a[1]*r*0.4); ctx.line_to(x+b[0]*r*0.4,y+b[1]*r*0.4)
    ctx.set_source_rgb(1,1,1); ctx.set_line_width(max(2,r*0.22)); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
def chip(ctx,txt,cx,cy,col,k,size=44,mark="check"):
    if k<=0.02: return
    w_,_=paint_text(ctx,txt,cx-20*k,cy,size,scale=k,fill=(30,25,28),stroke=col,sw=0,font="Baloo2.ttf",box=col,pad=14)
    (check_badge if mark=="check" else x_badge)(ctx,cx-20*k+w_/2+8*k,cy,22*k)
def phone_with(ctx,cx,cy,w,h,k,draw_screen,rot=0.0):
    if k<=0.02: return
    ctx.save(); ctx.translate(cx,cy); ctx.scale(k,k); ctx.rotate(rot); draw_phone(ctx,0,0,w,h)
    ctx.save(); rrect(ctx,-w/2+22,-h/2+22,w-44,h-44,36); ctx.clip(); draw_screen(ctx,-w/2+22,-h/2+22,w-44,h-44); ctx.restore(); ctx.restore()

def room(ctx,t,alert=0.0):
    g=cairo.LinearGradient(0,0,0,H); g.add_color_stop_rgb(0,*hexc("#2A1B54")); g.add_color_stop_rgb(1,*hexc("#120C2A")); ctx.set_source(g); ctx.paint()
    for i in range(0,W,90): ctx.rectangle(i,0,2,1350); ctx.set_source_rgba(1,1,1,0.035); ctx.fill()
    for i in range(24):
        h_=(i/24+t*0.25)%1; r,g_,b=colorsys.hsv_to_rgb(h_,0.75,1)
        ellipse(ctx,25+i*45,70,13,13); ctx.set_source_rgba(r,g_,b,0.95); ctx.fill(); ellipse(ctx,25+i*45,70,30,30); ctx.set_source_rgba(r,g_,b,0.16); ctx.fill()
    cols=["#FF4D6D","#5E60CE","#FFD23F","#3BCEAC","#FF9F1C","#4CC9F0"]
    for sy in (430,700):
        rrect(ctx,30,sy,250,22,6); fill_stroke(ctx,hexc("#8A5A3C"),5); x=40
        for k in range(4): rrect(ctx,x,sy-140+k*6,42,140-k*6,6); fill_stroke(ctx,hexc(cols[(k+sy)%6]),5); x+=48
    ctx.rectangle(0,1350,W,H-1350); ctx.set_source_rgb(*hexc("#21183A")); ctx.fill()
    if alert>0: ctx.set_source_rgba(1,0.1,0.15,0.22*alert); ctx.paint()

def screen_deleted(c,x,y,w,h,t):
    c.set_source_rgb(*hexc("#0F1220")); c.rectangle(x,y,w,h); c.fill()
    c.rectangle(x,y,w*0.24,h); c.set_source_rgb(*hexc("#171B2E")); c.fill()
    for i in range(5): rrect(c,x+14,y+30+i*34,w*0.24-28,14,7); c.set_source_rgba(1,1,1,0.18); c.fill()
    paint_text(c,"LIBRARY",x+w*0.62,y+40,30,fill=(255,255,255),stroke=(15,18,32),sw=0,font="LuckiestGuy.ttf",pad=6)
    paint_text(c,"0 GAMES",x+w*0.62,y+h*0.45,52,fill=(140,150,180),stroke=(15,18,32),sw=0,font="Baloo2.ttf",pad=6)
    if t>=DEL_T:
        k=k_in(t,DEL_T,0.25)
        c.save(); c.translate(x+w*0.62,y+h*0.78); c.scale(k,k); rrect(c,-150,-34,300,68,14); c.set_source_rgb(*hexc("#E63946")); c.fill(); c.restore()
        paint_text(c,"GAME DELETED",x+w*0.62,y+h*0.78,34,scale=k,fill=(255,255,255),stroke=(230,57,70),sw=0,font="LuckiestGuy.ttf",pad=6)
def screen_download(c,x,y,w,h,t):
    c.set_source_rgb(*hexc("#0F1220")); c.rectangle(x,y,w,h); c.fill()
    paint_text(c,"DOWNLOADING... 50 GB",x+w/2,y+60,32,fill=(255,255,255),stroke=(15,18,32),sw=0,font="Baloo2.ttf",pad=6)
    rrect(c,x+30,y+h/2-20,w-60,40,20); c.set_source_rgb(*hexc("#2A2F48")); c.fill()
    p=0.012+0.004*math.sin(t*3); rrect(c,x+30,y+h/2-20,max(40,(w-60)*p),40,20); c.set_source_rgb(*hexc("#3BCEAC")); c.fill()
    paint_text(c,"1%",x+w/2,y+h/2+70,44,fill=(255,77,109),stroke=(15,18,32),sw=0,font="Baloo2.ttf",pad=6)
def monitors(ctx,t,main):
    draw_monitor(ctx,610,760,420,320,t,lambda c,x,y,w,h: main(c,x,y,w,h,t))
    draw_monitor(ctx,960,820,220,260,t+1,lambda c,x,y,w,h: (c.set_source_rgb(*hexc("#141830")),c.rectangle(x,y,w,h),c.fill(),[ (rrect(c,x+14,y+20+i*36,w-28-(i%3)*30,14,7),c.set_source_rgba(0.4,0.9,1,0.35),c.fill()) for i in range(6)]))
def desk(ctx,t):
    rrect(ctx,-20,1180,W+40,120,10); fill_stroke(ctx,hexc("#9C6B45"),8)
    ctx.rectangle(-20,1300,W+40,H-1300); ctx.set_source_rgb(*hexc("#7A5236")); ctx.fill()
    rrect(ctx,470,1140,300,46,10); fill_stroke(ctx,hexc("#2B2B33"),6)
    for i in range(10):
        r,g_,b=colorsys.hsv_to_rgb((i/10+t*0.3)%1,0.7,1); ctx.rectangle(485+i*28,1152,20,20); ctx.set_source_rgb(r,g_,b); ctx.fill()

def caption_draw(ctx,t,cy=1395,size=80):
    ln=None
    for c in caps:
        if c["start"]<=t<c["end"]: ln=c; break
    if not ln: return
    n=len(ln["chunks"]); dur=ln["end"]-ln["start"]; lens=[len(c.replace("*",""))+4 for c in ln["chunks"]]; tot=sum(lens); acc=ln["start"]; idx=n-1; cst=acc
    for i,lx in enumerate(lens):
        seg=dur*lx/tot
        if t<acc+seg: idx=i; cst=acc; break
        acc+=seg
    k=ease_out_back((t-cst)/0.16)
    parts=[(w.replace("*",""),w.startswith("*")) for w in ln["chunks"][idx].split(" ")]
    def st(h): return dict(fill=(30,25,28) if h else (255,255,255), stroke=(255,210,63) if h else (25,20,22), sw=0 if h else 9, font="Baloo2.ttf", box=(255,210,63) if h else None, pad=12)
    items=[]; total=0
    for txt,h in parts: _,w,_,_=text_surface(txt,size,**st(h)); items.append((txt,h,w)); total+=w+4
    CX=W/2-25; scale=min(1.0,(W-230)/total)*k; x=CX-total*scale/2
    for txt,h,w in items: paint_text(ctx,txt,x+w*scale/2,cy,size,scale=scale,**st(h)); x+=(w+4)*scale
    col={"golu":(242,193,78),"raju":(47,165,138),"nikki":(255,93,143),"all":(255,255,255)}[ln["spk"]]
    paint_text(ctx,{"all":"GOLU + RAJU + NIKKI"}.get(ln["spk"],ln["spk"].upper()),W/2-25,cy-90,36,fill=(30,25,28),stroke=col,sw=0,font="LuckiestGuy.ttf",box=col,pad=10)



SITE=img_surface("assets/site_home_hi.png",1032)
SITE_NEW_Y=int(5725*1032/1290)
PROOFS=img_surface("assets/proofs_hi.png",900)   # 'NEW ARRIVALS' section on the live homepage
def site_screen(c,x,y,w,h,scroll):
    c.set_source_rgb(*hexc("#0E0E12")); c.rectangle(x,y,w,h); c.fill()
    c.set_source_surface(SITE[0],x+(w-SITE[2])/2,y+70-scroll); c.paint()
    c.rectangle(x,y+h-6,w,6); c.set_source_rgba(0,0,0,0.0); c.fill()
    c.rectangle(x,y,w,70); c.set_source_rgb(1,1,1); c.fill()
    rrect(c,x+20,y+12,w-40,46,23); c.set_source_rgb(*hexc("#ECECF1")); c.fill()
    paint_text(c,"🔒".replace("🔒","")+"cheappcgames.in.net",x+w/2,y+35,32,fill=(40,40,50),stroke=(236,236,241),sw=0,font="Baloo2.ttf",pad=6)
def pip(ctx,kind,x,y,r,t,expr,mouth,look=(0,0),ring=(1,1,1)):
    ctx.save(); ellipse(ctx,x,y,r,r); ctx.clip()
    g=cairo.LinearGradient(x,y-r,x,y+r); g.add_color_stop_rgb(0,*hexc("#5E60CE")); g.add_color_stop_rgb(1,*hexc("#2A1B54")); ctx.set_source(g); ctx.paint()
    draw_character(ctx,kind,x,y+r*0.25,r/150,mouth=mouth,expr=expr,t=t,look=look)
    ctx.restore(); ellipse(ctx,x,y,r,r); ctx.set_source_rgb(*ring); ctx.set_line_width(8); ctx.stroke()
def tile_grid(ctx,x0,y0,cols,rows,w,h,gap,t,scroll=0.0,hi=None,seed0=0,clip=None):
    if clip: ctx.save(); rrect(ctx,*clip,20); ctx.clip()
    for r in range(rows):
        for c in range(cols):
            i=r*cols+c; yy=y0+r*(h+gap)-scroll
            if clip and (yy>clip[1]+clip[3] or yy+h<clip[1]): continue
            game_tile(ctx,x0+c*(w+gap),yy,w,h,seed0+i*3+r,glow=(0.9 if hi==i else 0))
    if clip: ctx.restore()
def qmarks(ctx,t,cx,cy,n=6,R=260):
    for i in range(n):
        a=t*1.5+i*2*math.pi/n; paint_text(ctx,"?",cx+R*math.cos(a),cy+R*0.6*math.sin(a),90,fill=(255,210,63),stroke=(40,0,60),font="LuckiestGuy.ttf",rot=0.3*math.sin(t*3+i))

def diwali_bg(ctx,t,c_top="#1B0B3A",c_bot="#4A1268",fw=True,lanterns=True,diyas=True):
    g=cairo.LinearGradient(0,0,0,H); g.add_color_stop_rgb(0,*hexc(c_top)); g.add_color_stop_rgb(1,*hexc(c_bot)); ctx.set_source(g); ctx.paint()
    rng=np.random.default_rng(6)
    for i in range(70):
        ellipse(ctx,rng.uniform(0,W),rng.uniform(0,1100),2.2,2.2); ctx.set_source_rgba(1,1,1,0.35+0.4*math.sin(t*3+i)); ctx.fill()
    if fw:
        cols=[(1,0.8,0.2),(1,0.35,0.6),(0.4,0.9,1),(0.6,1,0.4)]
        for k in range(6):
            t0=(k*0.7)+math.floor((t-k*0.7)/4.2)*4.2
            firework(ctx,150+((k*331)%800),330+((k*197)%380),t,t0,col=cols[k%4],R=170+30*(k%3),dur=1.5)
    # string lights
    for i in range(26):
        x=i*43+10; y=95+18*math.sin(i*0.9)
        on=0.6+0.4*math.sin(t*6+i*1.3)
        c=[(1,0.75,0.2),(1,0.35,0.45),(0.5,0.85,1),(0.7,1,0.5)][i%4]
        ellipse(ctx,x,y,9,12); ctx.set_source_rgba(*c,on); ctx.fill(); ellipse(ctx,x,y,24,24); ctx.set_source_rgba(*c,0.15*on); ctx.fill()
    if lanterns:
        lantern(ctx,70,330,0.75,t,"#FF4D6D"); lantern(ctx,W-70,420,0.65,t,"#FFD23F")
    if diyas:
        for i,x in enumerate([110,330,750,970]): diya(ctx,x,1760,0.85,t,seed=i)

def flip_calendar(ctx,cx,cy,t,t0,day_to=12,s=1.0,month="NOV"):
    u=t-t0
    if u<0: return
    k=max(0.01,ease_out_back(u/0.3))
    day=min(day_to,1+int(max(0,u-0.1)/0.06)); flip=(u/0.06)%1 if day<day_to else 1
    ctx.save(); ctx.translate(cx,cy); ctx.scale(k*s,k*s)
    rrect(ctx,-150,-170,300,340,30); fill_stroke(ctx,(1,1,1),8)
    ctx.save(); rrect(ctx,-150,-170,300,90,30); ctx.clip(); ctx.rectangle(-150,-170,300,90); ctx.set_source_rgb(*hexc("#E63946")); ctx.fill(); ctx.restore()
    for dx in (-80,80): rrect(ctx,dx-10,-190,20,50,10); fill_stroke(ctx,hexc("#2B2B33"),4)
    ctx.restore()
    paint_text(ctx,month,cx,cy-125*k*s,58,scale=max(k*s,0.01),fill=(255,255,255),stroke=(230,57,70),sw=0,font="LuckiestGuy.ttf",pad=6)
    paint_text(ctx,str(day),cx,cy+40*k*s,170,scale=max(k*s*(0.85+0.15*flip),0.01),fill=(30,25,28),stroke=(255,255,255),sw=0,font="Baloo2.ttf",pad=6)

def synthwave(ctx,t,horizon=1020,sun=True,dim=0.0):
    g=cairo.LinearGradient(0,0,0,horizon); g.add_color_stop_rgb(0,*hexc("#0D0221")); g.add_color_stop_rgb(0.5,*hexc("#4A0E6B")); g.add_color_stop_rgb(1,*hexc("#FF4F8B"))
    ctx.set_source(g); ctx.rectangle(0,0,W,horizon); ctx.fill()
    rng=np.random.default_rng(3)
    for i in range(60):
        x=rng.uniform(0,W); y=rng.uniform(0,horizon*0.6); tw=0.5+0.5*math.sin(t*3+i)
        ellipse(ctx,x,y,2.5,2.5); ctx.set_source_rgba(1,1,1,0.3+0.5*tw); ctx.fill()
    if sun:
        cx,cy,r=W/2,horizon-110,300
        sg=cairo.LinearGradient(0,cy-r,0,cy+r); sg.add_color_stop_rgb(0,*hexc("#FFE45E")); sg.add_color_stop_rgb(1,*hexc("#FF3D7F"))
        ctx.save(); ctx.arc(cx,cy,r,0,2*math.pi); ctx.clip(); ctx.set_source(sg); ctx.paint()
        for k in range(7):
            yy=cy+20+k*38+((t*30)%38); ctx.rectangle(cx-r,yy,2*r,6+k*3); ctx.set_source_rgb(*hexc("#B0247A")); ctx.fill()
        ctx.restore(); backlight(ctx,cx,cy,520,(1,0.4,0.6),0.22+0.12*beatpulse(t))
    rng=np.random.default_rng(8); x=0
    while x<W:
        bw=rng.uniform(50,120); bh=rng.uniform(80,300)
        ctx.rectangle(x,horizon-bh,bw,bh); ctx.set_source_rgb(*hexc("#16052E")); ctx.fill()
        for wy in range(int(horizon-bh+15),int(horizon-10),28):
            for wx in range(int(x+10),int(x+bw-10),22):
                if rng.random()<0.35: ctx.rectangle(wx,wy,8,12); ctx.set_source_rgba(1,0.85,0.4,0.8); ctx.fill()
        x+=bw+4
    for px,ph,flip in [(90,520,1),(990,600,-1),(200,380,1)]: palm(ctx,px,horizon,ph,flip,t)
    fg=cairo.LinearGradient(0,horizon,0,H); fg.add_color_stop_rgb(0,*hexc("#2A0845")); fg.add_color_stop_rgb(1,*hexc("#07000F"))
    ctx.set_source(fg); ctx.rectangle(0,horizon,W,H-horizon); ctx.fill(); ctx.set_line_width(3)
    for i in range(-12,13):
        ctx.move_to(W/2+i*40,horizon); ctx.line_to(W/2+i*260,H); ctx.set_source_rgba(1,0.3,0.8,0.5+0.3*beatpulse(t)); ctx.stroke()
    off=(t*0.8)%1
    for k in range(14):
        u=((k+off)/14)**2.2; yy=horizon+u*(H-horizon); ctx.move_to(0,yy); ctx.line_to(W,yy); ctx.set_source_rgba(0.3,0.9,1,0.25+0.5*u); ctx.stroke()
    if dim: ctx.set_source_rgba(0,0,0,dim); ctx.paint()

def palm(ctx,x,base,h,flip,t):
    ctx.save(); ctx.translate(x,base)
    ctx.move_to(-10,0); ctx.curve_to(-6*flip-10,-h*0.4,14*flip,-h*0.8,22*flip,-h); ctx.line_to(36*flip,-h); ctx.curve_to(28*flip,-h*0.8,8*flip+10,-h*0.4,12,0); ctx.close_path()
    ctx.set_source_rgb(*hexc("#0B021C")); ctx.fill(); ctx.translate(29*flip,-h); sw=0.06*math.sin(t*1.5+x)
    for a in [-2.9,-2.3,-1.7,-1.2,-0.6,-0.1]:
        ctx.save(); ctx.rotate(a+sw); ctx.move_to(0,0); ctx.curve_to(60,-30,130,-10,170,40); ctx.curve_to(120,10,60,0,0,12); ctx.close_path()
        ctx.set_source_rgb(*hexc("#0B021C")); ctx.fill(); ctx.restore()
    ctx.restore()

def neon_card(ctx,cx,cy,w,h,t,t0,label,price,col):
    u=t-t0
    if u<0: return
    k=max(0.01,ease_out_back(u/0.3)*(1.25-0.25*ease_out(u/0.2)))
    ctx.save(); ctx.translate(cx,cy); ctx.scale(k,k)
    for gw,ga in [(34,0.10),(20,0.2),(9,0.5)]:
        rrect(ctx,-w/2,-h/2,w,h,34); ctx.set_source_rgba(*col,ga*(1+0.6*beatpulse(t))); ctx.set_line_width(gw); ctx.stroke()
    rrect(ctx,-w/2,-h/2,w,h,34); ctx.set_source_rgba(0.05,0.01,0.12,0.9); ctx.fill_preserve(); ctx.set_source_rgb(*col); ctx.set_line_width(6); ctx.stroke()
    ctx.restore()
    c255=tuple(int(c*255) for c in col)
    paint_text(ctx,label,cx-w*0.2*k,cy,50 if len(label)<12 else 44,scale=max(k,0.01),fill=(255,255,255),stroke=(20,5,40),font="LuckiestGuy.ttf")
    paint_text(ctx,price,cx+w*0.27*k,cy,118,scale=max(k,0.01),fill=(255,255,255),stroke=(20,5,40),font="Baloo2.ttf",glow=c255,sw=6)


def beatpulse(t): ph=(t/(60/118))%1; return math.exp(-ph*6)
def hand_pos(x,y,s,side,mode,t):
    ang={"cheer":-2.7+0.2*math.sin(t*12+side),"up":-2.4+0.35*math.sin(t*10),"shrug":-0.95+0.05*math.sin(t*6)}[mode]
    a=ang*side
    return x+s*(side*175-320*math.sin(a)), y+s*(200+320*math.cos(a))
def beard(ctx,x,y,s):
    for (dx,dy,r) in [(-60,95,34),(-25,115,38),(25,115,38),(60,95,34),(0,135,34)]:
        ellipse(ctx,x+dx*s,y+dy*s,r*s,r*s); ctx.set_source_rgb(0.95,0.95,0.97); ctx.fill()
    ctx.move_to(x-30*s,y+90*s); ctx.line_to(x+30*s,y+90*s); ctx.set_source_rgb(0.95,0.95,0.97); ctx.set_line_width(14*s); ctx.stroke()
def golu_broke(ctx,x,y,s,t,mouth,expr="cry",pose="cheer"):
    draw_character(ctx,"golu",x,y,s,mouth=mouth,expr=expr,t=t,arm=(pose,pose))
    lx,ly=hand_pos(x,y,s,-1,pose,t); rx,ry=hand_pos(x,y,s,1,pose,t)
    draw_wallet(ctx,lx,ly-40*s,0.85*s); 
    ctx.save(); ctx.translate(lx+30*s+20*math.sin(t*3),ly-150*s-((t*80)%120)*s); ctx.scale(1.2*s,1.2*s); draw_moth(ctx,0,0,t); ctx.restore()
    gamepad(ctx,rx,ry-30*s,0.55*s,rot=0.3)
def dm_bubble(ctx,cx,cy,k,t):
    if k<=0.02: return
    ctx.save(); ctx.translate(cx,cy); ctx.scale(k,k)
    rrect(ctx,-300,-90,600,180,60); fill_stroke(ctx,hexc("#FFFFFF"),8)
    ctx.move_to(-200,85); ctx.line_to(-250,150); ctx.line_to(-140,88); ctx.close_path(); ctx.set_source_rgb(1,1,1); ctx.fill()
    ctx.restore()
    paint_text(ctx,"DM “GTA 6”",cx,cy,88,scale=k,fill=(30,25,28),stroke=(255,255,255),sw=0,font="Baloo2.ttf",pad=8)

def frame(t):
    surf=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); ctx=cairo.Context(surf)
    last=max([0]+[s for s in STARTS if s<=t]); z=1+0.07*(1-ease_out((t-last)/0.28)); shake=(0,0)
    for st_,dur,amp in [(GTA_T,0.3,22),(P1,0.28,22),(P2,0.28,22),(P3,0.28,22),(FREE_T,0.25,14)]:
        if st_<=t<st_+dur: f_=1-(t-st_)/dur; shake=(amp*f_*math.sin(t*97),amp*0.7*f_*math.cos(t*83))
    if t<END_CARD: ctx.translate(W/2+shake[0],H/2+shake[1]); ctx.scale(z,z); ctx.translate(-W/2,-H/2)
    m=lambda k_: mx.mouth(k_,t)
    if t<S_B:   # HOOK: broke gamer wants GTA 6
        synthwave(ctx,t)
        paint_text(ctx,"GTA 6",W/2,330,210,scale=k_in(t,GTA_T,0.3,0.7),fill=(255,255,255),stroke=(40,0,60),font="Baloo2.ttf",glow=(255,60,170),rot=-0.04)
        if t>=BROKE_T: paint_text(ctx,"PAISA?!",W/2,520,120,scale=k_in(t,BROKE_T,0.25,0.6),fill=(255,255,255),stroke=(120,0,20),font="LuckiestGuy.ttf",glow=(255,40,60),rot=0.05)
        golu_broke(ctx,W/2,1060+bob(t,2.5,0,6),1.1,t,m("golu"),expr="cry" if t>=BROKE_T else "excited")
    elif t<S_C: # Nikki: jama kar / Golu: GTA 7 (old Golu)
        if t<S_B2:
            synthwave(ctx,t,dim=0.2)
            draw_character(ctx,"golu",230,1080+bob(t,1.0),0.82,mouth=m("golu"),expr="sad",t=t,look=(1,0))
            draw_character(ctx,"nikki",740,880+bob(t,1.3,1),1.38,mouth=m("nikki"),expr="normal",t=t,look=(-1,0),arm=("hip","point"),blink=blink(t,0.4))
            for i in range(5): coin(ctx,560+i*90,1180+20*math.sin(t*4+i),30,t+i)
            paint_text(ctx,"PAISE JAMA KAR!",W/2,330,104,scale=k_in(t,S_B+0.1,0.3,0.4),fill=(255,255,255),stroke=(120,0,60),font="LuckiestGuy.ttf",glow=(255,90,190))
        else:
            burst_bg(ctx,t,c1="#6C757D",c2="#343A40",cy=700,speed=0.12)
            draw_character(ctx,"golu",W/2,900+bob(t,1.0),1.4,mouth=m("golu"),expr="sad",t=t,arm=("down","down"))
            kb=k_in(t,GTA7-0.3,0.35,0.3); 
            if t>=GTA7-0.3: beard(ctx,W/2,900,1.4*kb)
            paint_text(ctx,"GTA 7",W/2,320,170,scale=k_in(t,GTA7,0.3,0.6),fill=(255,255,255),stroke=(40,0,60),font="Baloo2.ttf",glow=(255,60,170),rot=-0.04)
            paint_text(ctx,"AA JAYEGA!",W/2,480,90,scale=k_in(t,GTA7+0.15,0.3,0.5),fill=(255,210,63),stroke=(40,20,70),font="LuckiestGuy.ttf")
    elif t<S_D: # Raju: budget gamer / Golu: FREE?
        synthwave(ctx,t,dim=0.15)
        if t<S_C2:
            ki=ease_out((t-S_C)/0.3)
            draw_character(ctx,"golu",820,1080+bob(t,1.0),0.82,mouth=m("golu"),expr="sad",t=t,look=(-1,0))
            draw_character(ctx,"raju",320-(1-ki)*700,900+bob(t,1.3),1.28,mouth=m("raju"),expr="smirk",t=t,look=(1,0),arm=("hip","point"),blink=False)
            ks=k_in(t,S_C+0.5,0.3,0.6)
            paint_text(ctx,"BUDGET GAMER",820,800,58,scale=ks,fill=(30,25,28),stroke=(255,210,63),sw=0,font="LuckiestGuy.ttf",box=(255,210,63),pad=14,rot=0.12)
        else:
            draw_character(ctx,"golu",W/2,900+math.sin(t*25)*6,1.45,mouth=m("golu"),expr="shock",t=t,arm=("cheer","cheer"))
            paint_text(ctx,"FREE MEIN?!",W/2,330,140,scale=k_in(t,FREE_T-0.2,0.25,0.6),fill=(255,255,255),stroke=(0,60,50),font="LuckiestGuy.ttf",glow=(46,196,90),rot=0.04)
    elif t<S_E: # PRICE CARDS
        synthwave(ctx,t,horizon=1150,sun=False,dim=0.25)
        paint_text(ctx,"GTA 6 • PS5",W/2,280,90,fill=(255,255,255),stroke=(40,0,60),font="Baloo2.ttf",glow=(255,60,170),scale=k_in(t,S_D,0.3))
        paint_text(ctx,"ACCESS OPTIONS",W/2,375,60,fill=(255,255,255),stroke=(0,40,70),font="LuckiestGuy.ttf",glow=(60,220,255),scale=k_in(t,S_D+0.4,0.3))
        neon_card(ctx,W/2,540,930,190,t,P1,"1 MONTH","₹1,300",(0.3,0.9,1.0))
        neon_card(ctx,W/2,770,930,190,t,P2,"OFFLINE LIFETIME","₹2,000",(1.0,0.35,0.75))
        neon_card(ctx,W/2,1000,930,190,t,P3,"ONLINE LIFETIME","₹3,000",(1.0,0.82,0.25))
        if t>=P3: confetti(ctx,t,P3+0.05,seed=21,n=60,dur=2.0)
        y0=1320
        draw_character(ctx,"golu",190,y0+bob(t,1.6),0.78,mouth=m("golu"),expr="excited" if t>P1 else "normal",t=t,look=(0.5,-1),arm=("cheer","down"),blink=blink(t,0.2))
        draw_character(ctx,"raju",890,y0+bob(t,1.3,2),0.78,mouth=m("raju"),expr="smirk",t=t,look=(-0.5,-1),arm=("point","down"),blink=False)
    elif t<S_F: # CONDITIONS
        synthwave(ctx,t,dim=0.3)
        if t<S_E2:
            draw_character(ctx,"nikki",W/2,880+bob(t,1.2),1.42,mouth=m("nikki"),expr="doubt",t=t,look=(0.5,-0.2),arm=("hip","hip"))
            paint_text(ctx,"CONDITIONS?",W/2,330,124,scale=k_in(t,S_E+0.1,0.3,0.4),fill=(255,255,255),stroke=(120,0,60),font="LuckiestGuy.ttf",glow=(255,90,190))
        else:
            paint_text(ctx,"ORDER SE PEHLE",W/2,290,80,scale=k_in(t,S_E2,0.3),fill=(255,255,255),stroke=(0,40,70),font="LuckiestGuy.ttf",glow=(60,220,255))
            chip(ctx,"ACCESS DETAILS",W/2,450,(80,220,255),k_in(t,CHK[0],0.3,0.4),size=58)
            chip(ctx,"ACTIVATION PROCESS",W/2,580,(255,90,190),k_in(t,CHK[1],0.3,0.4),size=58)
            chip(ctx,"REQUIREMENTS",W/2,710,(255,210,63),k_in(t,CHK[2],0.3,0.4),size=58)
            paint_text(ctx,"WEBSITE PE CHECK KARO",W/2,860,58,scale=k_in(t,frac("11",0.7),0.3),fill=(30,25,28),stroke=(255,255,255),sw=0,font="LuckiestGuy.ttf",box=(255,255,255),pad=16)
            draw_character(ctx,"raju",190,1250+bob(t,1.3),0.75,mouth=m("raju"),expr="smirk",t=t,look=(1,-0.6),arm=("down","point"),blink=False)
            draw_character(ctx,"nikki",880,1270+bob(t,1.2,1),0.72,mouth=m("nikki"),expr="normal",t=t,look=(-1,-0.5),arm=("down","phone"),blink=blink(t,0.6))
    elif t<S_G: # DREAM + DM/URL
        synthwave(ctx,t)
        if t<S_F2:
            kd=k_in(t,DREAM,0.35)
            ctx.save(); ctx.translate(W/2+150,520); ctx.scale(kd,kd)
            for (dx,dy,r) in [(-180,0,120),(-60,-70,140),(90,-50,130),(190,30,110),(40,70,130),(-110,80,110)]: ellipse(ctx,dx,dy,r,r*0.85); ctx.set_source_rgba(1,1,1,0.95); ctx.fill()
            for (dx,dy,r) in [(-260,190,26),(-300,250,16)]: ellipse(ctx,dx,dy,r,r); ctx.set_source_rgba(1,1,1,0.95); ctx.fill()
            gamepad(ctx,0,0,0.9,rot=-0.1)
            ctx.restore()
            if kd>0.3: paint_text(ctx,"GTA 6",W/2+150,420,96,scale=kd,fill=(255,255,255),stroke=(40,0,60),font="Baloo2.ttf",glow=(255,60,170))
            draw_character(ctx,"golu",260,1080-abs(math.sin(t*6))*25,1.15,mouth=m("golu"),expr="excited",t=t,arm=("cheer","cheer"))
            paint_text(ctx,"SAPNA POORA!",W/2+130,800,90,scale=k_in(t,frac("12",0.6),0.3,0.5),fill=(255,210,63),stroke=(40,20,70),font="LuckiestGuy.ttf",glow=(255,170,40))
        else:
            dm_bubble(ctx,W/2+120,420,k_in(t,DM_T,0.3,0.5),t)
            paint_text(ctx,"cheappcgames.in.net",W/2+60,700,74,scale=k_in(t,URL_T,0.3,0.4)*(1+0.03*math.sin(t*8)),fill=(30,25,28),stroke=(255,255,255),sw=0,font="Baloo2.ttf",box=(255,255,255),pad=22)
            draw_character(ctx,"raju",280,1020+bob(t,1.3),1.15,mouth=m("raju"),expr="smirk",t=t,look=(1,-0.5),arm=("down","point"),blink=False)
    elif t<END_CARD: # HAPPY GAMING
        synthwave(ctx,t)
        paint_text(ctx,"HAPPY GAMING!",W/2,380,130,scale=k_in(t,S_G,0.3,0.6),fill=(255,255,255),stroke=(120,40,0),font="LuckiestGuy.ttf",glow=(255,120,0),rot=-0.04)
        draw_character(ctx,"golu",200,1100+bob(t,2.4),0.95,mouth=m("golu"),expr="excited",t=t,arm=("cheer","cheer"))
        draw_character(ctx,"nikki",540,1050+bob(t,2.2,1),1.0,mouth=m("nikki"),expr="laugh",t=t,arm=("cheer","thumbs"))
        draw_character(ctx,"raju",880,1110+bob(t,2.0,2),0.95,mouth=m("raju"),expr="smirk",t=t,arm=("pad","pad")); gamepad(ctx,880,1110+470*0.95,0.75)
        confetti(ctx,t,S_G,seed=4,n=110,dur=3)
    else:       # END CARD
        synthwave(ctx,t,dim=0.55); e=END_CARD
        ctx.set_source_rgba(0.03,0.0,0.08,0.55); rrect(ctx,70,250,W-140,1300,40); ctx.fill()
        paint_text(ctx,"GTA VI — PS5",W/2,370,110,scale=k_in(t,e,0.3),fill=(255,255,255),stroke=(20,5,40),font="Baloo2.ttf",glow=(255,60,170))
        paint_text(ctx,"ACCESS OPTIONS",W/2,490,70,scale=k_in(t,e+0.1,0.3),fill=(255,255,255),stroke=(0,40,70),font="LuckiestGuy.ttf",glow=(60,220,255))
        for i,(lab,pr,col) in enumerate([("1 MONTH","₹1,300",(80,220,255)),("OFFLINE LIFETIME","₹2,000",(255,90,190)),("ONLINE LIFETIME","₹3,000",(255,210,63))]):
            kk=k_in(t,e+0.25+i*0.12,0.3); y=660+i*165
            paint_text(ctx,lab,W/2,y-40,52,scale=kk,fill=(255,255,255),stroke=(20,5,40),font="LuckiestGuy.ttf")
            paint_text(ctx,pr,W/2,y+40,92,scale=kk,fill=(255,255,255),stroke=(20,5,40),font="Baloo2.ttf",glow=col,sw=5)
        paint_text(ctx,"DM “GTA 6”",W/2,1200,96,scale=k_in(t,e+0.7,0.3)*(1+0.04*math.sin(t*8)),fill=(20,15,30),stroke=(255,210,63),sw=0,font="Baloo2.ttf",box=(255,210,63),pad=24)
        paint_text(ctx,"CHEAP PC GAMES STORE",W/2,1370,66,scale=k_in(t,e+0.85,0.3),fill=(255,255,255),stroke=(40,20,70),font="LuckiestGuy.ttf",glow=(255,60,170))
    ctx.identity_matrix(); vignette(ctx)
    if t<END_CARD:
        flash(ctx,t,STARTS+[P1,P2,P3],dur=0.1)
        paint_text(ctx,"CHEAP PC GAMES STORE",W/2-40,165,42,fill=(255,255,255),stroke=(40,25,70),font="LuckiestGuy.ttf",alpha=0.95)
        caption_draw(ctx,t)
    logo_badge(ctx,t)
    return surf

def ease_in_out(x): x=min(max(x,0),1); return 3*x*x-2*x*x*x

def srt(path):
    def ts(x):
        ms=int(round(x*1000)); h=ms//3600000; ms%=3600000; m_=ms//60000; ms%=60000; s_=ms//1000; ms%=1000
        return f"{h:02d}:{m_:02d}:{s_:02d},{ms:03d}"
    names={"golu":"Golu","raju":"Raju","nikki":"Nikki","all":"ALL THREE"}
    with open(path,"w",encoding="utf-8") as f:
        for i,c in enumerate(caps,1): f.write(f"{i}\n{ts(c['start'])} --> {ts(c['end'])}\n{names[c['spk']]}: {c['text']}\n\n")
        f.write(f"{len(caps)+1}\n{ts(END_CARD)} --> {ts(END)}\nGTA VI — PS5 ACCESS OPTIONS | 1 MONTH — ₹1,300 | OFFLINE LIFETIME — ₹2,000 | ONLINE LIFETIME — ₹3,000 | DM \"GTA 6\" | CHEAP PC GAMES STORE\n\n")

def thumbnail(path):
    surf=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); ctx=cairo.Context(surf); t=1.2
    synthwave(ctx,t,horizon=1250)
    ctx.set_source_rgba(0.05,0.0,0.12,0.5); rrect(ctx,40,240,W-80,470,36); ctx.fill()
    paint_text(ctx,"GTA 6 KHELNA HAI…",W/2,330,92,fill=(255,255,255),stroke=(30,0,50),font="LuckiestGuy.ttf",glow=(255,60,170))
    w_,_=paint_text(ctx,"PAISA NAHI HAI?!",W/2-55,480,106,fill=(255,255,255),stroke=(120,0,20),font="LuckiestGuy.ttf",glow=(255,40,60),rot=-0.03)
    skull(ctx,W/2-55+w_/2+52,480,40)
    paint_text(ctx,"STARTING AT ₹1,300",W/2,640,78,fill=(30,25,28),stroke=(255,210,63),sw=0,font="Baloo2.ttf",box=(255,210,63),pad=18)
    for i,(lab,pr,col) in enumerate([("1 MONTH","₹1,300",(0.3,0.9,1.0)),("OFFLINE LIFETIME","₹2,000",(1.0,0.35,0.75)),("ONLINE LIFETIME","₹3,000",(1.0,0.82,0.25))]):
        cx=200+i*340; cy=820
        for gw,ga in [(22,0.15),(9,0.5)]:
            rrect(ctx,cx-155,cy-80,310,160,24); ctx.set_source_rgba(*col,ga); ctx.set_line_width(gw); ctx.stroke()
        rrect(ctx,cx-155,cy-80,310,160,24); ctx.set_source_rgba(0.05,0.01,0.12,0.92); ctx.fill_preserve(); ctx.set_source_rgb(*col); ctx.set_line_width(5); ctx.stroke()
        paint_text(ctx,lab,cx,cy-38,30 if len(lab)>8 else 34,fill=(255,255,255),stroke=(20,5,40),sw=3,font="LuckiestGuy.ttf",pad=6)
        paint_text(ctx,pr,cx,cy+28,66,fill=(255,255,255),stroke=(20,5,40),sw=4,font="Baloo2.ttf",glow=tuple(int(c*255) for c in col),pad=10)
    draw_character(ctx,"nikki",150,1180,0.82,expr="laugh",t=t,arm=("hip","down"))
    draw_character(ctx,"raju",935,1200,0.8,expr="smirk",t=t,look=(-0.6,-0.8),arm=("point","down"))
    golu_broke(ctx,W/2,1240,1.0,t,0.7,expr="cry",pose="shrug")
    vignette(ctx); logo_badge(ctx)
    surf.write_to_png(path); Image.open(path).convert("RGB").save(path.replace(".png",".jpg"),quality=93)

if __name__=="__main__":
    srt("out/reel008.srt")
    meta={"cover_ms":int((P3+0.8)*1000),"duration":END,"end_card":[END_CARD,END],"prices":[P1,P2,P3],"lines":[(c["id"],c["spk"],round(c["start"],2),round(c["end"],2)) for c in caps]}
    if "--thumb" in sys.argv: thumbnail("out/reel008_thumbnail.png"); sys.exit()
    if PREVIEW:
        pts=[("a",BROKE_T+0.4),("b",S_B+0.6),("c",GTA7+0.5),("d",S_C+1.0),("e",FREE_T+0.3),("f",P3+0.6),("g",S_E+0.4),("h",CHK[2]+0.6),("i",DREAM+0.8),("j",URL_T+0.6),("k",S_G+0.4),("l",END-0.5)]
        for n_,tt in pts: frame(tt).write_to_png(f"out/r11_{n_}.png")
        json.dump(meta,open("out/reel008_meta.json","w"),indent=1); print(json.dumps(meta)[:300]); sys.exit()
    encode(frame,NF,"out/reel008_mix.wav",OUT); json.dump(meta,open("out/reel008_meta.json","w"),indent=1); print("done",OUT)

