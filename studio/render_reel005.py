"""Reel 005 - 'MUMMY NE GAME DELETE KAR DIYA' (approved script, verbatim subtitles)."""
import math, sys, os, json, re
import numpy as np, cairo, soundfile as sf, colorsys
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from draw import *
from reelkit import *
import sfx

AUD="audio/reel005"; OUT=sys.argv[1] if len(sys.argv)>1 and not sys.argv[1].startswith("--") else "out/reel005.mp4"
PREVIEW="--preview" in sys.argv; BPM=128; HB=60/BPM/4
DIALOGUE=[
 ("01","golu","BHAI! MERI GAME LIBRARY MEIN 50 GAMES HAIN… PHIR BHI KUCH KHELNE KA MANN NAHI KAR RAHA!"),
 ("02","nikki","Toh koi ek game khel le!"),
 ("03","golu","WOHI TOH PROBLEM HAI! KYA KHELU?!"),
 ("04","raju","Bhai tu gamer hai ya Netflix ka customer? Game choose karne mein hi poori raat nikaal deta hai!"),
 ("05","golu","ABE GAME SELECT KARNA BHI EK ART HAI!"),
 ("06","raju","Drama band kar! Cheap PC Games Store check kar. Apni favourite games explore kar, aur games ₹99 se start hote hain!"),
 ("07","golu","BHAI ITNE OPTIONS?!"),
 ("08","nikki","Ab toh decide kar le!"),
 ("09","golu","EK MINUTE… PEHLE YE SAB WISHLIST MEIN DAALTA HOON!"),
 ("10","raju","Apni next game discover karo — cheappcgames.in.net!"),
 ("11","all","HAPPY GAMING!"),
]
HL=re.compile(r"^(BHAI|LIBRARY|50|GAMES|MANN|NAHI|PROBLEM|KYA|KHELU|GAMER|NETFLIX|CUSTOMER|POORI|RAAT|ART|DRAMA|CHEAP|PC|STORE|FAVOURITE|₹99|ITNE|OPTIONS|DECIDE|WISHLIST|NEXT|GAME|DISCOVER|CHEAPPCGAMES\.IN\.NET|HAPPY|GAMING)$")
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
GAP={"01":0.12,"02":0.08,"03":0.18,"04":0.1,"05":0.2,"06":0.1,"07":0.15,"08":0.08,"09":0.12,"10":0.15}
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
END_CARD=C["11"]["end"]+1.0; END=END_CARD+4.2
mx=Mixer(tl,END,["golu","raju","nikki"]); NF=mx.NF
print("duration",round(END,2))
def frac(lid,f): c=C[lid]; return c["start"]+f*(c["end"]-c["start"])
S_B=C["02"]["start"]; S_B2=C["03"]["start"]; S_C=C["04"]["start"]; S_C2=C["05"]["start"]; S_D=C["06"]["start"]; S_D2=C["07"]["start"]; S_E=C["08"]["start"]; S_E2=C["09"]["start"]; S_F=C["10"]["start"]; S_G=C["11"]["start"]
STARTS=[S_B,S_B2,S_C,S_C2,S_D,S_D2,S_E,S_E2,S_F,S_G,END_CARD]
N50=frac("01",0.18); MANN=frac("01",0.7); KYA=frac("03",0.55); RAAT=frac("04",0.62); ART=frac("05",0.6); P99=frac("06",0.74); WISH=frac("09",0.45)
mx.add(sfx.boom(),N50,0.8); mx.add(sfx.boing(),MANN,0.6)
for s in STARTS: mx.add(sfx.whoosh(),s-0.1,0.7)
mx.add(sfx.boom(),KYA,0.9); mx.add(sfx.ticks(1.0),RAAT-0.3,0.7); mx.add(sfx.sparkle(),ART,0.8)
mx.add(sfx.chaching(),P99,0.9); mx.add(sfx.sparkle(),P99+0.1,0.6); mx.add(sfx.pop(),S_D2,0.8)
for i in range(6): mx.add(sfx.heart_pop(),WISH+i*0.18,0.6)
mx.add(sfx.ding(),frac("10",0.6),0.7); mx.add(sfx.sparkle(),S_G,0.9); mx.add(sfx.chaching(),END_CARD+0.2,0.7)
os.makedirs("out",exist_ok=True); mx.render("out/reel005_mix.wav",bpm=BPM,music_gain=0.36)
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
SITE_NEW_Y=int(5725*1032/1290)   # 'NEW ARRIVALS' section on the live homepage
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

