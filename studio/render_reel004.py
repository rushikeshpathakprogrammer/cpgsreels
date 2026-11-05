"""Reel 004 - 'MUMMY NE GAME DELETE KAR DIYA' (approved script, verbatim subtitles)."""
import math, sys, os, json, re
import numpy as np, cairo, soundfile as sf, colorsys
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from draw import *
from reelkit import *
import sfx

AUD="audio/reel004"; OUT=sys.argv[1] if len(sys.argv)>1 and not sys.argv[1].startswith("--") else "out/reel004.mp4"
PREVIEW="--preview" in sys.argv; BPM=128; HB=60/BPM/2
DIALOGUE=[
 ("01","golu","BHAI! MERI MUMMY NE MERA GAME DELETE KAR DIYA!!!"),
 ("02","nikki","Toh dobara download kar le!"),
 ("03","golu","50 GB ka game tha! Internet khatam, patience khatam, zindagi khatam!"),
 ("04","raju","Bhai, tu game khelta hai ya har baar game install karne ka course karta hai?"),
 ("05","golu","Bhai dard samajh!"),
 ("06","raju","Waise Cheap PC Games Store check kiya? Apni favourite games ki listings dekh. Games ₹99 se start hote hain!"),
 ("07","golu","Aur mujhe apni favourite game mil gayi toh?"),
 ("08","raju","Available edition aur access details check kar, phir order kar!"),
 ("09","nikki","Aur delivery ka proof?"),
 ("10","raju","Website pe WhatsApp delivery proofs hain, plus 2000+ happy customers!"),
 ("11","golu","Ab mummy delete kare ya PC format ho... pehle backup rakhunga!"),
 ("12","raju","Aur games explore karne ke liye visit karo cheappcgames.in.net!"),
 ("13","all","HAPPY GAMING!"),
]
HL=re.compile(r"^(MUMMY|DELETE|50|GB|KHATAM|INTERNET|PATIENCE|ZINDAGI|COURSE|DARD|CHEAP|PC|GAMES|STORE|₹99|LISTINGS|FAVOURITE|EDITION|ACCESS|DETAILS|ORDER|PROOF|PROOFS|WHATSAPP|2000\+|BACKUP|CHEAPPCGAMES\.IN\.NET|HAPPY|GAMING)$")
def chunks_of(text):
    words=text.upper().split(); out=[]; cur=[]
    for w in words:
        cur.append(w)
        if len(cur)>=3 or (w.endswith(("!","?",",",".","...")) and len(cur)>=2) or len(w)>14:
            out.append(cur); cur=[]
    if cur: out.append(cur)
    return [" ".join(("*"+w+"*") if HL.match(w.strip("!?,.")) else w for w in c) for c in out]
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
GAP={"01":0.2,"02":0.12,"03":0.2,"04":0.15,"05":0.25,"06":0.12,"07":0.1,"08":0.15,"09":0.1,"10":0.15,"11":0.15,"12":0.2}
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
HG_END=C["13"]["end"]+1.0
END_CARD=HG_END; END=END_CARD+4.2
mx=Mixer(tl,END,["golu","raju","nikki"]); NF=mx.NF
print("duration",round(END,2))
def frac(lid,f): c=C[lid]; return c["start"]+f*(c["end"]-c["start"])

