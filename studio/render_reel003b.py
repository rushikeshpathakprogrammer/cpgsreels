"""Reel 003 (final) - GTA VI PS5 deal. Approved dialogue verbatim. Original Vice-City-style neon art (no official artwork)."""
import math, sys, os, json, re
import numpy as np, cairo
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from draw import *
from reelkit import *
import sfx

AUD="audio/reel003b"; OUT=sys.argv[1] if len(sys.argv)>1 and not sys.argv[1].startswith("--") else "out/reel003b.mp4"
PREVIEW="--preview" in sys.argv
BPM=118; HB=60/BPM/2
# ---- APPROVED DIALOGUE (verbatim; used for subtitles/SRT) ----
DIALOGUE=[
 ("01","golu","STOP SCROLLING! GTA 6 aa raha hai… aur paisa udaane ki koi zaroorat nahi!"),
 ("02","raju","Jason, Lucia, Vice City… sabse bada GTA experience, 19 November ko launch ho raha hai!"),
 ("03","nikki","Toh PS5 pe khelne ke liye kya karein?"),
 ("04","raju","Cheap PC Games Store laaya hai teen PS5 access options!"),
 ("05","raju","ONE MONTH… sirf ₹1,300!"),
 ("06","golu","OFFLINE LIFETIME… ₹2,000!"),
 ("07","nikki","ONLINE LIFETIME… ₹3,000!"),
 ("08","all","Jo tumhare gaming style ko suit kare, wahi choose karo!"),
 ("09","nikki","Ek minute… scam toh nahi hai na?"),
 ("10","golu","Pichhla reel dekh! GST registered, Udyam registered, 2000+ happy customers!"),
 ("11","raju","Aur activation process, account setup, access conditions… sab website pe available hai. Order se pehle humse pooch bhi sakte ho!"),
 ("12","nikki","Matlab pata hai kya le rahe hain… no surprises!"),
 ("13","raju","GTA 6 aa raha hai 19 November ko! Launch offer limited time ke liye hai, availability ke hisaab se."),
 ("14","golu","Launch day ka wait mat karo!"),
 ("15","nikki","Abhi DM karo… 'GTA 6' likh ke!"),
]
HL=re.compile(r"(STOP|SCROLLING|GTA|6|PS5|₹|ONE|MONTH|OFFLINE|ONLINE|LIFETIME|JASON|LUCIA|VICE|CITY|19|NOVEMBER|TEEN|SCAM|GST|UDYAM|2000\+|WEBSITE|DM|LIMITED|TIME|NO|SURPRISES|STYLE|LAUNCH)",re.I)
def chunks_of(text):
    words=text.upper().replace("…","… ").split(); out=[]; cur=[]
    for w in words:
        cur.append(w)
        if len(cur)>=3 or w.endswith(("!","?","…",",",".")) and len(cur)>=2:
            out.append(cur); cur=[]
    if cur: out.append(cur)
    res=[]
    for c in out:
        res.append(" ".join(("*"+w+"*") if HL.search(w.strip("!?,.…'")) and len(w.strip("!?,.…'"))>0 else w for w in c))
    return res
def q(t): return math.ceil(t/HB)*HB

# ---- timeline (quantized to half-beat grid) ----
import subprocess, soundfile as sf
SPEED={"golu":1.1,"raju":1.12,"nikki":1.04}
def tighten(a, maxgap=0.16, thr_db=-38):
    hop=SR//100; e=np.array([np.sqrt(np.mean(a[i:i+hop]**2)) for i in range(0,len(a),hop)])
    thr=10**(thr_db/20)*e.max(); sil=e<thr; out=[]; i=0
    while i<len(sil):
        j=i
        while j<len(sil) and sil[j]==sil[i]: j+=1
        seg=a[i*hop:j*hop]
        if sil[i] and len(seg)>maxgap*SR: seg=np.concatenate([seg[:int(maxgap*SR/2)],seg[-int(maxgap*SR/2):]])
        out.append(seg); i=j
    return np.concatenate(out)
def load(i, spk):
    src=f"{AUD}/{i}.wav"; dst=f"out/v_{i}.wav"
    if not os.path.exists(dst):
        subprocess.run(["ffmpeg","-y","-loglevel","error","-i",src,"-af",f"rubberband=tempo={SPEED[spk]}:pitch=1.0","-ar",str(SR),dst],check=True)
    a=load_voice(dst); return tighten(a)
