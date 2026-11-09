"""Reel 007 - 'MUMMY NE GAME DELETE KAR DIYA' (approved script, verbatim subtitles)."""
import math, sys, os, json, re
import numpy as np, cairo, soundfile as sf, colorsys
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from draw import *
from reelkit import *
import sfx

AUD="audio/reel007"; OUT=sys.argv[1] if len(sys.argv)>1 and not sys.argv[1].startswith("--") else "out/reel007.mp4"
PREVIEW="--preview" in sys.argv; BPM=128; HB=60/BPM/4
DIALOGUE=[
 ("01","golu","BHAI! MAINE GAME KHAREED LI... PAR 10% DISCOUNT LAGANA BHOOL GAYA!"),
 ("02","nikki","HAYE RAM! Itni jaldi kya thi tujhe?!"),
 ("03","golu","AB KYA KARU?!"),
 ("04","raju","ABE PAGAL! DIWALI OFFER ABHI LIVE HAI!"),
 ("05","golu","SACHIII?!"),
 ("06","raju","Cheap PC Games Store pe games ₹99 se start hote hain. Checkout pe DIWALI10 lagao aur pao instant 10% OFF!"),
 ("07","nikki","Aur minimum purchase?"),
 ("08","raju","KOI MINIMUM PURCHASE NAHI!"),
 ("09","golu","TOH JALDI KARO DOSTON!"),
 ("10","raju","Offer sirf 12 November tak hai!"),
 ("11","all","ABHI SHOP KARO!"),
]
HL=re.compile(r"^(BHOOL|GAYA|HAYE|RAM|PAGAL|LIVE|SACHIII|JALDI|DIWALI|PATAKHE|DISCOUNT|OFFER|RAJU|DHAMAKA|₹99|CHEAP|PC|GAMES|STORE|COUPON|DIWALI10|INSTANT|10%|OFF|MINIMUM|PURCHASE|ZERO|BHAROSA|GST|UDYAM|2000\+|WHATSAPP|DELIVERY|PROOFS|12|NOVEMBER|SHOP|KYUN)$")
def chunks_of(text):
    words=text.upper().replace("…","… ").replace("...","... ").split(); out=[]; cur=[]
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
GAP={"01":0.12,"02":0.08,"03":0.15,"04":0.08,"05":0.15,"06":0.12,"07":0.08,"08":0.15,"09":0.08,"10":0.15}
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
END_CARD=C["11"]["end"]+0.9; END=END_CARD+5.2
mx=Mixer(tl,END,["golu","raju","nikki"]); NF=mx.NF
print("duration",round(END,2))
def frac(lid,f): c=C[lid]; return c["start"]+f*(c["end"]-c["start"])
S_B=C["02"]["start"]; S_B2=C["03"]["start"]; S_C=C["04"]["start"]; S_C2=C["05"]["start"]; S_D=C["06"]["start"]; S_D1=C["06"]["start"]+0.5*(C["06"]["end"]-C["06"]["start"]); S_D2=C["07"]["start"]; S_D3=C["08"]["start"]; S_E=C["09"]["start"]; S_E2=C["10"]["start"]; S_G=C["11"]["start"]
STARTS=[S_B,S_B2,S_C,S_C2,S_D,S_D1,S_D2,S_D3,S_E,S_E2,S_G,END_CARD]
BHOOL=frac("01",0.7); LIVE_T=frac("04",0.55); P99=frac("06",0.38); CODE_T=frac("06",0.58); PCT_T=frac("06",0.86); ZERO_T=frac("08",0.3); DATE_T=frac("10",0.4)
mx.add(sfx.error_buzz(),0.25,0.8); mx.add(sfx.boom(),BHOOL,0.9); mx.add(sfx.sad_trombone(),C["01"]["end"]+0.02,0.7)
for s in STARTS: mx.add(sfx.whoosh(),s-0.1,0.65)
mx.add(sfx.boing(),S_B2,0.5); mx.add(sfx.boom(),LIVE_T,0.8); mx.add(sfx.sparkle(),S_C2,0.8)
mx.add(sfx.chaching(),P99,0.9); mx.add(sfx.riser(0.5),CODE_T-0.5,0.8); mx.add(sfx.boom(),CODE_T,0.8); mx.add(sfx.boom(),PCT_T,1.0); mx.add(sfx.chaching(),PCT_T+0.05,0.7)
mx.add(sfx.stamp(),ZERO_T,1.0); mx.add(sfx.ticks(1.0),DATE_T-0.6,0.7); mx.add(sfx.stamp(),DATE_T+0.4,0.8)
mx.add(sfx.boom(),S_G,0.7); mx.add(sfx.sparkle(),S_G,0.9); mx.add(sfx.chaching(),END_CARD+0.3,0.7)
os.makedirs("out",exist_ok=True); mx.render("out/reel007_mix.wav",bpm=BPM,music_gain=0.36)

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