S_B=C["02"]["start"]; S_C=C["04"]["start"]; S_C2=C["05"]["start"]; S_D=C["06"]["start"]; S_E=C["09"]["start"]; S_F=C["11"]["start"]; S_F2=C["12"]["start"]; S_G=C["13"]["start"]
STARTS=[S_B,S_C,S_C2,S_D,S_E,S_F,S_F2,S_G,END_CARD]
DEL_T=frac("01",0.55); X1=frac("03",0.42); X2=frac("03",0.66); X3=frac("03",0.9)
CAP_T=frac("04",0.55); P99=frac("06",0.72)
K1=frac("08",0.05); K2=frac("08",0.38); K3=frac("08",0.75)
mx.add(sfx.alarm(1.2),0.0,0.7); mx.add(sfx.error_buzz(),DEL_T,1.0); mx.add(sfx.boom(),DEL_T,0.8)
for s in STARTS: mx.add(sfx.whoosh(),s-0.1,0.7)
for x in (X1,X2,X3): mx.add(sfx.stamp(),x,0.9)
mx.add(sfx.sad_trombone(),C["03"]["end"]+0.05,0.9)
mx.add(sfx.pop(),CAP_T,0.8); mx.add(sfx.boing(),C["05"]["start"]+0.1,0.5)
mx.add(sfx.chaching(),P99,0.9); mx.add(sfx.sparkle(),P99+0.1,0.7)
for k in (K1,K2,K3): mx.add(sfx.pop(),k,0.7)
mx.add(sfx.ding(),frac("10",0.5),0.7); mx.add(sfx.sparkle(),S_G,0.9); mx.add(sfx.chaching(),END_CARD+0.2,0.7)
os.makedirs("out",exist_ok=True); mx.render("out/reel004_mix.wav",bpm=BPM,music_gain=0.45)

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
    scale=min(1.0,(W-70)/total)*k; x=W/2-total*scale/2
    for txt,h,w in items: paint_text(ctx,txt,x+w*scale/2,cy,size,scale=scale,**st(h)); x+=(w+4)*scale
    col={"golu":(242,193,78),"raju":(47,165,138),"nikki":(255,93,143),"all":(255,255,255)}[ln["spk"]]
    paint_text(ctx,{"all":"GOLU + RAJU + NIKKI"}.get(ln["spk"],ln["spk"].upper()),W/2,cy-90,36,fill=(30,25,28),stroke=col,sw=0,font="LuckiestGuy.ttf",box=col,pad=10)

def backup_drive(ctx,x,y,s,t):
    ctx.save(); ctx.translate(x,y); ctx.scale(s,s); ctx.rotate(0.05*math.sin(t*4))
    rrect(ctx,-150,-100,300,200,30); fill_stroke(ctx,hexc("#3A86FF"),8)
    rrect(ctx,-120,-70,240,90,16); ctx.set_source_rgb(1,1,1); ctx.fill()
    ellipse(ctx,110,70,12,12); ctx.set_source_rgb(*hexc("#3BCEAC")); ctx.fill()
    ctx.restore()
    paint_text(ctx,"BACKUP",x,y-25*s,56*s if s<1 else 56,scale=s if s<1 else 1,fill=(30,25,28),stroke=(255,255,255),sw=0,font="LuckiestGuy.ttf",pad=6)
def mortarboard(ctx,x,y,s,k):
    ctx.save(); ctx.translate(x,y); ctx.scale(s*k,s*k)
    ctx.move_to(0,-60); ctx.line_to(170,0); ctx.line_to(0,60); ctx.line_to(-170,0); ctx.close_path(); fill_stroke(ctx,hexc("#1D1D24"),6)
    rrect(ctx,-80,10,160,60,12); fill_stroke(ctx,hexc("#1D1D24"),6)
    ctx.move_to(0,0); ctx.line_to(120,40); ctx.line_to(130,110); ctx.set_source_rgb(*hexc("#FFD23F")); ctx.set_line_width(7); ctx.stroke()
    ctx.restore()