tl=[]; caps=[]; t=q(0.35)
GAP={"01":0.15,"02":0.12,"03":0.1,"04":0.12,"05":0.15,"06":0.15,"07":0.15,"08":0.15,"09":0.1,"10":0.12,"11":0.12,"12":0.12,"13":0.12,"14":0.08}
for lid,spk,text in DIALOGUE:
    if spk=="all":
        parts=[("golu",load("08a","golu")),("raju",load("08b","raju")),("nikki",load("08c","nikki"))]
        d=max(len(a) for _,a in parts)/SR
        for s_,a in parts: tl.append(dict(id=lid+s_,spk=s_,chunks=[],start=t,end=t+len(a)/SR,audio=a*0.75))
    else:
        a=load(lid,spk); d=len(a)/SR; tl.append(dict(id=lid,spk=spk,chunks=[],start=t,end=t+d,audio=a))
    caps.append(dict(id=lid,spk=spk if spk!="all" else "all",text=text,chunks=chunks_of(text),start=t,end=t+d))
    t=q(t+d+GAP.get(lid,0.12))
C={c["id"]:c for c in caps}
END_CARD=C["15"]["end"]+0.35; END=END_CARD+4.6
mx=Mixer(tl,END,["golu","raju","nikki"]); NF=mx.NF
print("duration",round(END,2))

def pause_end(lid):  # end of the '…' pause inside a line (price moment)
    a=[x for x in tl if x["id"]==lid][0]["audio"]; hop=SR//100
    e=np.array([np.sqrt(np.mean(a[i:i+hop]**2)) for i in range(0,len(a)-hop,hop)]); thr=0.06*e.max()
    sil=e<thr; best=(0,0); i=10
    while i<len(sil)-5:
        if sil[i]:
            j=i
            while j<len(sil) and sil[j]: j+=1
            if j-i>best[1]-best[0]: best=(i,j)
            i=j
        else: i+=1
    return C[lid]["start"]+best[1]*hop/SR
P1=pause_end("05"); P2=pause_end("06"); P3=pause_end("07")
S_B=C["02"]["start"]; S_C=C["03"]["start"]; S_D=C["05"]["start"]; S_E=C["09"]["start"]; S_E2=C["10"]["start"]; S_E3=C["11"]["start"]; S_E4=C["12"]["start"]; S_F=C["13"]["start"]
STARTS=[S_B,S_C,C["04"]["start"],S_D,S_E,S_E2,S_E3,S_E4,S_F,END_CARD]
GTA_HOOK=C["01"]["start"]+0.95
REEL_T=C["10"]["start"]+0.05
GST_T=C["10"]["start"]+0.30*(C["10"]["end"]-C["10"]["start"])
UDY_T=C["10"]["start"]+0.55*(C["10"]["end"]-C["10"]["start"])
CUS_T=C["10"]["start"]+0.78*(C["10"]["end"]-C["10"]["start"])

# ---- sound design (impacts on the beat grid) ----
music=sfx.synthwave_track(END+1,bpm=BPM)
mx.add(sfx.boom(),C["01"]["start"]-0.02,1.0); mx.add(sfx.boom(),GTA_HOOK,0.9)
for s in STARTS: mx.add(sfx.whoosh(),s-0.12,0.7)
for p in (P1,P2,P3): mx.add(sfx.boom(),p-0.03,1.15); mx.add(sfx.chaching(),p,0.55)
mx.add(sfx.stamp(),C["09"]["start"]+0.6,0.9)
mx.add(sfx.pop(),REEL_T,0.8)
for c in (GST_T,UDY_T,CUS_T): mx.add(sfx.stamp(),c,0.6)
mx.add(sfx.sparkle(),C["12"]["end"]-0.6,0.8)
mx.add(sfx.ticks(1.2),S_F+0.2,0.8); mx.add(sfx.boom(),END_CARD,0.9); mx.add(sfx.chaching(),END_CARD+0.3,0.6)
os.makedirs("out",exist_ok=True); mx.render("out/reel003b_mix.wav",music=music,music_gain=0.5)

# ---- assets ----
def img_surface(path,wmax=None,crop=None):
    im=Image.open(path).convert("RGBA")
    if crop: im=im.crop(crop)
    if wmax: r=wmax/im.width; im=im.resize((int(im.width*r),int(im.height*r)),Image.LANCZOS)
    a=np.array(im).astype(np.float32); al=a[...,3:4]/255
    bgra=np.ascontiguousarray(np.dstack([a[...,2:3]*al,a[...,1:2]*al,a[...,0:1]*al,a[...,3:4]]).astype(np.uint8))
    return (cairo.ImageSurface.create_for_data(memoryview(bgra),cairo.FORMAT_ARGB32,im.width,im.height,im.width*4),bgra,im.width,im.height)