def checkout_screen(c,x,y,w,h,t,applied=False):
    c.set_source_rgb(*hexc("#F4F5FA")); c.rectangle(x,y,w,h); c.fill()
    c.rectangle(x,y,w,h*0.13); c.set_source_rgb(*hexc("#3A0CA3")); c.fill()
    paint_text(c,"CHECKOUT",x+w/2,y+h*0.065,int(h*0.07),fill=(255,255,255),stroke=(58,12,163),sw=0,font="LuckiestGuy.ttf",pad=4)
    for i in range(2):
        rrect(c,x+w*0.06,y+h*(0.2+i*0.12),w*0.88,h*0.09,10); c.set_source_rgb(1,1,1); c.fill()
        rrect(c,x+w*0.09,y+h*(0.225+i*0.12),w*0.16,h*0.045,6); c.set_source_rgb(*hexc(["#F72585","#4CC9F0"][i])); c.fill()
        rrect(c,x+w*0.3,y+h*(0.235+i*0.12),w*0.4,h*0.025,6); c.set_source_rgba(0,0,0,0.25); c.fill()
    rrect(c,x+w*0.06,y+h*0.47,w*0.6,h*0.1,10); c.set_source_rgb(1,1,1); c.fill_preserve(); c.set_source_rgb(*hexc("#E63946") if not applied else hexc("#2EC45A")); c.set_line_width(4); c.stroke()
    paint_text(c,"COUPON CODE" if not applied else "DIWALI10",x+w*0.36,y+h*0.52,int(h*0.045),fill=(150,150,160) if not applied else (30,25,28),stroke=(255,255,255),sw=0,font="Baloo2.ttf",pad=4)
    rrect(c,x+w*0.69,y+h*0.47,w*0.25,h*0.1,10); c.set_source_rgb(*hexc("#3A0CA3")); c.fill()
    paint_text(c,"APPLY",x+w*0.815,y+h*0.52,int(h*0.045),fill=(255,255,255),stroke=(58,12,163),sw=0,font="LuckiestGuy.ttf",pad=4)
    if not applied:
        bl=0.6+0.4*math.sin(t*10)
        paint_text(c,"NOT APPLIED",x+w*0.36,y+h*0.62,int(h*0.045),fill=(230,57,70),stroke=(244,245,250),sw=0,font="LuckiestGuy.ttf",pad=4,alpha=bl)
    rrect(c,x+w*0.06,y+h*0.72,w*0.88,h*0.16,14); c.set_source_rgb(*hexc("#2EC45A")); c.fill()
    paint_text(c,"ORDER PLACED",x+w/2,y+h*0.8,int(h*0.065),fill=(255,255,255),stroke=(46,196,90),sw=0,font="LuckiestGuy.ttf",pad=4)

def live_badge(ctx,x,y,k,t):
    if k<=0.02: return
    w_,_=paint_text(ctx,"   LIVE",x,y,64,scale=k,fill=(255,255,255),stroke=(200,20,40),sw=0,font="LuckiestGuy.ttf",box=(230,57,70),pad=16)
    ellipse(ctx,x-w_/2+40*k,y,12*k*(0.8+0.3*abs(math.sin(t*5))),12*k*(0.8+0.3*abs(math.sin(t*5)))); ctx.set_source_rgb(1,1,1); ctx.fill()

