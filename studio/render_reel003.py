"""Reel 003 - GTA 6 on PS5: 3 plans (1 month ₹1300, Offline lifetime ₹2000, Online lifetime ₹3000). Generic synthwave look, no game artwork/logos."""
import math, sys, os, json
import numpy as np, cairo
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from draw import *
from reelkit import *
import sfx

AUD="audio/reel003"; OUT=sys.argv[1] if len(sys.argv)>1 and not sys.argv[1].startswith("--") else "out/reel003.mp4"
PREVIEW="--preview" in sys.argv
LINES=[
 ("01","golu",["RUKO RUKO RUKO!","*GTA 6*...","SIRF *₹1300* MEIN?!"]),
 ("02","raju",["HAAN BHAI!","*PS5* PE *GTA 6*,","*19 NOVEMBER* KO LAUNCH...","AUR HAMARE *3 PLANS*","READY HAIN!"]),
 ("03","raju",["PEHLA PLAN...","*1 MAHINA*,","SIRF *₹1300!*"]),
 ("04","golu",["DOOSRA...","*OFFLINE LIFETIME*,","SIRF *₹2000!*"]),
 ("05","nikki",["AUR MUJHE DOSTON KE SAATH","*ONLINE* KHELNA HAI TOH?"]),
 ("06","raju",["TOH *ONLINE LIFETIME*...","SIRF *₹3000!*","*BEST DEAL!*"]),
 ("07","nikki",["WOW! PAR ITNE","SASTE MEIN...","*TRUST* KAISE KAREIN?"]),
 ("08","golu",["*TRUST ISSUES?*","HAMARA *PICHHLA REEL*","DEKHO!","*GST* REGISTERED,","*UDYAM* REGISTERED,","AUR *2000+* HAPPY CUSTOMERS!"]),
 ("09","raju",["TOH DER MAT KARO!","*ABHI BOOK KARO*...","*LINK BIO MEIN!*"]),
]
GAPS={"01":0.3,"02":0.3,"03":0.3,"04":0.3,"05":0.25,"06":0.35,"07":0.25,"08":0.3}
tl=build_timeline(AUD,LINES,GAPS,lead=0.55)
L={x["id"]:x for x in tl}
END=tl[-1]["end"]+2.2
mx=Mixer(tl,END,["golu","raju","nikki"]); NF=mx.NF
print("duration",round(END,2))

S2=L["02"]["start"]-0.12; S3=L["03"]["start"]-0.12; S4=L["07"]["start"]-0.12; S5=L["09"]["start"]-0.12
STARTS=[S2,S3,S4,S5]
GTA_T=0.05; P1300_T=L["01"]["start"]+1.75
C1=L["03"]["start"]+1.2; C2=L["04"]["start"]+0.9; C3Q=L["05"]["start"]+0.2; C3=L["06"]["start"]+1.0
PLANS3_T=L["02"]["end"]-1.6
GST_T=L["08"]["start"]+2.4; UDY_T=L["08"]["start"]+3.5; CUS_T=L["08"]["start"]+4.6; REEL_T=L["08"]["start"]+1.0

mx.add(sfx.siren(1.0),0.0,0.9); mx.add(sfx.boom(),GTA_T,1.0); mx.add(sfx.boom(),P1300_T,1.0); mx.add(sfx.chaching(),P1300_T+0.1,0.7)
for s in STARTS: mx.add(sfx.whoosh(),s-0.05,0.9)
mx.add(sfx.riser(0.6),PLANS3_T-0.6,0.9); mx.add(sfx.pop(),PLANS3_T,0.9)
for c in (C1,C2,C3): mx.add(sfx.stamp(),c,0.9); mx.add(sfx.chaching(),c+0.05,0.6)
mx.add(sfx.boing(),C3Q,0.5); mx.add(sfx.sparkle(),C3+0.2,0.9)
mx.add(sfx.pop(),REEL_T,0.8)
for c in (GST_T,UDY_T,CUS_T): mx.add(sfx.pop(),c,0.7)
mx.add(sfx.heart_pop(),CUS_T+0.5,0.7); mx.add(sfx.boom(),S5+0.1,0.6); mx.add(sfx.chaching(),S5+0.6,0.8)
os.makedirs("out",exist_ok=True); mx.render("out/reel003_mix.wav",bpm=138,music_gain=0.55)