def frame(t):
    surf=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); ctx=cairo.Context(surf)
    last=max([0]+[s for s in STARTS if s<=t]); z=1+0.07*(1-ease_out((t-last)/0.28)); shake=(0,0)
    for st_,dur,amp in [(DEL_T,0.4,26),(X1,0.18,10),(X2,0.18,10),(X3,0.25,16),(P99,0.2,10)]:
        if st_<=t<st_+dur: f_=1-(t-st_)/dur; shake=(amp*f_*math.sin(t*97),amp*0.7*f_*math.cos(t*83))
    if t<END_CARD: ctx.translate(W/2+shake[0],H/2+shake[1]); ctx.scale(z,z); ctx.translate(-W/2,-H/2)
    m=lambda k_: mx.mouth(k_,t)
    if t<S_B:   # HOOK: game deleted
        al=0.5+0.5*math.sin(t*14) if t>DEL_T else 0
        room(ctx,t,al); monitors(ctx,t,screen_deleted)
        draw_character(ctx,"golu",280,790+bob(t,3,0,8),1.12,mouth=m("golu"),expr="shock",t=t,look=(0.6,-0.2),arm=("head","head"))
        desk(ctx,t)
        kd=k_in(t,DEL_T-0.1,0.3,0.6)
        paint_text(ctx,"DELETE",W/2,330,190,scale=kd,fill=(255,255,255),stroke=(120,0,20),font="LuckiestGuy.ttf",glow=(255,40,60),rot=-0.05)
    elif t<S_C: # DRAMA
        room(ctx,t)
        draw_character(ctx,"golu",290,930+bob(t,2.2),1.1,mouth=m("golu"),expr="cry" if t>=C["03"]["start"] else "shock",t=t,look=(1,0),arm=("head","head") if t>=X3 else ("down","down"),blink=False)
        draw_character(ctx,"nikki",800,950+bob(t,1.2,1),1.08,mouth=m("nikki"),expr="normal" if t<C["03"]["start"] else "laugh",t=t,look=(-1,0),arm=("down","phone"),blink=blink(t,0.7))
        if t>=C["03"]["start"]-0.1:
            kp=k_in(t,C["03"]["start"]-0.1,0.3)
            ctx.save(); ctx.translate(W/2,370); ctx.scale(kp,kp); ctx.translate(-W/2,-370)
            rrect(ctx,W/2-360,240,720,260,30); fill_stroke(ctx,hexc("#0F1220"),8)
            screen_download(ctx,W/2-340,255,680,230,t); ctx.restore()
            for i,(txt,tt) in enumerate([("INTERNET KHATAM",X1),("PATIENCE KHATAM",X2),("ZINDAGI KHATAM",X3)]):
                chip(ctx,txt,W/2,575+i*72,(255,120,120),k_in(t,tt,0.25,0.5),size=42,mark="x")
    elif t<S_C2: # ROAST
        room(ctx,t)
        draw_character(ctx,"raju",300,800+bob(t,1.3),1.12,mouth=m("raju"),expr="normal",t=t,look=(1,0),arm=("down","point"),blink=blink(t,0.4))
        draw_character(ctx,"golu",800,830+bob(t,1.6,1),1.05,mouth=m("golu"),expr="sad",t=t,look=(-1,0.3),blink=blink(t,1.2))
        kc=k_in(t,CAP_T,0.3,0.4)
        if t>=CAP_T: mortarboard(ctx,800,660,1.05,kc)
        kcert=k_in(t,CAP_T+0.2,0.35)
        if t>=CAP_T+0.2:
            ctx.save(); ctx.translate(W/2,330); ctx.scale(kcert,kcert); ctx.rotate(-0.04)
            rrect(ctx,-400,-120,800,240,24); fill_stroke(ctx,hexc("#FFF6D6"),8)
            rrect(ctx,-380,-100,760,200,16); ctx.set_source_rgb(*hexc("#E0B84A")); ctx.set_line_width(4); ctx.stroke(); ctx.restore()
            paint_text(ctx,"CERTIFIED",W/2,290,58,scale=kcert,fill=(120,70,10),stroke=(255,246,214),sw=0,font="LuckiestGuy.ttf",rot=-0.04)
            paint_text(ctx,"GAME INSTALLER",W/2,370,64,scale=kcert,fill=(30,25,28),stroke=(255,246,214),sw=0,font="LuckiestGuy.ttf",rot=-0.04)
    elif t<S_D: # DARD
        burst_bg(ctx,t,c1="#4A4E69",c2="#22223B",cy=700,speed=0.1)
        draw_character(ctx,"golu",W/2,860+bob(t,2.5),1.45,mouth=m("golu"),expr="cry",t=t,arm=("head","head"))
        kh=k_in(t,S_C2+0.1,0.3,0.4)
        paint_text(ctx,"DARD",W/2,330,170,scale=kh,fill=(255,255,255),stroke=(80,0,30),font="LuckiestGuy.ttf",glow=(255,60,120),rot=0.05)
    elif t<S_E: # STORE + ₹99 + checklist
        bokeh_bg(ctx,t,"#3A2466","#140B2E",seed=5,tint=(1,0.9,0.6))
        def site(c,x,y,w,h):
            c.set_source_rgb(*hexc("#0E0E12")); c.rectangle(x,y,w,h); c.fill(); c.rectangle(x,y,w,60); c.set_source_rgb(1,1,1); c.fill()
            paint_text(c,"cheappcgames.in.net",x+w/2,y+31,28,fill=(60,60,70),stroke=(255,255,255),sw=0,font="Baloo2.ttf",pad=6)
            c.set_source_surface(HDR[0],x+(w-HDR[2])/2,y+64); c.paint()
        if t<K1-0.15:
            kp=k_in(t,S_D+0.05,0.35)
            phone_with(ctx,W/2+170,620,500,760,kp,site,rot=0.03)
        draw_character(ctx,"raju",190,1180+bob(t,1.3),0.85,mouth=m("raju"),expr="normal",t=t,look=(1,-0.6),arm=("down","point"),blink=blink(t,0.6))
        if t>=C["07"]["start"]-0.2:
            kg=k_in(t,C["07"]["start"]-0.2,0.35)
            draw_character(ctx,"golu",900,1200+(1-kg)*500+bob(t,1.8),0.8,mouth=m("golu"),expr="star",t=t,look=(-1,-0.5),arm=("cheer","down"))
        if t>=P99-0.05 and t<K1-0.15:
            paint_text(ctx,"GAMES ₹99 SE START",W/2+60,1060,70,scale=k_in(t,P99,0.3,0.6),fill=(255,255,255),stroke=(60,20,0),font="Baloo2.ttf",grad=((255,245,150),(255,150,0)),glow=(255,190,40))
        if t>=K1-0.15:
            paint_text(ctx,"CHECK KARO",W/2,300,96,scale=k_in(t,K1-0.15,0.3,0.4),fill=(255,255,255),stroke=(0,40,70),font="LuckiestGuy.ttf",glow=(60,220,255))
            chip(ctx,"AVAILABLE EDITION",W/2,470,(80,220,255),k_in(t,K1,0.3,0.4),size=58)
            chip(ctx,"ACCESS DETAILS",W/2,610,(255,90,190),k_in(t,K2,0.3,0.4),size=58)
            chip(ctx,"PHIR ORDER",W/2,750,(255,210,63),k_in(t,K3,0.3,0.4),size=58)
    elif t<S_F: # PROOF
        bokeh_bg(ctx,t,"#0B6E4F","#04301F",seed=7,tint=(0.6,1,0.7))
        def proof(c,x,y,w,h):
            c.set_source_rgb(*hexc("#0E0E12")); c.rectangle(x,y,w,h); c.fill(); c.rectangle(x,y,w,60); c.set_source_rgb(1,1,1); c.fill()
            paint_text(c,"cheappcgames.in.net",x+w/2,y+31,28,fill=(60,60,70),stroke=(255,255,255),sw=0,font="Baloo2.ttf",pad=6)
            c.set_source_surface(PROOF[0],x+(w-PROOF[2])/2,y+120); c.paint()
        if t<C["10"]["start"]:
            draw_character(ctx,"nikki",W/2,880+bob(t,1.2),1.35,mouth=m("nikki"),expr="doubt",t=t,look=(0.6,-0.2),arm=("hip","phone"))
            paint_text(ctx,"PROOF?",W/2,360,170,scale=k_in(t,S_E+0.2,0.3,0.5),fill=(255,255,255),stroke=(10,90,50),font="LuckiestGuy.ttf",glow=(37,211,102),rot=-0.05)
        else:
            kp=k_in(t,C["10"]["start"],0.35)
            phone_with(ctx,W/2+150,600,500,700,kp,proof,rot=-0.03)
            draw_character(ctx,"raju",180,1180+bob(t,1.3),0.85,mouth=m("raju"),expr="normal",t=t,look=(1,-0.6),arm=("down","point"),blink=blink(t,0.9))
            chip(ctx,"WHATSAPP DELIVERY PROOFS",W/2+60,1030,(37,211,102),k_in(t,frac("10",0.2),0.3),size=40)
            chip(ctx,"2000+ HAPPY CUSTOMERS",W/2+60,1110,(255,133,161),k_in(t,frac("10",0.62),0.3,0.4),size=44)
    elif t<S_F2: # BACKUP
        room(ctx,t)
        draw_character(ctx,"golu",W/2,880+bob(t,1.6),1.3,mouth=m("golu"),expr="angry",t=t,look=(0,0.2),arm=("hold","hold"),blink=blink(t,0.3))
        kb=k_in(t,frac("11",0.55),0.35,0.5)
        if t>=frac("11",0.55):
            backup_drive(ctx,W/2,1150,kb,t)
            paint_text(ctx,"PEHLE BACKUP!",W/2,330,120,scale=kb,fill=(255,255,255),stroke=(0,40,90),font="LuckiestGuy.ttf",glow=(58,134,255))
    elif t<S_G: # URL
        bokeh_bg(ctx,t,"#3A0CA3","#14053A",seed=9,tint=(0.8,0.7,1))
        draw_character(ctx,"raju",W/2,900+bob(t,1.3),1.3,mouth=m("raju"),expr="normal",t=t,look=(0,-0.5),arm=("up","point"),blink=blink(t,0.5))
        ku=k_in(t,frac("12",0.5),0.35,0.4)
        paint_text(ctx,"cheappcgames.in.net",W/2,360,82,scale=ku*(1+0.03*math.sin(t*8)),fill=(30,25,28),stroke=(255,255,255),sw=0,font="Baloo2.ttf",box=(255,255,255),pad=22)
    elif t<END_CARD: # HAPPY GAMING
        burst_bg(ctx,t,c1="#FFD23F",c2="#FF9F1C",cy=600,speed=0.25)
        paint_text(ctx,"HAPPY GAMING!",W/2,380,130,scale=k_in(t,S_G,0.3,0.6),fill=(255,255,255),stroke=(120,40,0),font="LuckiestGuy.ttf",glow=(255,120,0),rot=-0.04)
        draw_character(ctx,"golu",200,1100+bob(t,2.4),0.95,mouth=m("golu"),expr="happy",t=t,arm=("cheer","cheer"))
        draw_character(ctx,"nikki",540,1050+bob(t,2.2,1),1.0,mouth=m("nikki"),expr="laugh",t=t,arm=("cheer","thumbs"))
        draw_character(ctx,"raju",880,1110+bob(t,2.0,2),0.95,mouth=m("raju"),expr="happy",t=t,arm=("pad","pad")); gamepad(ctx,880,1110+470*0.95,0.75)
        confetti(ctx,t,S_G,seed=4,n=110,dur=3)
    else:       # END CARD
        bokeh_bg(ctx,t,"#2A1B54","#0E0A20",seed=3,tint=(1,0.8,1))
        u=t-END_CARD
        paint_text(ctx,"YOUR NEXT GAME",W/2,520,104,scale=k_in(t,END_CARD,0.3),fill=(255,255,255),stroke=(40,20,70),font="LuckiestGuy.ttf")
        paint_text(ctx,"STARTS HERE",W/2,650,104,scale=k_in(t,END_CARD+0.12,0.3),fill=(255,255,255),stroke=(40,20,70),font="LuckiestGuy.ttf")
        paint_text(ctx,"GAMES FROM ₹99",W/2,860,120,scale=k_in(t,END_CARD+0.35,0.3,0.3),fill=(255,255,255),stroke=(60,20,0),font="Baloo2.ttf",grad=((255,245,150),(255,150,0)),glow=(255,190,40))
        paint_text(ctx,"cheappcgames.in.net",W/2,1060,66,scale=k_in(t,END_CARD+0.55,0.3),fill=(30,25,28),stroke=(255,255,255),sw=0,font="Baloo2.ttf",box=(255,255,255),pad=20)
    ctx.identity_matrix(); vignette(ctx)
    if t<END_CARD:
        flash(ctx,t,STARTS+[DEL_T],dur=0.1)
        paint_text(ctx,"CHEAP PC GAMES STORE",W/2-40,165,42,fill=(255,255,255),stroke=(40,25,70),font="LuckiestGuy.ttf",alpha=0.95)
        caption_draw(ctx,t)
    logo_badge(ctx,t)
    return surf