def frame(t):
    surf=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); ctx=cairo.Context(surf)
    last=max([0]+[s for s in STARTS if s<=t]); z=1+0.07*(1-ease_out((t-last)/0.28)); shake=(0,0)
    for st_,dur,amp in [(BHOOL,0.35,24),(S_C,0.25,14),(PCT_T,0.3,22),(ZERO_T,0.25,16)]:
        if st_<=t<st_+dur: f_=1-(t-st_)/dur; shake=(amp*f_*math.sin(t*97),amp*0.7*f_*math.cos(t*83))
    if t<END_CARD: ctx.translate(W/2+shake[0],H/2+shake[1]); ctx.scale(z,z); ctx.translate(-W/2,-H/2)
    m=lambda k_: mx.mouth(k_,t)
    if t<S_B:   # HOOK: checkout done, coupon not applied
        room(ctx,t,alert=(0.5+0.5*math.sin(t*12)) if t>=BHOOL else 0)
        for i,x in enumerate([90,990]): diya(ctx,x,1230,0.6,t,seed=i)
        draw_monitor(ctx,640,700,560,420,t,lambda c,x,y,w,h: checkout_screen(c,x,y,w,h,t))
        draw_character(ctx,"golu",240,900+bob(t,2.5,0,6),1.08,mouth=m("golu"),expr="happy" if t<0.8 else "shock",t=t,look=(1,-0.2),arm=("down","down") if t<BHOOL-0.4 else ("head","head"))
        desk(ctx,t)
        if t>=BHOOL-0.1:
            paint_text(ctx,"10% DISCOUNT",W/2,300,110,scale=k_in(t,BHOOL-0.1,0.25,0.5),fill=(255,255,255),stroke=(80,20,0),font="Baloo2.ttf",grad=((255,245,150),(255,140,0)),glow=(255,170,40),rot=-0.04)
            paint_text(ctx,"BHOOL GAYA!",W/2,440,96,scale=k_in(t,BHOOL+0.1,0.25,0.6),fill=(255,255,255),stroke=(120,0,20),font="LuckiestGuy.ttf",glow=(255,40,60),rot=0.03)
    elif t<S_C: # HAYE RAM / AB KYA KARU
        if t<S_B2:
            diwali_bg(ctx,t,fw=False)
            draw_character(ctx,"golu",220,1070+bob(t,1.0),0.82,mouth=m("golu"),expr="cry",t=t,arm=("head","head"))
            draw_character(ctx,"nikki",740,880+bob(t,1.6,1),1.38,mouth=m("nikki"),expr="shock" if t<S_B+0.7 else "laugh",t=t,look=(-1,0),arm=("head","down") if t<S_B+0.7 else ("hip","down"),blink=False)
            paint_text(ctx,"HAYE RAM!",W/2,330,140,scale=k_in(t,S_B+0.05,0.25,0.6),fill=(255,255,255),stroke=(120,0,60),font="LuckiestGuy.ttf",glow=(255,90,190),rot=-0.04)
        else:
            burst_bg(ctx,t,c1="#4A4E69",c2="#22223B",cy=700,speed=0.1)
            draw_character(ctx,"golu",W/2,880+bob(t,3,0,8),1.45,mouth=m("golu"),expr="cry",t=t,arm=("head","head"))
            qmarks(ctx,t,W/2,700,n=6,R=380)
            paint_text(ctx,"AB KYA KARU?!",W/2,330,124,scale=k_in(t,S_B2,0.25,0.6),fill=(255,255,255),stroke=(40,20,70),font="LuckiestGuy.ttf",glow=(120,160,255))
    elif t<S_D: # RAJU ENTRY / SACHIII
        if t<S_C2:
            diwali_bg(ctx,t,fw=t>=LIVE_T)
            ki=ease_out((t-S_C)/0.3)
            draw_character(ctx,"golu",830,1080+bob(t,1.0),0.8,mouth=m("golu"),expr="cry",t=t,look=(-1,0))
            draw_character(ctx,"raju",320-(1-ki)*700,900+bob(t,1.3),1.28,mouth=m("raju"),expr="smirk",t=t,look=(1,0),arm=("hip","point"),blink=False)
            paint_text(ctx,"ABE PAGAL!",W/2,300,110,scale=k_in(t,S_C+0.05,0.25,0.5),fill=(255,255,255),stroke=(0,60,50),font="LuckiestGuy.ttf",glow=(47,165,138),rot=-0.05)
            if t>=LIVE_T-0.1:
                paint_text(ctx,"DIWALI OFFER",W/2,450,92,scale=k_in(t,LIVE_T-0.1,0.3,0.4),fill=(255,255,255),stroke=(80,20,0),font="LuckiestGuy.ttf",grad=((255,245,150),(255,140,0)),glow=(255,170,40))
                live_badge(ctx,W/2,570,k_in(t,LIVE_T+0.1,0.3,0.5),t)
        else:
            burst_bg(ctx,t,c1="#FFB703",c2="#FB8500",cy=700,speed=0.35)
            draw_character(ctx,"golu",W/2,900-abs(math.sin(t*9))*30,1.5,mouth=m("golu"),expr="excited",t=t,arm=("cheer","cheer"))
            paint_text(ctx,"SACHIII?!",W/2,330,150,scale=k_in(t,S_C2,0.25,0.7),fill=(255,255,255),stroke=(120,40,0),font="LuckiestGuy.ttf",glow=(255,120,0),rot=0.05)
    elif t<S_D2: # OFFER REVEAL: website (₹99) then coupon
        if t<S_D1:
            diwali_bg(ctx,t,fw=False,lanterns=False,diyas=False)
            u=t-S_D-0.2; d=S_D1-S_D-0.2
            sc=(SITE_NEW_Y+150)*ease_in_out(min(max(u/(d*0.9),0),1)) if u>0 else 0
            phone_with(ctx,W/2,822,1000,1064,k_in(t,S_D,0.35),lambda c,x,y,w,h: site_screen(c,x,y,w,h,sc))
            pip(ctx,"raju",118,300,92,t,"smirk",m("raju"),look=(1,0.2),ring=(47/255,165/255,138/255))
            if t>=P99-0.05:
                kq=k_in(t,P99,0.3,0.6); ctx.set_source_rgba(0.05,0.02,0.1,0.78*min(1,kq)); rrect(ctx,90,1170,W-180,120,30); ctx.fill()
                paint_text(ctx,"GAMES ₹99 SE START",W/2,1230,72,scale=kq,fill=(255,255,255),stroke=(60,20,0),font="Baloo2.ttf",grad=((255,245,150),(255,150,0)),glow=(255,190,40))
        else:
            diwali_bg(ctx,t,fw=t>=PCT_T)
            paint_text(ctx,"CHECKOUT PE LAGAO",W/2,320,76,scale=k_in(t,S_D1+0.05,0.3),fill=(255,255,255),stroke=(40,20,70),font="LuckiestGuy.ttf")
            kc=k_in(t,CODE_T,0.35,0.5); coupon_ticket(ctx,W/2,590,860,280,kc,t)
            if kc>0.05:
                ctx.save(); ctx.translate(W/2,590); ctx.rotate(-0.05+0.02*math.sin(t*3)); ctx.translate(-W/2,-590)
                paint_text(ctx,"DIWALI10",W/2-70,590,128,scale=kc,fill=(30,25,28),stroke=(255,210,63),sw=0,font="Baloo2.ttf",pad=8)
                paint_text(ctx,"CODE",W/2+330,590,40,scale=kc,fill=(30,25,28),stroke=(255,210,63),sw=0,font="LuckiestGuy.ttf",pad=6,rot=-1.5708)
                ctx.restore()
            if t>=PCT_T: paint_text(ctx,"10% OFF",W/2,880,190,scale=k_in(t,PCT_T,0.3,0.7),fill=(255,255,255),stroke=(80,20,0),font="Baloo2.ttf",grad=((255,245,150),(255,140,0)),glow=(255,170,40),rot=-0.03)
            if t>=PCT_T+0.2: paint_text(ctx,"INSTANT",W/2,1040,62,scale=k_in(t,PCT_T+0.2,0.3),fill=(30,25,28),stroke=(255,255,255),sw=0,font="LuckiestGuy.ttf",box=(255,255,255),pad=14)
            draw_character(ctx,"raju",160,1290+bob(t,1.3),0.7,mouth=m("raju"),expr="smirk",t=t,look=(1,-0.6),arm=("down","point"),blink=False)
    elif t<S_D3: # Nikki: minimum purchase?
        diwali_bg(ctx,t,fw=False)
        draw_character(ctx,"nikki",W/2,880+bob(t,1.2),1.42,mouth=m("nikki"),expr="doubt",t=t,look=(0.5,-0.2),arm=("hip","hip"))
        paint_text(ctx,"MINIMUM PURCHASE?",W/2,330,92,scale=k_in(t,S_D2+0.1,0.3,0.4),fill=(255,255,255),stroke=(120,0,60),font="LuckiestGuy.ttf",glow=(255,90,190))
    elif t<S_E: # NO MINIMUM
        diwali_bg(ctx,t,fw=True)
        draw_character(ctx,"raju",290,940+bob(t,1.3),1.2,mouth=m("raju"),expr="smirk",t=t,look=(1,-0.3),arm=("down","point"),blink=False)
        draw_character(ctx,"nikki",860,1090+bob(t,1.6,1),0.82,mouth=m("nikki"),expr="love",t=t,arm=("down","thumbs"))
        kz=k_in(t,ZERO_T,0.25,0.9)
        if t>=ZERO_T:
            ctx.save(); ctx.translate(W/2+60,470); ctx.rotate(-0.08); ctx.scale(kz,kz)
            rrect(ctx,-380,-150,760,300,40); ctx.set_source_rgba(0.95,0.25,0.3,0.12); ctx.fill_preserve(); ctx.set_source_rgb(*hexc("#2EC45A")); ctx.set_line_width(14); ctx.stroke(); ctx.restore()
            paint_text(ctx,"NO",W/2+60,410,140,scale=kz,fill=(255,255,255),stroke=(10,80,30),font="LuckiestGuy.ttf",glow=(46,196,90),rot=-0.08)
            paint_text(ctx,"MINIMUM PURCHASE",W/2+60,540,64,scale=kz,fill=(255,255,255),stroke=(10,80,30),font="LuckiestGuy.ttf",rot=-0.08)
    elif t<S_E2: # JALDI KARO
        burst_bg(ctx,t,c1="#FF4D6D",c2="#C9184A",cy=700,speed=0.4)
        for i in range(14):
            y=200+i*110; x=(t*1800+i*237)%(W+600)-300
            ctx.move_to(x,y); ctx.line_to(x+220,y); ctx.set_source_rgba(1,1,1,0.35); ctx.set_line_width(6); ctx.stroke()
        draw_character(ctx,"golu",W/2,900+math.sin(t*26)*8,1.45,mouth=m("golu"),expr="excited",t=t,arm=("cheer","point"))
        paint_text(ctx,"JALDI KARO!",W/2,330,140,scale=k_in(t,S_E,0.25,0.6),fill=(255,255,255),stroke=(100,0,30),font="LuckiestGuy.ttf",glow=(255,60,100),rot=-0.04)
    elif t<S_G: # ENDS 12 NOV
        diwali_bg(ctx,t,fw=False)
        flip_calendar(ctx,W/2+190,560,t,S_E2+0.1,day_to=12,s=1.0)
        paint_text(ctx,"OFFER ENDS",W/2+190,300,70,scale=k_in(t,S_E2+0.1,0.3),fill=(255,255,255),stroke=(120,0,40),font="LuckiestGuy.ttf",glow=(255,60,120))
        if t>=DATE_T+0.3: paint_text(ctx,"12 NOVEMBER",W/2+190,820,80,scale=k_in(t,DATE_T+0.3,0.3,0.6),fill=(30,25,28),stroke=(255,210,63),sw=0,font="Baloo2.ttf",box=(255,210,63),pad=16)
        draw_character(ctx,"raju",220,1000+bob(t,1.3),1.05,mouth=m("raju"),expr="smirk",t=t,look=(1,-0.4),arm=("down","point"),blink=False)
    elif t<END_CARD: # ABHI SHOP KARO
        diwali_bg(ctx,t,fw=True)
        for k in range(3): firework(ctx,(250,540,830)[k],420+60*k,t,S_G+0.1*k,col=[(1,0.8,0.2),(1,0.35,0.6),(0.4,0.9,1)][k],R=240,dur=1.6)
        paint_text(ctx,"ABHI SHOP KARO!",W/2,360,118,scale=k_in(t,S_G,0.3,0.6),fill=(255,255,255),stroke=(80,20,0),font="LuckiestGuy.ttf",grad=((255,245,150),(255,140,0)),glow=(255,170,40),rot=-0.04)
        draw_character(ctx,"golu",200,1080+bob(t,2.4),0.95,mouth=m("golu"),expr="excited",t=t,arm=("cheer","cheer"))
        draw_character(ctx,"nikki",540,1030+bob(t,2.2,1),1.0,mouth=m("nikki"),expr="laugh",t=t,arm=("cheer","thumbs"))
        draw_character(ctx,"raju",880,1090+bob(t,2.0,2),0.95,mouth=m("raju"),expr="smirk",t=t,arm=("down","up"))
        confetti(ctx,t,S_G,seed=4,n=110,dur=3)
    else:       # END CARD
        diwali_bg(ctx,t,c_top="#1B0B3A",c_bot="#3A0F5E",fw=True,lanterns=False,diyas=True)
        ctx.set_source_rgba(0.04,0.0,0.1,0.55); rrect(ctx,60,250,W-120,1300,40); ctx.fill()
        e=END_CARD
        w_,_=paint_text(ctx,"DIWALI OFFER",W/2,340,86,scale=k_in(t,e,0.3),fill=(255,255,255),stroke=(80,20,0),font="LuckiestGuy.ttf",grad=((255,245,150),(255,140,0)),glow=(255,170,40))
        diya(ctx,W/2-w_/2-70,365,0.55,t,1); diya(ctx,W/2+w_/2+70,365,0.55,t,2)
        paint_text(ctx,"GAMES FROM ₹99",W/2,500,100,scale=k_in(t,e+0.12,0.3,0.3),fill=(255,255,255),stroke=(60,20,0),font="Baloo2.ttf",grad=((255,245,150),(255,150,0)),glow=(255,190,40))
        paint_text(ctx,"EXTRA 10% OFF",W/2,640,100,scale=k_in(t,e+0.25,0.3,0.3),fill=(255,255,255),stroke=(120,0,40),font="Baloo2.ttf",glow=(255,60,120))
        kc=k_in(t,e+0.4,0.3); coupon_ticket(ctx,W/2,800,860,150,kc,0)
        paint_text(ctx,"CODE: DIWALI10",W/2-110,800,66,scale=kc,fill=(30,25,28),stroke=(255,210,63),sw=0,font="Baloo2.ttf",pad=6,rot=-0.05)
        paint_text(ctx,"NO MINIMUM PURCHASE",W/2,960,58,scale=k_in(t,e+0.55,0.3),fill=(255,255,255),stroke=(10,80,30),font="LuckiestGuy.ttf",glow=(46,196,90))
        paint_text(ctx,"ENDS 12 NOVEMBER",W/2,1065,62,scale=k_in(t,e+0.65,0.3),fill=(255,255,255),stroke=(40,20,70),font="LuckiestGuy.ttf")
        paint_text(ctx,"cheappcgames.in.net",W/2,1220,76,scale=k_in(t,e+0.8,0.3)*(1+0.03*math.sin(t*7)),fill=(20,15,30),stroke=(255,255,255),sw=0,font="Baloo2.ttf",box=(255,255,255),pad=24)
    ctx.identity_matrix(); vignette(ctx)
    if t<END_CARD:
        flash(ctx,t,STARTS,dur=0.1)
        paint_text(ctx,"CHEAP PC GAMES STORE",W/2-40,165,42,fill=(255,255,255),stroke=(40,25,70),font="LuckiestGuy.ttf",alpha=0.95)
        caption_draw(ctx,t)
    logo_badge(ctx,t)
    return surf