def blink(t,seed): return ((t+seed)%3.2)<0.12
bob=lambda t,f,ph=0,a=6: a*math.sin(t*2*math.pi*f+ph)

# ---------- synthwave scenery (generic, original) ----------
def synthwave(ctx,t,horizon=1020,sun=True):
    g=cairo.LinearGradient(0,0,0,horizon)
    g.add_color_stop_rgb(0,*hexc("#12002B")); g.add_color_stop_rgb(0.55,*hexc("#5B0E7A")); g.add_color_stop_rgb(1,*hexc("#FF4F8B"))
    ctx.set_source(g); ctx.rectangle(0,0,W,horizon); ctx.fill()
    rng=np.random.default_rng(3)
    for i in range(60):
        x=rng.uniform(0,W); y=rng.uniform(0,horizon*0.6); tw=0.5+0.5*math.sin(t*3+i)
        ellipse(ctx,x,y,2.5,2.5); ctx.set_source_rgba(1,1,1,0.3+0.5*tw); ctx.fill()
    if sun:
        cx,cy,r=W/2,horizon-120,300
        sg=cairo.LinearGradient(0,cy-r,0,cy+r); sg.add_color_stop_rgb(0,*hexc("#FFE45E")); sg.add_color_stop_rgb(1,*hexc("#FF3D7F"))
        ctx.save(); ctx.arc(cx,cy,r,0,2*math.pi); ctx.clip()
        ctx.set_source(sg); ctx.paint()
        for k in range(7):
            yy=cy+20+k*38+((t*30)%38); hh=6+k*3
            ctx.rectangle(cx-r,yy,2*r,hh); ctx.set_source_rgb(*hexc("#B0247A")); ctx.fill()
        ctx.restore()
        backlight(ctx,cx,cy,520,(1,0.4,0.6),0.25)
    # city skyline silhouette
    rng=np.random.default_rng(8); x=0
    while x<W:
        bw=rng.uniform(50,120); bh=rng.uniform(80,300)
        ctx.rectangle(x,horizon-bh,bw,bh); ctx.set_source_rgb(*hexc("#1A0633")); ctx.fill()
        for wy in range(int(horizon-bh+15),int(horizon-10),28):
            for wx in range(int(x+10),int(x+bw-10),22):
                if rng.random()<0.35: ctx.rectangle(wx,wy,8,12); ctx.set_source_rgba(1,0.85,0.4,0.8); ctx.fill()
        x+=bw+4
    # palms
    for px,ph,flip in [(90,520,1),(990,600,-1),(200,380,1)]:
        palm(ctx,px,horizon,ph,flip,t)
    # neon grid floor
    fg=cairo.LinearGradient(0,horizon,0,H); fg.add_color_stop_rgb(0,*hexc("#2A0845")); fg.add_color_stop_rgb(1,*hexc("#0B0018"))
    ctx.set_source(fg); ctx.rectangle(0,horizon,W,H-horizon); ctx.fill()
    ctx.set_line_width(3)
    for i in range(-12,13):
        ctx.move_to(W/2+i*40,horizon); ctx.line_to(W/2+i*260,H)
        ctx.set_source_rgba(1,0.3,0.8,0.55); ctx.stroke()
    off=(t*0.8)%1
    for k in range(14):
        u=((k+off)/14)**2.2; yy=horizon+u*(H-horizon)
        ctx.move_to(0,yy); ctx.line_to(W,yy); ctx.set_source_rgba(0.3,0.9,1,0.25+0.5*u); ctx.stroke()