REEL2=img_surface("assets/reel002_trust_cover.jpg",380)
HDR=img_surface("assets/site_about.png",520,crop=(0,0,1075,400))
PROOF=img_surface("assets/site_home.png",520,crop=(0,3380,1075,3820))

def blink(t,seed): return ((t+seed)%3.2)<0.12
bob=lambda t,f,ph=0,a=6: a*math.sin(t*2*math.pi*f+ph)
def beatpulse(t): ph=(t/(2*HB))%1; return math.exp(-ph*6)

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

def flip_calendar(ctx,cx,cy,t,t0,s=1.0):
    u=t-t0
    if u<0: return
    k=max(0.01,ease_out_back(u/0.3))
    day=min(19,1+int(max(0,u-0.1)/0.045)); flip=(u/0.045)%1 if day<19 else 1
    ctx.save(); ctx.translate(cx,cy); ctx.scale(k*s,k*s)
    rrect(ctx,-150,-170,300,340,30); fill_stroke(ctx,(1,1,1),8)
    ctx.save(); rrect(ctx,-150,-170,300,90,30); ctx.clip(); ctx.rectangle(-150,-170,300,90); ctx.set_source_rgb(*hexc("#E63946")); ctx.fill(); ctx.restore()
    for dx in (-80,80): rrect(ctx,dx-10,-190,20,50,10); fill_stroke(ctx,hexc("#2B2B33"),4)
    ctx.restore()
    paint_text(ctx,"NOV",cx,cy-125*k*s,58,scale=max(k*s,0.01),fill=(255,255,255),stroke=(230,57,70),sw=0,font="LuckiestGuy.ttf",pad=6)
    paint_text(ctx,str(day),cx,cy+40*k*s,170,scale=max(k*s*(0.85+0.15*flip),0.01),fill=(30,25,28),stroke=(255,255,255),sw=0,font="Baloo2.ttf",pad=6)

def check_badge(ctx,x,y,r):
    ellipse(ctx,x,y,r,r); fill_stroke(ctx,hexc("#2EC45A"),4)
    ctx.move_to(x-r*0.45,y); ctx.line_to(x-r*0.1,y+r*0.38); ctx.line_to(x+r*0.5,y-r*0.35)
    ctx.set_source_rgb(1,1,1); ctx.set_line_width(max(2,r*0.22)); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()

def chip(ctx,txt,cx,cy,col,k,size=46):
    if k<=0.01: return
    w_,_=paint_text(ctx,txt,cx-20*k,cy,size,scale=max(k,0.01),fill=(30,25,28),stroke=col,sw=0,font="Baloo2.ttf",box=col,pad=14)
    check_badge(ctx,cx-20*k+w_/2+6*k,cy,22*k)

def phone_with(ctx,cx,cy,w,h,k,draw_screen,rot=0.0):
    if k<=0.01: return
    ctx.save(); ctx.translate(cx,cy); ctx.scale(k,k); ctx.rotate(rot)
    draw_phone(ctx,0,0,w,h)
    ctx.save(); rrect(ctx,-w/2+22,-h/2+22,w-44,h-44,36); ctx.clip(); draw_screen(ctx,-w/2+22,-h/2+22,w-44,h-44); ctx.restore()
    ctx.restore()

def caption_draw(ctx,t,cy=1395,size=80):
    ln=None
    for c in caps:
        if c["start"]<=t<c["end"]: ln=c; break
    if not ln: return
    n=len(ln["chunks"]); dur=ln["end"]-ln["start"]
    lens=[len(c.replace("*",""))+4 for c in ln["chunks"]]; tot=sum(lens); acc=ln["start"]; idx=n-1; cst=acc
    for i,lx in enumerate(lens):
        seg=dur*lx/tot
        if t<acc+seg: idx=i; cst=acc; break
        acc+=seg
    k=ease_out_back((t-cst)/0.16)
    parts=[(w.replace("*",""),w.startswith("*")) for w in ln["chunks"][idx].split(" ")]
    def st(h): return dict(fill=(30,25,28) if h else (255,255,255), stroke=(255,210,63) if h else (25,20,22), sw=0 if h else 9, font="Baloo2.ttf", box=(255,210,63) if h else None, pad=12)
    items=[]; total=0
    for txt,h in parts:
        _,w,_,_=text_surface(txt,size,**st(h)); items.append((txt,h,w)); total+=w+4
    scale=min(1.0,(W-70)/total)*k; x=W/2-total*scale/2
    for txt,h,w in items: paint_text(ctx,txt,x+w*scale/2,cy,size,scale=scale,**st(h)); x+=(w+4)*scale
    col={"golu":(242,193,78),"raju":(47,165,138),"nikki":(255,93,143),"all":(255,255,255)}[ln["spk"]]
    name={"all":"GOLU + RAJU + NIKKI"}.get(ln["spk"],ln["spk"].upper())
    paint_text(ctx,name,W/2,cy-90,36,fill=(30,25,28),stroke=col,sw=0,font="LuckiestGuy.ttf",box=col,pad=10)