def srt(path):
    def ts(x):
        ms=int(round(x*1000)); h=ms//3600000; ms%=3600000; m_=ms//60000; ms%=60000; s_=ms//1000; ms%=1000
        return f"{h:02d}:{m_:02d}:{s_:02d},{ms:03d}"
    names={"golu":"Golu","raju":"Raju","nikki":"Nikki","all":"ALL"}
    with open(path,"w",encoding="utf-8") as f:
        for i,c in enumerate(caps,1): f.write(f"{i}\n{ts(c['start'])} --> {ts(c['end'])}\n{names[c['spk']]}: {c['text']}\n\n")
        f.write(f"{len(caps)+1}\n{ts(END_CARD)} --> {ts(END)}\nYOUR NEXT GAME STARTS HERE | GAMES FROM ₹99 | cheappcgames.in.net\n\n")

def thumbnail(path):
    surf=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); ctx=cairo.Context(surf); t=1.3
    room(ctx,t,0.35)
    draw_monitor(ctx,880,640,300,250,t+1,lambda c,x,y,w,h: (c.set_source_rgb(*hexc("#141830")),c.rectangle(x,y,w,h),c.fill()))
    draw_monitor(ctx,W/2,790,460,320,t,lambda c,x,y,w,h: (screen_deleted(c,x,y,w,h,DEL_T+1)))
    draw_character(ctx,"nikki",210,1000,0.95,expr="laugh",t=t,arm=("hip","down"))
    draw_character(ctx,"raju",880,1060,0.85,expr="normal",t=t,look=(-0.6,0.2),arm=("pad","pad")); gamepad(ctx,880,1060+470*0.85,0.68)
    draw_character(ctx,"golu",490,1240,1.22,expr="shock",t=t,look=(0,-0.4),arm=("head","head"))
    ctx.set_source_rgba(0.05,0.02,0.1,0.45); rrect(ctx,40,250,W-80,560,36); ctx.fill()
    paint_text(ctx,"MUMMY NE GAME",W/2,330,100,fill=(255,255,255),stroke=(30,10,50),font="LuckiestGuy.ttf")
    paint_text(ctx,"DELETE",W/2,505,230,fill=(255,255,255),stroke=(120,0,20),font="LuckiestGuy.ttf",glow=(255,40,60),rot=-0.03)
    paint_text(ctx,"KAR DIYA?!",W/2,680,110,fill=(255,210,63),stroke=(30,10,50),font="LuckiestGuy.ttf")
    w_,_=paint_text(ctx,"50 GB GONE!",W/2-45,1590,96,fill=(30,25,28),stroke=(255,210,63),sw=0,font="Baloo2.ttf",box=(255,210,63),pad=18)
    skull(ctx,W/2-45+w_/2+70,1590,46)
    vignette(ctx); logo_badge(ctx)
    surf.write_to_png(path); Image.open(path).convert("RGB").save(path.replace(".png",".jpg"),quality=93)

if __name__=="__main__":
    srt("out/reel004.srt")
    meta={"cover_ms":int(frac("01",0.9)*1000),"duration":END,"end_card":[END_CARD,END],"lines":[(c["id"],c["spk"],round(c["start"],2),round(c["end"],2)) for c in caps]}
    if "--thumb" in sys.argv: thumbnail("out/reel004_thumbnail.png"); sys.exit()
    if PREVIEW:
        pts=[("a",DEL_T+0.5),("b",X3+0.3),("c",CAP_T+0.6),("d",S_C2+0.6),("e",P99+0.5),("f",K3+0.4),("g",S_E+0.6),("h",frac("10",0.8)),("i",frac("11",0.8)),("j",frac("12",0.8)),("k",S_G+0.6),("l",END-0.5)]
        for n_,tt in pts: frame(tt).write_to_png(f"out/r6_{n_}.png")
        json.dump(meta,open("out/reel004_meta.json","w"),indent=1); print(json.dumps(meta)[:300]); sys.exit()
    encode(frame,NF,"out/reel004_mix.wav",OUT); json.dump(meta,open("out/reel004_meta.json","w"),indent=1); print("done",OUT)