def palm(ctx,x,base,h,flip,t):
    ctx.save(); ctx.translate(x,base)
    ctx.move_to(-10,0); ctx.curve_to(-6*flip-10,-h*0.4,14*flip,-h*0.8,22*flip,-h); ctx.line_to(36*flip,-h); ctx.curve_to(28*flip,-h*0.8,8*flip+10,-h*0.4,12,0); ctx.close_path()
    ctx.set_source_rgb(*hexc("#0E0220")); ctx.fill()
    ctx.translate(29*flip,-h)
    sw=0.06*math.sin(t*1.5+x)
    for a in [-2.9,-2.3,-1.7,-1.2,-0.6,-0.1]:
        ctx.save(); ctx.rotate(a+sw); ctx.move_to(0,0); ctx.curve_to(60,-30,130,-10,170,40); ctx.curve_to(120,10,60,0,0,12); ctx.close_path()
        ctx.set_source_rgb(*hexc("#0E0220")); ctx.fill(); ctx.restore()
    ctx.restore()

def neon_card(ctx,cx,cy,w,h,t,t0,label,price,col,best=False):
    u=t-t0
    if u<0: return
    k=ease_out_back(u/0.35)
    ctx.save(); ctx.translate(cx,cy); ctx.scale(k,k); ctx.rotate(-0.02 if not best else 0.0)
    if best: s_=1+0.03*math.sin(t*7); ctx.scale(s_,s_)
    for gw,ga in [(30,0.12),(18,0.22),(8,0.5)]:
        rrect(ctx,-w/2,-h/2,w,h,36); ctx.set_source_rgba(*col,ga); ctx.set_line_width(gw); ctx.stroke()
    rrect(ctx,-w/2,-h/2,w,h,36); ctx.set_source_rgba(0.06,0.01,0.14,0.88); ctx.fill_preserve(); ctx.set_source_rgb(*col); ctx.set_line_width(6); ctx.stroke()
    if best:
        rrect(ctx,w/2-260,-h/2-34,240,62,20); ctx.set_source_rgb(*hexc("#FFD23F")); ctx.fill_preserve(); ctx.set_source_rgb(*INK); ctx.set_line_width(5); ctx.stroke()
    ctx.restore()
    c255=tuple(int(c*255) for c in col)
    paint_text(ctx,label,cx-w*0.2*k,cy,56 if len(label)<12 else 48,scale=max(k,0.01),fill=(255,255,255),stroke=(20,5,40),font="LuckiestGuy.ttf")
    paint_text(ctx,price,cx+w*0.3*k,cy,104,scale=max(k,0.01),fill=(255,255,255),stroke=(20,5,40),font="Baloo2.ttf",glow=c255,sw=6)
    if best: paint_text(ctx,"BEST DEAL",cx+w/2-140,cy-h/2-3,38,scale=max(k,0.01),fill=(30,25,28),stroke=(255,210,63),sw=0,font="LuckiestGuy.ttf",pad=6)

def img_surface(path,wmax):
    im=Image.open(path).convert("RGBA"); r=wmax/im.width; im=im.resize((int(im.width*r),int(im.height*r)))
    a=np.array(im).astype(np.float32); al=a[...,3:4]/255
    bgra=np.ascontiguousarray(np.dstack([a[...,2:3]*al,a[...,1:2]*al,a[...,0:1]*al,a[...,3:4]]).astype(np.uint8))
    return cairo.ImageSurface.create_for_data(memoryview(bgra),cairo.FORMAT_ARGB32,im.width,im.height,im.width*4),bgra
REEL2,_keep=img_surface("reel002_trust_cover.jpg",400)