def frame(t):
    surf=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); ctx=cairo.Context(surf)
    last=max([0]+[s for s in STARTS if s<=t]); z=1+0.07*(1-ease_out((t-last)/0.28)); shake=(0,0)
    for st_,dur,amp in [(N50,0.25,14),(KYA,0.35,24),(P99,0.2,8)]:
        if st_<=t<st_+dur: f_=1-(t-st_)/dur; shake=(amp*f_*math.sin(t*97),amp*0.7*f_*math.cos(t*83))
    if t<END_CARD: ctx.translate(W/2+shake[0],H/2+shake[1]); ctx.scale(z,z); ctx.translate(-W/2,-H/2)
    m=lambda k_: mx.mouth(k_,t)
    if t<S_B:   # HOOK: 50 games, confused & bored
        room(ctx,t)
        def lib(c,x,y,w,h):
            c.set_source_rgb(*hexc("#0F1220")); c.rectangle(x,y,w,h); c.fill()
            paint_text(c,"LIBRARY • 50 GAMES",x+w/2,y+26,22,fill=(255,255,255),stroke=(15,18,32),sw=0,font="Baloo2.ttf",pad=4)
            tile_grid(c,x+12,y+52,5,10,(w-24-4*8)/5,(w-24-4*8)/5*1.3,8,t,scroll=(t*60)%260,clip=(x,y+46,w,h-46))
        draw_monitor(ctx,640,700,560,400,t,lib)
        draw_character(ctx,"golu",240,900+bob(t,0.8),1.05,mouth=m("golu"),expr="confused" if t<MANN else "sad",t=t,look=(1,-0.3),arm=("down","shrug") if t>=MANN else ("down","down"),blink=blink(t,0.3))
        desk(ctx,t)
        paint_text(ctx,"50 GAMES",W/2,300,150,scale=k_in(t,N50,0.3,0.6),fill=(255,255,255),stroke=(40,0,60),font="Baloo2.ttf",grad=((255,245,150),(255,150,0)),glow=(255,190,40),rot=-0.04)
        if t>=MANN: paint_text(ctx,"PHIR BHI BORE",W/2,450,72,scale=k_in(t,MANN,0.3,0.4),fill=(255,255,255),stroke=(0,40,70),font="LuckiestGuy.ttf",glow=(60,220,255))
    elif t<S_C: # Nikki (big, over-shoulder) + KYA KHELU wheel
        if t<S_B2:
            room(ctx,t)
            draw_character(ctx,"golu",230,1000+bob(t,0.9),0.85,mouth=m("golu"),expr="sad",t=t,look=(1,-0.2),blink=blink(t,0.8))
            draw_character(ctx,"nikki",760,860+bob(t,1.4,1),1.4,mouth=m("nikki"),expr="laugh" if m("nikki")<0.05 else "normal",t=t,look=(-1,0),arm=("down","shrug"),blink=blink(t,0.4))
        else:
            burst_bg(ctx,t,c1="#5E60CE",c2="#3A0CA3",cy=700,speed=0.15)
            ctx.save(); ctx.translate(W/2,560); ctx.rotate(t*2.5)
            for i in range(8):
                ctx.save(); ctx.rotate(i*math.pi/4); game_tile(ctx,-60,-330,120,150,i*5); ctx.restore()
            ctx.restore()
            draw_character(ctx,"golu",W/2,980+bob(t,3,0,8),1.3,mouth=m("golu"),expr="confused" if t<KYA else "shock",t=t,arm=("head","head"))
            paint_text(ctx,"KYA KHELU?!",W/2,330,150,scale=k_in(t,KYA,0.3,0.6),fill=(255,255,255),stroke=(120,0,40),font="LuckiestGuy.ttf",glow=(255,60,170),rot=0.04)
    elif t<S_C2: # Raju roast close-up (smirk), Golu reaction PIP
        bg=cairo.LinearGradient(0,0,0,H); bg.add_color_stop_rgb(0,*hexc("#0B1026")); bg.add_color_stop_rgb(1,*hexc("#1B1F3B")); ctx.set_source(bg); ctx.paint()
        rng=np.random.default_rng(2)
        for i in range(50):
            ellipse(ctx,rng.uniform(0,W),rng.uniform(0,900),2.5,2.5); ctx.set_source_rgba(1,1,1,0.4+0.4*math.sin(t*3+i)); ctx.fill()
        moon(ctx,860,330,80)
        draw_character(ctx,"raju",400,870+bob(t,1.1),1.45,mouth=m("raju"),expr="smirk",t=t,look=(1,0),arm=("hip","point"),blink=False)
        if t>=RAAT-0.4:
            kc=k_in(t,RAAT-0.4,0.3); clock(ctx,830,560,95*kc,t,speed=14)
            paint_text(ctx,"POORI RAAT",820,720,74,scale=k_in(t,RAAT,0.3,0.4),fill=(255,255,255),stroke=(0,20,60),font="LuckiestGuy.ttf",glow=(120,160,255))
        pip(ctx,"golu",840,1060,120,t,"sad",m("golu"),look=(-1,0.3),ring=(242/255,193/255,78/255))
    elif t<S_D: # ART
        burst_bg(ctx,t,c1="#FFB3C6",c2="#FF85A1",cy=700,speed=0.2)
        draw_character(ctx,"golu",W/2,900+bob(t,1.6),1.35,mouth=m("golu"),expr="smirk",t=t,look=(0,-0.3),arm=("down","cheer"),blink=False)
        beret(ctx,W/2-10,900-150*1.35,1.35*k_in(t,S_C2+0.1,0.3,0.4))
        palette(ctx,W/2-260,1130,1.3*k_in(t,S_C2+0.25,0.3,0.4),t)
        paint_text(ctx,"EK ART HAI!",W/2,330,130,scale=k_in(t,ART,0.3,0.5),fill=(255,255,255),stroke=(120,0,60),font="LuckiestGuy.ttf",glow=(255,120,180),rot=-0.04)
    elif t<S_E: # LIVE WEBSITE SHOWCASE (big, readable)
        bokeh_bg(ctx,t,"#3A2466","#140B2E",seed=5,tint=(1,0.9,0.6))
        PX,PY,PW,PH=W/2,822,1000,1064
        if t<S_D2:
            u=t-S_D-0.35; d=S_D2-S_D-0.35
            sc=(SITE_NEW_Y+150)*ease_in_out(min(max(u/(d*0.8),0),1)) if u>0 else 0
        else:
            sc=SITE_NEW_Y+150 + 40*(t-S_D2)
        phone_with(ctx,PX,PY,PW,PH,k_in(t,S_D,0.35),lambda c,x,y,w,h: site_screen(c,x,y,w,h,sc))
        if t<S_D2:
            pip(ctx,"raju",118,300,92,t,"smirk",m("raju"),look=(1,0.2),ring=(47/255,165/255,138/255))
            if t>=P99-0.05:
                kq=k_in(t,P99,0.3,0.6); ctx.set_source_rgba(0.05,0.02,0.1,0.75*min(1,kq)); rrect(ctx,90,1170,W-180,120,30); ctx.fill()
                paint_text(ctx,"GAMES ₹99 SE START",W/2,1230,72,scale=k_in(t,P99,0.3,0.6),fill=(255,255,255),stroke=(60,20,0),font="Baloo2.ttf",grad=((255,245,150),(255,150,0)),glow=(255,190,40))
        else:
            draw_character(ctx,"golu",150,1230+abs(math.sin(t*7))*-30,0.72,mouth=m("golu"),expr="excited",t=t,arm=("cheer","cheer"))
            paint_text(ctx,"ITNE OPTIONS?!",W/2,1215,96,scale=k_in(t,S_D2+0.05,0.3,0.5),fill=(255,255,255),stroke=(60,20,0),font="LuckiestGuy.ttf",grad=((255,245,150),(255,150,0)),glow=(255,190,40))
    elif t<S_F: # decide / wishlist
        room(ctx,t)
        if t<S_E2:
            draw_character(ctx,"golu",210,1060+bob(t,1.0),0.8,mouth=m("golu"),expr="confused",t=t,look=(1,-0.3),arm=("down","shrug"))
            draw_character(ctx,"nikki",700,860+bob(t,1.2),1.35,mouth=m("nikki"),expr="doubt",t=t,look=(-0.6,0),arm=("hip","hip"))
            paint_text(ctx,"DECIDE KAR!",W/2,330,120,scale=k_in(t,S_E+0.1,0.3,0.5),fill=(255,255,255),stroke=(120,0,60),font="LuckiestGuy.ttf",glow=(255,90,190))
        else:
            bx,by=W/2+190,560
            rrect(ctx,bx-210,by-170,420,340,30); fill_stroke(ctx,hexc("#FFFFFF"),8)
            paint_text(ctx,"WISHLIST",bx,by-110,64,fill=(230,57,70),stroke=(255,255,255),sw=0,font="LuckiestGuy.ttf",pad=6)
            n=int(min(12,max(0,(t-WISH)/0.12)))
            for i in range(n): game_tile(ctx,bx-185+(i%6)*62,by-55+(i//6)*95,54,80,i*5)
            draw_character(ctx,"nikki",820,1180+bob(t,1.8,1),0.8,mouth=m("nikki"),expr="laugh",t=t,arm=("down","down"))
            for i in range(6):
                u=((t-WISH)*0.9+i*0.17)%1
                if t>=WISH:
                    hx=260+u*(bx-260)+40*math.sin(i); hy=1000-u*(1000-by)
                    ctx.save(); ctx.translate(hx,hy); ctx.scale(1.2,1.2); ctx.move_to(0,22); ctx.curve_to(-46,-6,-24,-44,0,-18); ctx.curve_to(24,-44,46,-6,0,22); ctx.close_path(); ctx.set_source_rgba(1,0.25,0.42,0.9); ctx.fill(); ctx.restore()
            draw_character(ctx,"golu",260,960+bob(t,2.6,0,10),1.1,mouth=m("golu"),expr="love",t=t,look=(1,-0.5),arm=("phone","cheer"))
    elif t<S_G: # URL
        bokeh_bg(ctx,t,"#3A0CA3","#14053A",seed=9,tint=(0.8,0.7,1))
        draw_character(ctx,"raju",300,940+bob(t,1.3),1.2,mouth=m("raju"),expr="smirk",t=t,look=(1,-0.4),arm=("down","point"),blink=False)
        paint_text(ctx,"NEXT GAME",W/2+140,560,92,scale=k_in(t,S_F+0.1,0.3),fill=(255,255,255),stroke=(40,20,70),font="LuckiestGuy.ttf")
        paint_text(ctx,"DISCOVER KARO",W/2+140,670,78,scale=k_in(t,S_F+0.2,0.3),fill=(255,210,63),stroke=(40,20,70),font="LuckiestGuy.ttf")
        paint_text(ctx,"cheappcgames.in.net",W/2,340,84,scale=k_in(t,frac("10",0.4),0.35,0.4)*(1+0.03*math.sin(t*8)),fill=(30,25,28),stroke=(255,255,255),sw=0,font="Baloo2.ttf",box=(255,255,255),pad=22)
    elif t<END_CARD: # HAPPY GAMING
        burst_bg(ctx,t,c1="#FFD23F",c2="#FF9F1C",cy=600,speed=0.25)
        paint_text(ctx,"HAPPY GAMING!",W/2,380,130,scale=k_in(t,S_G,0.3,0.6),fill=(255,255,255),stroke=(120,40,0),font="LuckiestGuy.ttf",glow=(255,120,0),rot=-0.04)
        draw_character(ctx,"golu",200,1100+bob(t,2.4),0.95,mouth=m("golu"),expr="excited",t=t,arm=("cheer","cheer"))
        draw_character(ctx,"nikki",540,1050+bob(t,2.2,1),1.0,mouth=m("nikki"),expr="laugh",t=t,arm=("cheer","thumbs"))
        draw_character(ctx,"raju",880,1110+bob(t,2.0,2),0.95,mouth=m("raju"),expr="smirk",t=t,arm=("pad","pad")); gamepad(ctx,880,1110+470*0.95,0.75)
        confetti(ctx,t,S_G,seed=4,n=110,dur=3)
    else:       # END CARD (high contrast, mobile-first)
        bokeh_bg(ctx,t,"#2A1B54","#0E0A20",seed=3,tint=(1,0.8,1))
        backlight(ctx,W/2,760,560,(1,0.75,0.3),0.22)
        paint_text(ctx,"CHEAP PC GAMES STORE",W/2,420,82,scale=k_in(t,END_CARD,0.3),fill=(255,255,255),stroke=(40,20,70),font="LuckiestGuy.ttf",glow=(255,60,170))
        paint_text(ctx,"GAMES FROM",W/2,590,84,scale=k_in(t,END_CARD+0.15,0.3),fill=(255,255,255),stroke=(40,20,70),font="LuckiestGuy.ttf")
        paint_text(ctx,"₹99",W/2,790,260,scale=k_in(t,END_CARD+0.3,0.3,0.4)*(1+0.02*math.sin(t*6)),fill=(255,255,255),stroke=(60,20,0),font="Baloo2.ttf",grad=((255,245,150),(255,150,0)),glow=(255,190,40))
        paint_text(ctx,"cheappcgames.in.net",W/2,1030,80,scale=k_in(t,END_CARD+0.5,0.3),fill=(20,15,30),stroke=(255,255,255),sw=0,font="Baloo2.ttf",box=(255,255,255),pad=24)
        paint_text(ctx,"LINK IN BIO",W/2,1200,84,scale=k_in(t,END_CARD+0.7,0.3)*(1+0.04*math.sin(t*8)),fill=(20,15,30),stroke=(255,210,63),sw=0,font="LuckiestGuy.ttf",box=(255,210,63),pad=22)
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
    names={"golu":"Golu","raju":"Raju","nikki":"Nikki","all":"ALL THREE"}
    with open(path,"w",encoding="utf-8") as f:
        for i,c in enumerate(caps,1): f.write(f"{i}\n{ts(c['start'])} --> {ts(c['end'])}\n{names[c['spk']]}: {c['text']}\n\n")
        f.write(f"{len(caps)+1}\n{ts(END_CARD)} --> {ts(END)}\nCHEAP PC GAMES STORE | GAMES FROM ₹99 | cheappcgames.in.net | LINK IN BIO\n\n")

def thumbnail(path):
    surf=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); ctx=cairo.Context(surf); t=1.0
    burst_bg(ctx,t,c1="#5E60CE",c2="#3A0CA3",cy=900,speed=0)
    for i in range(18):
        a=i*2*math.pi/18+0.1; d=380+70*(i%3)
        ctx.save(); ctx.translate(W/2+d*math.cos(a),1000+d*0.85*math.sin(a)); ctx.rotate(0.25*math.sin(i*1.7)); game_tile(ctx,-60,-78,120,156,i*7); ctx.restore()
    qmarks(ctx,0.6,W/2,960,n=6,R=330)
    draw_character(ctx,"nikki",210,1150,0.85,expr="laugh",t=t,arm=("hip","down"))
    draw_character(ctx,"raju",880,1180,0.82,expr="normal",t=t,look=(-0.6,0),arm=("down","point"))
    draw_character(ctx,"golu",W/2,1230,1.25,expr="shock",t=t,look=(0,-0.5),arm=("head","head"))
    ctx.set_source_rgba(0.05,0.02,0.1,0.45); rrect(ctx,40,250,W-80,470,36); ctx.fill()
    paint_text(ctx,"BHAI,",W/2,330,100,fill=(255,255,255),stroke=(30,10,50),font="LuckiestGuy.ttf")
    paint_text(ctx,"AB KYA KHELU?!",W/2,490,140,fill=(255,255,255),stroke=(120,0,40),font="LuckiestGuy.ttf",glow=(255,60,170),rot=-0.03)
    paint_text(ctx,"50 GAMES… 0 DECISION",W/2,640,64,fill=(30,25,28),stroke=(255,210,63),sw=0,font="Baloo2.ttf",box=(255,210,63),pad=14)
    vignette(ctx); logo_badge(ctx)
    surf.write_to_png(path); Image.open(path).convert("RGB").save(path.replace(".png",".jpg"),quality=93)

if __name__=="__main__":
    srt("out/reel005.srt")
    meta={"cover_ms":int((KYA+0.6)*1000),"duration":END,"end_card":[END_CARD,END],"lines":[(c["id"],c["spk"],round(c["start"],2),round(c["end"],2)) for c in caps]}
    if "--thumb" in sys.argv: thumbnail("out/reel005_thumbnail.png"); sys.exit()
    if PREVIEW:
        pts=[("a",MANN+0.4),("b",S_B+0.6),("c",KYA+0.5),("d",RAAT+0.5),("e",ART+0.4),("f",S_D+1.2),("f2",P99+0.4),("g",S_D2+0.7),("h",S_E+0.6),("i",WISH+1.0),("j",frac("10",0.8)),("l",END-0.5)]
        for n_,tt in pts: frame(tt).write_to_png(f"out/r7_{n_}.png")
        json.dump(meta,open("out/reel005_meta.json","w"),indent=1); print(json.dumps(meta)[:200]); sys.exit()
    encode(frame,NF,"out/reel005_mix.wav",OUT); json.dump(meta,open("out/reel005_meta.json","w"),indent=1); print("done",OUT)