def frame(t):
    surf=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); ctx=cairo.Context(surf)
    last=max([0]+[s for s in STARTS if s<=t]); z=1+0.07*(1-ease_out((t-last)/0.28))
    shake=(0,0)
    for st_,dur,amp in [(C["01"]["start"],0.3,24),(GTA_HOOK,0.3,20),(P1,0.28,22),(P2,0.28,22),(P3,0.28,22),(C["09"]["start"]+0.6,0.2,12)]:
        if st_<=t<st_+dur: f_=1-(t-st_)/dur; shake=(amp*f_*math.sin(t*97),amp*0.7*f_*math.cos(t*83))
    if t<END_CARD:
        ctx.translate(W/2+shake[0],H/2+shake[1]); ctx.scale(z,z); ctx.translate(-W/2,-H/2)
    m=lambda k_: mx.mouth(k_,t)
    if t<S_B:   # HOOK
        synthwave(ctx,t)
        k1=ease_out_back((t-C["01"]["start"])/0.25)*(1.7-0.7*ease_out((t-C["01"]["start"])/0.2))
        paint_text(ctx,"STOP",W/2,330,170,scale=max(k1,0.01),fill=(255,255,255),stroke=(120,0,20),font="LuckiestGuy.ttf",glow=(255,40,60),rot=-0.04)
        paint_text(ctx,"SCROLLING!",W/2,480,120,scale=max(k1,0.01),fill=(255,255,255),stroke=(120,0,20),font="LuckiestGuy.ttf",glow=(255,40,60),rot=-0.04)
        k2=ease_out_back((t-GTA_HOOK)/0.25)*(1.8-0.8*ease_out((t-GTA_HOOK)/0.2))
        paint_text(ctx,"GTA 6",W/2,680,200,scale=max(k2,0.01),fill=(255,255,255),stroke=(40,0,60),font="Baloo2.ttf",glow=(255,60,170),rot=0.03)
        ki=ease_out_back((t-0.1)/0.35)
        draw_character(ctx,"golu",W/2,1110+(1-ki)*500+bob(t,3,0,8),1.2,mouth=m("golu"),expr="shock",t=t,look=(0,-0.6),arm=("up","cheer"))
    elif t<S_C: # HYPE
        synthwave(ctx,t); u=t-S_B; d=C["02"]["end"]-S_B
        for i,(nm,fr) in enumerate([("JASON",0.0),("LUCIA",0.12),("VICE CITY",0.24)]):
            kk=ease_out_back((u-fr*d)/0.25)
            paint_text(ctx,nm,W/2+(-200,200,0)[i],300+i*130,(96,96,104)[i],scale=max(kk,0.01),fill=(255,255,255),stroke=(0,40,70),font="LuckiestGuy.ttf",glow=(60,220,255) if i<2 else (255,60,170),rot=(-0.05,0.05,0)[i])
        flip_calendar(ctx,W/2+250,780,t,S_B+0.55*d,0.8)
        paint_text(ctx,"LAUNCH",W/2+250,960,62,scale=max(ease_out_back((u-0.75*d)/0.3),0.01),fill=(255,255,255),stroke=(120,0,40),font="LuckiestGuy.ttf",glow=(255,60,120))
        ki=ease_out((t-S_B)/0.3)
        draw_character(ctx,"raju",300-(1-ki)*600,1100+bob(t,1.4),1.1,mouth=m("raju"),expr="normal",t=t,look=(0.6,-0.6),arm=("down","point"),blink=blink(t,0.3))
    elif t<S_D: # REVEAL
        synthwave(ctx,t,dim=0.15)
        if t<C["04"]["start"]:
            backlight(ctx,W/2,900,500,(1,0.5,0.8),0.3)
            draw_character(ctx,"nikki",W/2,900+bob(t,1.2),1.35,mouth=m("nikki"),expr="normal",t=t,look=(0.3,-0.4),arm=("hip","phone"),blink=blink(t,0.8))
            paint_text(ctx,"?",W/2+330,420,200,scale=max(ease_out_back((t-S_C-0.3)/0.3),0.01),fill=(255,210,63),stroke=(40,0,60),font="LuckiestGuy.ttf",rot=0.2*math.sin(t*4))
        else:
            u=t-C["04"]["start"]
            k3=ease_out_back((u-0.9)/0.3)*(1.5-0.5*ease_out((u-0.9)/0.2))
            paint_text(ctx,"3",W/2,420,300,scale=max(k3,0.01),fill=(255,255,255),stroke=(60,20,0),font="Baloo2.ttf",grad=((255,245,150),(255,150,0)),glow=(255,190,40))
            paint_text(ctx,"PS5 ACCESS OPTIONS",W/2,640,80,scale=max(ease_out_back((u-1.2)/0.3),0.01),fill=(255,255,255),stroke=(0,40,70),font="LuckiestGuy.ttf",glow=(60,220,255))
            draw_character(ctx,"raju",W/2,1100+bob(t,1.4),1.15,mouth=m("raju"),expr="normal",t=t,look=(0,-0.6),arm=("up","point"),blink=blink(t,0.5))
    elif t<S_E: # PRICES
        synthwave(ctx,t,horizon=1150,sun=False,dim=0.25)
        paint_text(ctx,"GTA 6 • PS5",W/2,290,86,fill=(255,255,255),stroke=(40,0,60),font="Baloo2.ttf",glow=(255,60,170),scale=max(ease_out_back((t-S_D)/0.3),0.01))
        neon_card(ctx,W/2,470,930,205,t,P1,"1 MONTH","₹1,300",(0.3,0.9,1.0))
        neon_card(ctx,W/2,715,930,205,t,P2,"OFFLINE LIFETIME","₹2,000",(1.0,0.35,0.75))
        neon_card(ctx,W/2,960,930,205,t,P3,"ONLINE LIFETIME","₹3,000",(1.0,0.82,0.25))
        if t>=P3: confetti(ctx,t,P3+0.05,seed=21,n=60,dur=2.0)
        y0=1310; spk=active_line(tl,t)
        draw_character(ctx,"golu",190,y0+bob(t,1.6),0.8,mouth=m("golu"),expr="star" if t>P2 else "normal",t=t,look=(0.5,-1),arm=("cheer","down"),blink=blink(t,0.2))
        draw_character(ctx,"nikki",540,y0+30+bob(t,1.2,1),0.82,mouth=m("nikki"),expr="love" if t>P3+0.3 else "normal",t=t,look=(0,-1),arm=("down","thumbs"),blink=blink(t,1.1))
        draw_character(ctx,"raju",890,y0+bob(t,1.3,2),0.8,mouth=m("raju"),expr="normal",t=t,look=(-0.5,-1),arm=("point","down"),blink=blink(t,0.7))
    elif t<S_E2: # SCAM?
        bokeh_bg(ctx,t,"#3B0F4F","#12051F",seed=4,tint=(1,0.5,0.7))
        backlight(ctx,W/2,850,520,(1,0.4,0.6),0.3)
        draw_character(ctx,"nikki",W/2,880+bob(t,1.0),1.45,mouth=m("nikki"),expr="doubt",t=t,look=(0.6,-0.2),arm=("hip","hip"),blink=False)
        ks=ease_out_back((t-S_E-0.6)/0.25)*(1.6-0.6*ease_out((t-S_E-0.6)/0.2))
        paint_text(ctx,"SCAM?",W/2,360,190,scale=max(ks,0.01),fill=(255,255,255),stroke=(150,0,20),font="LuckiestGuy.ttf",glow=(255,40,60),rot=-0.08)
    elif t<S_E3: # Golu: previous reel + registrations
        bokeh_bg(ctx,t,"#3A2466","#140B2E",seed=5,tint=(1,0.9,0.6))
        kp=ease_out_back((t-REEL_T)/0.35)
        def scr(c,x,y,w,h):
            c.set_source_rgb(0,0,0); c.rectangle(x,y,w,h); c.fill()
            c.set_source_surface(REEL2[0],x+(w-REEL2[2])/2,y+(h-REEL2[3])/2); c.paint()
            ellipse(c,x+w/2,y+h/2,52,52); c.set_source_rgba(0,0,0,0.5); c.fill()
            c.move_to(x+w/2-16,y+h/2-28); c.line_to(x+w/2+28,y+h/2); c.line_to(x+w/2-16,y+h/2+28); c.close_path(); c.set_source_rgb(1,1,1); c.fill()
        phone_with(ctx,W/2-150,640,420,760,kp,scr,rot=-0.03)
        paint_text(ctx,"PICHHLA REEL",W/2-150,250,56,scale=max(kp,0.01)*(1+0.04*math.sin(t*8)),fill=(30,25,28),stroke=(255,210,63),sw=0,font="LuckiestGuy.ttf",box=(255,210,63),pad=12)
        draw_character(ctx,"golu",W/2+360,1230+bob(t,1.6),0.68,mouth=m("golu"),expr="normal",t=t,look=(-1,-0.6),arm=("point","down"),blink=blink(t,0.4))
        chip(ctx,"GST REGISTERED",W/2,1080,(255,210,63),ease_out_back((t-GST_T)/0.3),size=42)
        chip(ctx,"UDYAM REGISTERED",W/2,1158,(59,206,172),ease_out_back((t-UDY_T)/0.3),size=42)
        chip(ctx,"2000+ HAPPY CUSTOMERS",W/2,1236,(255,133,161),ease_out_back((t-CUS_T)/0.3),size=40)
        kh=ease_out_back((t-UDY_T-0.15)/0.3)
        if kh>0.01:  # real website header showing the Udyam registration number
            ctx.save(); ctx.translate(W/2+275,600); ctx.scale(kh*0.8,kh*0.8); ctx.rotate(0.03)
            rrect(ctx,-HDR[2]/2-8,-HDR[3]/2-8,HDR[2]+16,HDR[3]+16,14); fill_stroke(ctx,(1,1,1),6)
            ctx.set_source_surface(HDR[0],-HDR[2]/2,-HDR[3]/2); ctx.paint(); ctx.restore()
            paint_text(ctx,"AS SHOWN ON OUR WEBSITE",W/2+275,790,30,scale=max(kh,0.01),fill=(255,255,255),stroke=(20,5,40),sw=4,font="Baloo2.ttf",pad=6)
    elif t<S_E4: # Raju: real website
        bokeh_bg(ctx,t,"#0B4F6C","#04202E",seed=6,tint=(0.6,0.9,1))
        u=t-S_E3; d=C["11"]["end"]-S_E3
        def site(c,x,y,w,h):
            c.set_source_rgb(*hexc("#0E0E12")); c.rectangle(x,y,w,h); c.fill()
            c.rectangle(x,y,w,64); c.set_source_rgb(1,1,1); c.fill()
            paint_text(c,"cheappcgames.in.net",x+w/2,y+33,30,fill=(60,60,70),stroke=(255,255,255),sw=0,font="Baloo2.ttf",pad=6)
            sc=min(1.0,u/2.5)*max(0,PROOF[3]+HDR[3]-h+140)
            c.save(); c.translate(0,-sc)
            c.set_source_surface(HDR[0],x+(w-HDR[2])/2,y+70); c.paint()
            c.set_source_surface(PROOF[0],x+(w-PROOF[2])/2,y+70+HDR[3]+20); c.paint()
            c.restore()
        kp=ease_out_back((u-0.05)/0.35)
        phone_with(ctx,W/2+90,600,540,820,kp,site)
        draw_character(ctx,"raju",150,1230+bob(t,1.3),0.68,mouth=m("raju"),expr="normal",t=t,look=(1,-0.6),arm=("down","point"),blink=blink(t,0.6))
        for i,(txt,col) in enumerate([("ACTIVATION PROCESS",(80,220,255)),("ACCOUNT SETUP",(255,90,190)),("ACCESS CONDITIONS",(255,210,63))]):
            kk=ease_out_back((u-(0.12+i*0.1)*d)/0.3)
            chip(ctx,txt,W/2,1075+i*76,col,kk,size=38)
        kw=ease_out_back((u-0.62*d)/0.3)
        paint_text(ctx,"ORDER SE PEHLE POOCHO",W/2+90,900,46,scale=max(kw,0.01),fill=(255,255,255),stroke=(10,90,50),font="Baloo2.ttf",box=(37,211,102),pad=14)
    elif t<S_F: # Nikki convinced
        bokeh_bg(ctx,t,"#FF85A1","#7B1F4B",seed=7,tint=(1,1,1))
        backlight(ctx,W/2,850,520,(1,1,1),0.3)
        draw_character(ctx,"nikki",W/2,880+bob(t,2),1.4,mouth=m("nikki"),expr="love",t=t,arm=("down","thumbs"))
        kn=ease_out_back((t-C["12"]["end"]+0.9)/0.3)
        w_,_=paint_text(ctx,"NO SURPRISES",W/2-25,340,96,scale=max(kn,0.01),fill=(255,255,255),stroke=(120,0,60),font="LuckiestGuy.ttf",glow=(255,120,180))
        if kn>0.05: check_badge(ctx,W/2-25+w_/2+40*kn,340,40*kn)
    elif t<END_CARD: # FOMO
        synthwave(ctx,t,dim=0.1); u=t-S_F
        flip_calendar(ctx,W/2,520,t,S_F+0.15,1.0)
        paint_text(ctx,"LAUNCH COUNTDOWN",W/2,290,76,scale=max(ease_out_back((u-0.1)/0.3),0.01),fill=(255,255,255),stroke=(0,40,70),font="LuckiestGuy.ttf",glow=(60,220,255))
        kl=ease_out_back((u-1.6)/0.3); pl=1+0.06*beatpulse(t)
        paint_text(ctx,"LIMITED-TIME LAUNCH OFFER",W/2,790,64,scale=max(kl,0.01)*pl,fill=(30,25,28),stroke=(255,210,63),sw=0,font="LuckiestGuy.ttf",box=(255,210,63),pad=16)
        paint_text(ctx,"*Subject to availability",W/2,875,38,scale=max(kl,0.01),fill=(255,255,255),stroke=(20,5,40),sw=4,font="Baloo2.ttf",pad=6)
        if t>=C["14"]["start"]-0.1:
            draw_character(ctx,"golu",220,1180+bob(t,2.4),0.95,mouth=m("golu"),expr="shock" if t<C["15"]["start"] else "happy",t=t,arm=("up","down"))
        if t>=C["15"]["start"]-0.15:
            kd=ease_out_back((t-C["15"]["start"]+0.15)/0.3)
            draw_character(ctx,"nikki",820,1180+(1-kd)*500+bob(t,2,1),0.95,mouth=m("nikki"),expr="normal",t=t,arm=("down","phone"))
            paint_text(ctx,"DM “GTA 6”",W/2+60,1000,84,scale=max(kd,0.01)*(1+0.05*beatpulse(t)),fill=(255,255,255),stroke=(120,0,60),font="Baloo2.ttf",glow=(255,90,190))
        if t<C["14"]["start"]-0.1:
            draw_character(ctx,"raju",W/2,1180+bob(t,1.3),1.0,mouth=m("raju"),expr="normal",t=t,look=(0,-0.6),arm=("point","down"),blink=blink(t,0.9))
    else:       # FINAL END CARD (static-readable)
        synthwave(ctx,t,dim=0.55); u=t-END_CARD
        ctx.set_source_rgba(0.03,0.0,0.08,0.55); rrect(ctx,70,250,W-140,1330,40); ctx.fill()
        rows=[("CHEAP PC GAMES STORE",330,62,"LuckiestGuy.ttf",(255,255,255),(255,60,170)),
              ("GTA VI — PS5",460,104,"Baloo2.ttf",(255,255,255),(255,60,170))]
        for i,(txt,y,sz,f,fill,gl) in enumerate(rows):
            paint_text(ctx,txt,W/2,y,sz,scale=max(ease_out_back((u-i*0.12)/0.3),0.01),fill=fill,stroke=(20,5,40),font=f,glow=gl)
        prices=[("1 MONTH","₹1,300",(80,220,255)),("OFFLINE LIFETIME","₹2,000",(255,90,190)),("ONLINE LIFETIME","₹3,000",(255,210,63))]
        for i,(lab,pr,col) in enumerate(prices):
            kk=max(ease_out_back((u-0.3-i*0.12)/0.3),0.01); y=650+i*170
            paint_text(ctx,lab,W/2,y-42,52,scale=kk,fill=(255,255,255),stroke=(20,5,40),font="LuckiestGuy.ttf")
            paint_text(ctx,pr,W/2,y+42,96,scale=kk,fill=(255,255,255),stroke=(20,5,40),font="Baloo2.ttf",glow=col,sw=5)
        kb=max(ease_out_back((u-0.75)/0.3),0.01)*(1+0.04*beatpulse(t))
        paint_text(ctx,"DM “GTA 6” NOW",W/2,1240,92,scale=kb,fill=(30,25,28),stroke=(255,210,63),sw=0,font="Baloo2.ttf",box=(255,210,63),pad=22)
        paint_text(ctx,"cheappcgames.in.net",W/2,1390,48,scale=max(ease_out_back((u-0.9)/0.3),0.01),fill=(255,255,255),stroke=(20,5,40),sw=4,font="Baloo2.ttf")
    ctx.identity_matrix()
    vignette(ctx)
    if t<END_CARD:
        flash(ctx,t,STARTS+[GTA_HOOK,P1,P2,P3],dur=0.1)
        paint_text(ctx,"CHEAP PC GAMES STORE",W/2,165,42,fill=(255,255,255),stroke=(40,25,70),font="LuckiestGuy.ttf",alpha=0.95)
        caption_draw(ctx,t)
    return surf