def frame(t):
    surf=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); ctx=cairo.Context(surf)
    last=max([0]+[s for s in STARTS if s<=t]); z=1+0.06*(1-ease_out((t-last)/0.3))
    shake=(0,0)
    for st,dur,amp in [(GTA_T,0.35,22),(P1300_T,0.35,22),(C1,0.2,10),(C2,0.2,10),(C3,0.25,14)]:
        if st<=t<st+dur: f_=1-(t-st)/dur; shake=(amp*f_*math.sin(t*97),amp*0.7*f_*math.cos(t*83))
    ctx.translate(W/2+shake[0],H/2+shake[1]); ctx.scale(z,z); ctx.translate(-W/2,-H/2)
    m=lambda k: mx.mouth(k,t)
    if t<S2:   # HOOK
        synthwave(ctx,t)
        k=ease_out_back((t-GTA_T)/0.3)*(1.8-0.8*ease_out((t-GTA_T)/0.25))
        paint_text(ctx,"GTA 6",W/2,430,230,scale=max(k,0.01),fill=(255,255,255),stroke=(40,0,60),font="LuckiestGuy.ttf",glow=(255,60,170),rot=-0.05)
        paint_text(ctx,"PS5",W/2+280,560,70,scale=max(ease_out_back((t-0.35)/0.3),0.01),fill=(30,25,28),stroke=(255,255,255),sw=0,font="LuckiestGuy.ttf",box=(80,220,255),pad=14,rot=0.08)
        kp=ease_out_back((t-P1300_T)/0.3)*(1.8-0.8*ease_out((t-P1300_T)/0.25))
        paint_text(ctx,"₹1300?!",W/2,700,190,scale=max(kp,0.01),fill=(255,255,255),stroke=(60,20,0),font="Baloo2.ttf",grad=((255,245,150),(255,150,0)),glow=(255,190,40),rot=0.04)
        ki=ease_out_back((t-0.2)/0.4)
        draw_character(ctx,"golu",W/2,1080+(1-ki)*500+bob(t,3,0,8),1.25,mouth=m("golu"),expr="shock",t=t,look=(0,-0.6),arm=("cheer","cheer"))
    elif t<S3: # Raju: launch + 3 plans
        synthwave(ctx,t)
        k=ease_out_back((t-S2-0.1)/0.35)
        paint_text(ctx,"GTA 6 • PS5",W/2,340,120,scale=max(k,0.01),fill=(255,255,255),stroke=(40,0,60),font="Baloo2.ttf",glow=(255,60,170))
        k2=ease_out_back((t-S2-0.9)/0.35); flick=1.0 if (t*13)%7>0.6 else 0.35
        paint_text(ctx,"19 NOV LAUNCH",W/2,500,86,scale=max(k2,0.01),alpha=flick,fill=(255,255,255),stroke=(0,60,90),font="LuckiestGuy.ttf",glow=(60,220,255))
        k3=ease_out_back((t-PLANS3_T)/0.35)*(1.5-0.5*ease_out((t-PLANS3_T)/0.25))
        paint_text(ctx,"3 PLANS!",W/2,680,150,scale=max(k3,0.01),fill=(255,255,255),stroke=(60,20,0),font="LuckiestGuy.ttf",grad=((255,245,150),(255,150,0)),glow=(255,190,40),rot=-0.04)
        backlight(ctx,W/2,1100,450,(0.3,1,0.8),0.25)
        ki=ease_out((t-S2)/0.35)
        draw_character(ctx,"raju",W/2+(1-ki)*700,1080+bob(t,1.4),1.2,mouth=m("raju"),expr="normal",t=t,look=(0,-0.5),arm=("point","up"),blink=blink(t,0.3))
    elif t<S4: # PRICE CARDS
        synthwave(ctx,t,horizon=1150,sun=False)
        ctx.set_source_rgba(0,0,0,0.25); ctx.paint()
        paint_text(ctx,"GTA 6 • PS5 PLANS",W/2,300,74,fill=(255,255,255),stroke=(40,0,60),font="Baloo2.ttf",glow=(255,60,170),scale=max(ease_out_back((t-S3)/0.3),0.01))
        neon_card(ctx,W/2,480,920,200,t,C1,"1 MONTH","₹1300",(0.3,0.9,1.0))
        neon_card(ctx,W/2,730,920,200,t,C2,"OFFLINE LIFETIME","₹2000",(1.0,0.35,0.75))
        if C3Q<=t<C3:
            kq=ease_out_back((t-C3Q)/0.3)
            paint_text(ctx,"???",W/2,985,130,scale=max(kq,0.01)*(1+0.06*math.sin(t*12)),fill=(255,210,63),stroke=(40,0,60),font="LuckiestGuy.ttf")
        neon_card(ctx,W/2,990,920,210,t,C3,"ONLINE LIFETIME","₹3000",(1.0,0.82,0.25),best=True)
        if t>=C3: confetti(ctx,t,C3+0.1,seed=21,n=70,dur=2.5)
        y0=1300
        draw_character(ctx,"golu",190,y0+bob(t,1.5),0.8,mouth=m("golu"),expr="star" if t>C3 else "happy" if m("golu")<0.1 else "normal",t=t,look=(0.5,-1),arm=("cheer","down"))
        if t>L["05"]["start"]-0.4:
            kn=ease_out_back((t-L["05"]["start"]+0.4)/0.4)
            draw_character(ctx,"nikki",540,y0+30+(1-kn)*500+bob(t,1.2,1),0.82,mouth=m("nikki"),expr="love" if t>C3+0.3 else "normal",t=t,look=(0,-1),arm=("down","phone"))
        draw_character(ctx,"raju",890,y0+bob(t,1.3,2),0.8,mouth=m("raju"),expr="normal",t=t,look=(-0.5,-1),arm=("point","down"),blink=blink(t,0.7))
    elif t<S5: # TRUST: previous reel
        bokeh_bg(ctx,t,"#5B2A86","#1E1240",seed=4,tint=(1,0.7,0.9))
        u=t-S4
        draw_character(ctx,"nikki",250,1000+bob(t,1.1),1.0,mouth=m("nikki"),expr="doubt" if t<CUS_T+0.4 else "love",t=t,look=(1,-0.2),arm=("hip","down"),blink=blink(t,1.2))
        # big phone with previous reel
        kp=ease_out_back((t-REEL_T)/0.4)
        if kp>0:
            ctx.save(); ctx.translate(745,745); ctx.scale(kp,kp); ctx.rotate(0.05)
            draw_phone(ctx,0,0,470,820)
            ctx.save(); rrect(ctx,-213,-388,426,776,30); ctx.clip()
            ctx.set_source_surface(REEL2,-200,-355); ctx.paint(); ctx.restore()
            ellipse(ctx,0,0,58,58); ctx.set_source_rgba(0,0,0,0.5); ctx.fill()
            ctx.move_to(-18,-30); ctx.line_to(30,0); ctx.line_to(-18,30); ctx.close_path(); ctx.set_source_rgb(1,1,1); ctx.fill()
            ctx.restore()
            paint_text(ctx,"PICHHLA REEL DEKHO",700,262,58,scale=max(kp,0.01)*(1+0.04*math.sin(t*8)),fill=(30,25,28),stroke=(255,210,63),sw=0,font="LuckiestGuy.ttf",box=(255,210,63),pad=14)
        for i,(txt,col,tt) in enumerate([("GST",(255,210,63),GST_T),("UDYAM",(59,206,172),UDY_T),("2000+",(255,133,161),CUS_T)]):
            kk=ease_out_back((t-tt)/0.3)
            if kk<=0: continue
            cx_=500+i*215; cy_=1225
            w_,_=paint_text(ctx,txt,cx_-18,cy_,50,scale=max(kk,0.01),fill=(30,25,28),stroke=col,sw=0,font="Baloo2.ttf",box=col,pad=14)
            ellipse(ctx,cx_-18+w_/2+6,cy_,22*kk,22*kk); fill_stroke(ctx,hexc("#2EC45A"),4)
        ki=ease_out((t-L["08"]["start"]+0.3)/0.4)
        if t>L["08"]["start"]-0.3:
            draw_character(ctx,"golu",900+(1-ki)*400,1450+bob(t,1.6),0.85,mouth=m("golu"),expr="normal",t=t,look=(-1,-0.6),arm=("point","down"),blink=blink(t,0.4))
    else:      # END CARD
        synthwave(ctx,t)
        u=t-S5
        paint_text(ctx,"GTA 6 • PS5",W/2,300,110,scale=max(ease_out_back(u/0.35),0.01),fill=(255,255,255),stroke=(40,0,60),font="Baloo2.ttf",glow=(255,60,170))
        rows=[("1 MONTH","₹1300",(80,220,255)),("OFFLINE LIFETIME","₹2000",(255,90,190)),("ONLINE LIFETIME","₹3000",(255,210,63))]
        for i,(lab,pr,col) in enumerate(rows):
            kk=ease_out_back((u-0.2-i*0.15)/0.35)
            y=440+i*105
            paint_text(ctx,lab,W/2-150,y,52,scale=max(kk,0.01),fill=(255,255,255),stroke=(20,5,40),font="LuckiestGuy.ttf")
            paint_text(ctx,pr,W/2+300,y,76,scale=max(kk,0.01),fill=(255,255,255),stroke=(20,5,40),font="Baloo2.ttf",glow=col,sw=5)
        pb=1+0.06*math.sin(t*9); kb=ease_out_back((u-0.7)/0.35)
        paint_text(ctx,"BOOK NOW",W/2,800,96,scale=max(kb,0.01)*pb,fill=(30,25,28),stroke=(255,210,63),sw=0,font="LuckiestGuy.ttf",box=(255,210,63),pad=22)
        paint_text(ctx,"LINK IN BIO",W/2,935,60,scale=max(ease_out_back((u-0.9)/0.35),0.01),fill=(255,255,255),stroke=(230,57,70),font="LuckiestGuy.ttf")
        draw_character(ctx,"golu",190,1290+bob(t,2),0.85,mouth=m("golu"),expr="happy",t=t,arm=("cheer","down"))
        draw_character(ctx,"nikki",540,1230+bob(t,2,2),0.95,mouth=m("nikki"),expr="love",t=t,arm=("down","thumbs"))
        draw_character(ctx,"raju",890,1300+bob(t,2,1),0.85,mouth=m("raju"),expr="normal",t=t,look=(-0.3,0.3),arm=("down","up"),blink=blink(t,0.4))
        confetti(ctx,t,S5+0.3,seed=13,n=120,dur=END-S5)
    ctx.identity_matrix()
    vignette(ctx); flash(ctx,t,STARTS+[GTA_T,P1300_T])
    paint_text(ctx,"CHEAP PC GAMES STORE",W/2,165,44,fill=(255,255,255),stroke=(40,25,70),font="LuckiestGuy.ttf",alpha=0.95)
    caption(ctx,tl,t)
    return surf

if __name__=="__main__":
    meta={"cover_ms":int((C3+1.3)*1000),"duration":END}
    if PREVIEW:
        pts=[("1",0.6),("1b",P1300_T+0.5),("2",PLANS3_T+0.5),("3",C2+0.6),("3q",C3Q+0.5),("3c",C3+1.3),("4",CUS_T+0.8),("5",S5+1.8)]
        for n_,tt in pts: frame(tt).write_to_png(f"out/r3_{n_}.png")
        json.dump(meta,open("out/reel003_meta.json","w")); print(meta); sys.exit()
    encode(frame,NF,"out/reel003_mix.wav",OUT); json.dump(meta,open("out/reel003_meta.json","w")); print("done",OUT,meta)