def ease_in_out(x): x=min(max(x,0),1); return 3*x*x-2*x*x*x

def srt(path):
    def ts(x):
        ms=int(round(x*1000)); h=ms//3600000; ms%=3600000; m_=ms//60000; ms%=60000; s_=ms//1000; ms%=1000
        return f"{h:02d}:{m_:02d}:{s_:02d},{ms:03d}"
    names={"golu":"Golu","raju":"Raju","nikki":"Nikki","all":"ALL 3"}
    with open(path,"w",encoding="utf-8") as f:
        for i,c in enumerate(caps,1): f.write(f"{i}\n{ts(c['start'])} --> {ts(c['end'])}\n{names[c['spk']]}: {c['text']}\n\n")
        f.write(f"{len(caps)+1}\n{ts(END_CARD)} --> {ts(END)}\nDIWALI OFFER | GAMES FROM ₹99 | EXTRA 10% OFF | CODE: DIWALI10 | NO MINIMUM PURCHASE | ENDS 12 NOVEMBER | cheappcgames.in.net\n\n")

def thumbnail(path):
    surf=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); ctx=cairo.Context(surf); t=0.9
    room(ctx,t)
    for i in range(26):
        x=i*43+10; y=95+18*math.sin(i*0.9); c=[(1,0.75,0.2),(1,0.35,0.45),(0.5,0.85,1),(0.7,1,0.5)][i%4]
        ellipse(ctx,x,y,9,12); ctx.set_source_rgba(*c,0.95); ctx.fill(); ellipse(ctx,x,y,24,24); ctx.set_source_rgba(*c,0.15); ctx.fill()
    draw_monitor(ctx,W/2,860,520,380,t,lambda c,x,y,w,h: checkout_screen(c,x,y,w,h,t))
    rrect(ctx,830,1060,150,280,14); fill_stroke(ctx,hexc("#1B1B22"),7)
    for fy in (1130,1250):
        ellipse(ctx,905,fy,44,44); ctx.set_source_rgb(*hexc("#F72585") if fy<1200 else hexc("#4CC9F0")); ctx.set_line_width(8); ctx.stroke()
    draw_character(ctx,"nikki",180,1150,0.85,expr="laugh",t=t,arm=("hip","down"))
    draw_character(ctx,"raju",905,1170,0.82,expr="smirk",t=t,look=(-0.6,-0.6),arm=("point","down"))
    draw_character(ctx,"golu",W/2,1290,1.15,expr="shock",t=t,look=(0,-0.8),arm=("head","head"))
    ctx.set_source_rgba(0.05,0.02,0.1,0.5); rrect(ctx,40,240,W-80,420,36); ctx.fill()
    paint_text(ctx,"COUPON LAGANA",W/2,330,104,fill=(255,255,255),stroke=(30,10,50),font="LuckiestGuy.ttf")
    w_,_=paint_text(ctx,"BHOOL GAYA?!",W/2-55,490,128,fill=(255,255,255),stroke=(120,0,20),font="LuckiestGuy.ttf",glow=(255,40,60),rot=-0.03)
    skull(ctx,W/2-55+w_/2+60,490,44)
    coupon_ticket(ctx,W/2,720,880,150,1,0.0)
    paint_text(ctx,"CODE: DIWALI10",W/2-150,720,58,fill=(30,25,28),stroke=(255,210,63),sw=0,font="Baloo2.ttf",pad=6,rot=-0.05)
    paint_text(ctx,"10% OFF",W/2+300,705,58,fill=(30,25,28),stroke=(255,210,63),sw=0,font="LuckiestGuy.ttf",pad=6,rot=-0.05)
    paint_text(ctx,"NO MINIMUM PURCHASE",W/2,1560,54,fill=(255,255,255),stroke=(10,80,30),font="LuckiestGuy.ttf",glow=(46,196,90))
    paint_text(ctx,"ENDS 12 NOVEMBER",W/2,1640,48,fill=(30,25,28),stroke=(255,210,63),sw=0,font="Baloo2.ttf",box=(255,210,63),pad=12)
    for i,x in enumerate([80,1000]): diya(ctx,x,1460,0.75,t,seed=i)
    vignette(ctx); logo_badge(ctx)
    surf.write_to_png(path); Image.open(path).convert("RGB").save(path.replace(".png",".jpg"),quality=93)

if __name__=="__main__":
    srt("out/reel007.srt")
    meta={"cover_ms":int((PCT_T+0.6)*1000),"duration":END,"end_card":[END_CARD,END],"lines":[(c["id"],c["spk"],round(c["start"],2),round(c["end"],2)) for c in caps]}
    if "--thumb" in sys.argv: thumbnail("out/reel007_thumbnail.png"); sys.exit()
    if PREVIEW:
        pts=[("a",BHOOL+0.5),("b",S_B+1.0),("c",S_B2+0.4),("d",LIVE_T+0.5),("e",S_C2+0.3),("f",P99+0.4),("g",PCT_T+0.5),("h",S_D2+0.5),("i",ZERO_T+0.5),("j",S_E+0.5),("k",DATE_T+0.8),("l",S_G+0.5),("m",END-0.5)]
        for n_,tt in pts: frame(tt).write_to_png(f"out/r10_{n_}.png")
        json.dump(meta,open("out/reel007_meta.json","w"),indent=1); print(json.dumps(meta)[:200]); sys.exit()
    encode(frame,NF,"out/reel007_mix.wav",OUT); json.dump(meta,open("out/reel007_meta.json","w"),indent=1); print("done",OUT)