def srt(path):
    def ts(x):
        ms=int(round(x*1000)); h=ms//3600000; ms%=3600000; m_=ms//60000; ms%=60000; s_=ms//1000; ms%=1000
        return f"{h:02d}:{m_:02d}:{s_:02d},{ms:03d}"
    names={"golu":"Golu","raju":"Raju","nikki":"Nikki","all":"Golu + Raju + Nikki"}
    with open(path,"w",encoding="utf-8") as f:
        for i,c in enumerate(caps,1):
            f.write(f"{i}\n{ts(c['start'])} --> {ts(c['end'])}\n{names[c['spk']]}: {c['text']}\n\n")
        f.write(f"{len(caps)+1}\n{ts(END_CARD)} --> {ts(END)}\nCHEAP PC GAMES STORE | GTA VI — PS5 | 1 MONTH — ₹1,300 | OFFLINE LIFETIME — ₹2,000 | ONLINE LIFETIME — ₹3,000 | DM \"GTA 6\" NOW\n\n")

if __name__=="__main__" and "--thumb" not in sys.argv:
    meta={"cover_ms":int((P3+1.2)*1000),"duration":END,"end_card":[END_CARD,END],"prices":[P1,P2,P3],
          "lines":[(c["id"],c["spk"],round(c["start"],2),round(c["end"],2)) for c in caps]}
    srt("out/reel003b.srt")
    if PREVIEW:
        pts=[("a",C["01"]["start"]+1.3),("b",C["02"]["end"]-0.3),("c",C["04"]["end"]-0.2),("d",P3+0.8),("e",C["09"]["end"]-0.2),("f",CUS_T+0.6),("g",C["11"]["end"]-0.5),("h",C["12"]["end"]-0.2),("i",C["15"]["end"]-0.2),("j",END-0.5)]
        for n_,tt in pts: frame(tt).write_to_png(f"out/r4_{n_}.png")
        json.dump(meta,open("out/reel003b_meta.json","w"),indent=1); print(json.dumps(meta)[:600]); sys.exit()
    encode(frame,NF,"out/reel003b_mix.wav",OUT); json.dump(meta,open("out/reel003b_meta.json","w"),indent=1); print("done",OUT)

def thumbnail(path):
    surf=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); ctx=cairo.Context(surf); t=2.0
    synthwave(ctx,t)
    paint_text(ctx,"CHEAP PC GAMES STORE",W/2,170,46,fill=(255,255,255),stroke=(40,25,70),font="LuckiestGuy.ttf")
    paint_text(ctx,"GTA 6",W/2,370,250,fill=(255,255,255),stroke=(40,0,60),font="Baloo2.ttf",glow=(255,60,170),rot=-0.04)
    paint_text(ctx,"PS5",W/2+300,520,80,fill=(30,25,28),stroke=(255,255,255),sw=0,font="LuckiestGuy.ttf",box=(80,220,255),pad=14,rot=0.06)
    paint_text(ctx,"3 PLANS",W/2,640,110,fill=(255,255,255),stroke=(60,20,0),font="LuckiestGuy.ttf",grad=((255,245,150),(255,150,0)),glow=(255,190,40))
    for i,(lab,pr,col) in enumerate([("1 MONTH","₹1,300",(80,220,255)),("OFFLINE LIFETIME","₹2,000",(255,90,190)),("ONLINE LIFETIME","₹3,000",(255,210,63))]):
        y=800+i*125
        paint_text(ctx,lab,W/2-170,y,50,fill=(255,255,255),stroke=(20,5,40),font="LuckiestGuy.ttf")
        paint_text(ctx,pr,W/2+270,y,92,fill=(255,255,255),stroke=(20,5,40),font="Baloo2.ttf",glow=col,sw=5)
    draw_character(ctx,"golu",210,1330,0.85,expr="shock",t=t,arm=("up","down"))
    draw_character(ctx,"nikki",540,1290,0.9,expr="love",t=t,arm=("down","thumbs"))
    draw_character(ctx,"raju",880,1340,0.85,expr="normal",t=t,look=(-0.3,-0.5),arm=("point","down"))
    paint_text(ctx,"DM “GTA 6”",W/2,1250,84,fill=(30,25,28),stroke=(255,210,63),sw=0,font="Baloo2.ttf",box=(255,210,63),pad=20)
    vignette(ctx)
    surf.write_to_png(path)

if "--thumb" in sys.argv:
    thumbnail("out/reel003b_thumbnail.png")
    Image.open("out/reel003b_thumbnail.png").convert("RGB").save("out/reel003b_thumbnail.jpg",quality=92)
