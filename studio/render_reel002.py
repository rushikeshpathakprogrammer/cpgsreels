"""Reel 002 - 'Trust Kaise Karein?' (Nikki asks, Raju & Golu prove: GST, Udyam/MSME, 2000+ customers, WhatsApp delivery proofs)."""
import math, sys, os, json
import numpy as np, cairo
sys.path.insert(0, os.path.dirname(__file__))
from draw import *
from reelkit import *
import sfx

AUD="audio/reel002"; OUT=sys.argv[1] if len(sys.argv)>1 and not sys.argv[1].startswith("--") else "out/reel002.mp4"
PREVIEW="--preview" in sys.argv
LINES=[
 ("01","nikki",["GOLU! SIRF *₹99* MEIN","*GAME?*","ITNA SASTA...","YAAR, INPE *TRUST*","KAISE KARUN?"]),
 ("02","golu",["ARRE NIKKI,","*TENSION* MAT LE!","RAJU, ZARA ISE","*PROOF* DIKHA DE!"]),
 ("03","raju",["DEKHO NIKKI,","CHEAP PC GAMES STORE","*GST REGISTERED* HAI...","AUR *UDYAM*,","YAANI *MSME REGISTERED* BHI!"]),
 ("04","nikki",["ACHHA JI?","AUR *CUSTOMERS* KA KYA?"]),
 ("05","raju",["*2000+* SE ZYADA","*HAPPY CUSTOMERS*","INPE TRUST KARTE HAIN!"]),
 ("06","golu",["AUR SUN!","WEBSITE PE *NEECHE SCROLL* KAR...","HAR DELIVERY KA","*WHATSAPP SCREENSHOT*","*PROOF* KE SAATH UPLOAD HAI!"]),
 ("07","nikki",["WAAH! ITNA SAARA","*PROOF?*","AB TOH *PAKKA TRUST* HAI!"]),
 ("08","raju",["TOH DER KIS BAAT KI?","GAMES *₹99* SE SHURU...","ABHI CHECK KARO,","*CHEAPPCGAMES.IN.NET*"]),
]
GAPS={"01":0.3,"02":0.35,"03":0.4,"04":0.3,"05":0.35,"06":0.3,"07":0.35}
tl=build_timeline(AUD,LINES,GAPS,lead=0.45)
L={x["id"]:x for x in tl}
END=tl[-1]["end"]+2.0
mx=Mixer(tl,END,["golu","raju","nikki"]); NF=mx.NF
print("duration",round(END,2))

S1=0; S2=L["02"]["start"]-0.15; S3=L["03"]["start"]-0.2; S4=L["04"]["start"]-0.15; S5=L["05"]["start"]-0.15
S6=L["06"]["start"]-0.15; S7=L["07"]["start"]-0.15; S8=L["08"]["start"]-0.15
STARTS=[S2,S3,S4,S5,S6,S7,S8]
GST_T=L["03"]["start"]+2.3; UDY_T=L["03"]["start"]+5.0
CNT_T=S5+0.25; SCROLL_T=S6+0.5; ZOOM_T=L["06"]["start"]+4.6

# ---- sound design ----
mx.add(sfx.pop(),0.1); mx.add(sfx.boing(),L["01"]["start"]+1.6,0.5)
for s in STARTS: mx.add(sfx.whoosh(),s-0.05,0.9)
mx.add(sfx.stamp(),GST_T,1.0); mx.add(sfx.sparkle(),GST_T+0.1,0.7)
mx.add(sfx.stamp(),UDY_T,1.0); mx.add(sfx.sparkle(),UDY_T+0.1,0.7)
mx.add(sfx.ticks(1.4),CNT_T,1.0); mx.add(sfx.chaching(),CNT_T+1.45,0.9)
mx.add(sfx.whoosh(),SCROLL_T,0.6); mx.add(sfx.whoosh(),SCROLL_T+1.5,0.6); mx.add(sfx.ding(),ZOOM_T,0.8)
for i in range(4): mx.add(sfx.heart_pop(),S7+0.2+i*0.25,0.7)
mx.add(sfx.chaching(),S8+0.5,0.8)
os.makedirs("out",exist_ok=True); mx.render("out/reel002_mix.wav",bpm=126)

def blink(t,seed): return ((t+seed)%3.3)<0.12
bob=lambda t,f,ph=0,a=6: a*math.sin(t*2*math.pi*f+ph)

def thought_bubble(ctx,x,y,t,k):
    if k<=0: return
    ctx.save(); ctx.translate(x,y); ctx.scale(k,k)
    for (dx,dy,r) in [(-150,150,18),(-115,105,28)]:
        ellipse(ctx,dx,dy,r,r); fill_stroke(ctx,(1,1,1),5)
    for (dx,dy,r) in [(-70,0,90),(40,-30,110),(150,10,90),(60,60,100),(-40,60,80)]:
        ellipse(ctx,dx,dy,r,r*0.85); ctx.set_source_rgb(1,1,1); ctx.fill()
    ctx.restore()
    paint_text(ctx,"SCAM??",x+40*k,y+15*k,int(80),scale=max(k,0.01),fill=(230,57,70),stroke=(255,255,255),sw=0,font="LuckiestGuy.ttf",rot=-0.05)
    for i in range(3):
        a=t*2+i*2.1
        paint_text(ctx,"?",x+230+i*60+10*math.sin(a),y-120+i*40+12*math.cos(a*1.3),70,scale=max(k,0.01),fill=(255,210,63),font="LuckiestGuy.ttf",rot=0.2*math.sin(a))

def badge(ctx,cx,cy,t,t0,title,sub,col1,col2):
    u=t-t0
    if u<0: return
    k=ease_out_back(u/0.35)*(1.6-0.6*ease_out(u/0.2)) if u<0.35 else 1.0
    ctx.save(); ctx.translate(cx,cy); ctx.rotate(-0.04); ctx.scale(k,k)
    rrect(ctx,-380,-150,760,300,46)
    g=cairo.LinearGradient(0,-150,0,150); g.add_color_stop_rgb(0,*hexc(col1)); g.add_color_stop_rgb(1,*hexc(col2)); ctx.set_source(g); ctx.fill_preserve()
    ctx.set_source_rgb(*INK); ctx.set_line_width(9); ctx.stroke()
    # shield icon
    ctx.save(); ctx.translate(-250,0)
    ctx.move_to(0,-100); ctx.curve_to(60,-80,85,-80,95,-75); ctx.curve_to(95,20,60,75,0,105); ctx.curve_to(-60,75,-95,20,-95,-75); ctx.curve_to(-85,-80,-60,-80,0,-100); ctx.close_path()
    fill_stroke(ctx,(1,1,1),8)
    ctx.move_to(-42,0); ctx.line_to(-10,35); ctx.line_to(48,-35); ctx.set_source_rgb(*hexc("#2EC45A")); ctx.set_line_width(20); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
    ctx.restore()
    # shine sweep
    sh=((u*0.8)%1.6)-0.3
    if 0<sh<1:
        ctx.save(); rrect(ctx,-380,-150,760,300,46); ctx.clip()
        x0=-380+sh*900; ctx.move_to(x0,-160); ctx.line_to(x0+80,-160); ctx.line_to(x0-20,160); ctx.line_to(x0-100,160); ctx.close_path()
        ctx.set_source_rgba(1,1,1,0.35); ctx.fill(); ctx.restore()
    ctx.restore()
    paint_text(ctx,title,cx+90,cy-38,78,scale=max(k,0.01),fill=(255,255,255),stroke=(30,25,28),font="LuckiestGuy.ttf",rot=-0.04)
    paint_text(ctx,sub,cx+90,cy+52,44,scale=max(k,0.01),fill=(30,25,28),stroke=(255,255,255),sw=0,font="Baloo2.ttf",rot=-0.04)

def check_badge(ctx,x,y,r):
    ellipse(ctx,x,y,r,r); fill_stroke(ctx,hexc("#2EC45A"),4)
    ctx.move_to(x-r*0.45,y); ctx.line_to(x-r*0.1,y+r*0.38); ctx.line_to(x+r*0.5,y-r*0.35)
    ctx.set_source_rgb(1,1,1); ctx.set_line_width(max(2,r*0.22)); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()

def wa_card(ctx,x,y,w,h,seed):
    rng=np.random.default_rng(seed)
    rrect(ctx,x,y,w,h,18); ctx.set_source_rgb(*hexc("#ECE5DD")); ctx.fill_preserve(); ctx.set_source_rgb(*INK); ctx.set_line_width(4); ctx.stroke()
    ctx.save(); rrect(ctx,x,y,w,h,18); ctx.clip()
    ctx.rectangle(x,y,w,52); ctx.set_source_rgb(*hexc("#075E54")); ctx.fill()
    ellipse(ctx,x+30,y+26,16,16); ctx.set_source_rgb(*hexc("#B6D7D2")); ctx.fill()
    rrect(ctx,x+56,y+18,rng.uniform(70,120),14,7); ctx.set_source_rgba(1,1,1,0.85); ctx.fill()
    yy=y+70
    for j in range(4):
        out = (j%2==1)
        bw=rng.uniform(w*0.45,w*0.7); bh=rng.uniform(34,52)
        bx = x+w-bw-12 if out else x+12
        rrect(ctx,bx,yy,bw,bh,10); ctx.set_source_rgb(*hexc("#DCF8C6" if out else "#FFFFFF")); ctx.fill()
        for k in range(int(bh//18)):
            rrect(ctx,bx+10,yy+10+k*16,bw*rng.uniform(0.5,0.85)-20,8,4); ctx.set_source_rgba(0,0,0,0.22); ctx.fill()
        if out:  # blue double ticks
            for dx in (0,9):
                ctx.move_to(bx+bw-30+dx,yy+bh-12); ctx.line_to(bx+bw-25+dx,yy+bh-7); ctx.line_to(bx+bw-16+dx,yy+bh-17)
                ctx.set_source_rgb(*hexc("#34B7F1")); ctx.set_line_width(3); ctx.stroke()
        yy+=bh+12
        if yy>y+h-40: break
    ctx.restore()

def website(ctx,x,y,w,h,scroll,t):
    # browser chrome
    ctx.save(); rrect(ctx,x,y,w,h,30); ctx.clip()
    ctx.set_source_rgb(*hexc("#F5F5F7")); ctx.rectangle(x,y,w,h); ctx.fill()
    ctx.save(); ctx.translate(0,-scroll)
    yy=y+90
    g=cairo.LinearGradient(0,yy,0,yy+300); g.add_color_stop_rgb(0,*hexc("#3A0CA3")); g.add_color_stop_rgb(1,*hexc("#7209B7"))
    ctx.rectangle(x,yy,w,300); ctx.set_source(g); ctx.fill()
    paint_text(ctx,"CHEAP PC GAMES",x+w/2,yy+110,52,fill=(255,255,255),stroke=(40,20,70),font="LuckiestGuy.ttf")
    paint_text(ctx,"Games ₹99 se shuru",x+w/2,yy+190,38,fill=(255,210,63),stroke=(40,20,70),sw=3,font="Baloo2.ttf")
    yy+=330
    cols=["#F72585","#4CC9F0","#FFD23F","#3BCEAC","#FF9F1C","#5E60CE"]
    for r in range(2):
        for c in range(2):
            cx=x+30+c*(w-60)/2; cw=(w-60)/2-20
            rrect(ctx,cx,yy,cw,200,18); ctx.set_source_rgb(*hexc(cols[(r*2+c)%6])); ctx.fill()
            star(ctx,cx+cw/2,yy+90,45); ctx.set_source_rgba(1,1,1,0.9); ctx.fill()
            rrect(ctx,cx+20,yy+150,cw-40,30,10); ctx.set_source_rgb(1,1,1); ctx.fill()
        yy+=230
    # proofs section
    ctx.rectangle(x,yy,w,110); ctx.set_source_rgb(*hexc("#25D366")); ctx.fill()
    paint_text(ctx,"DELIVERY PROOFS",x+w/2,yy+58,50,fill=(255,255,255),stroke=(10,90,50),font="LuckiestGuy.ttf")
    yy+=130
    for r in range(6):
        for c in range(2):
            wa_card(ctx,x+24+c*(w-48)/2,yy,(w-48)/2-14,300,seed=r*2+c)
        yy+=320
    ctx.restore()
    # address bar (fixed)
    ctx.rectangle(x,y,w,80); ctx.set_source_rgb(1,1,1); ctx.fill()
    rrect(ctx,x+24,y+18,w-48,46,23); ctx.set_source_rgb(*hexc("#E9E9EE")); ctx.fill()
    paint_text(ctx,"cheappcgames.in.net",x+w/2,y+42,30,fill=(60,60,70),stroke=(233,233,238),sw=0,font="Baloo2.ttf",pad=6)
    ctx.restore()

def frame(t):
    surf=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); ctx=cairo.Context(surf)
    last=max([0]+[s for s in STARTS if s<=t]); z=1+0.06*(1-ease_out((t-last)/0.3))
    shake=(0,0)
    for st in (GST_T,UDY_T):
        if st<=t<st+0.25: shake=(14*math.sin(t*95)*(1-(t-st)/0.25),10*math.cos(t*80)*(1-(t-st)/0.25))
    ctx.translate(W/2+shake[0],H/2+shake[1]); ctx.scale(z,z); ctx.translate(-W/2,-H/2)
    m=lambda k: mx.mouth(k,t)
    if t<S2:   # Nikki doubting
        bokeh_bg(ctx,t,"#5B2A86","#1E1240",seed=1,tint=(1,0.6,0.85))
        backlight(ctx,W/2,760,520,(1,0.55,0.8),0.35)
        k=ease_out_back((t-0.05)/0.45)
        draw_character(ctx,"nikki",W/2,820+bob(t,1.1)+(1-k)*400,1.3,mouth=m("nikki"),expr="doubt",t=t,look=(0.6,-0.3),arm=("hip","phone"),blink=blink(t,0.2))
        thought_bubble(ctx,330,330,t,ease_out_back((t-L["01"]["start"]-1.4)/0.4))
    elif t<S3:   # Golu reassures
        bokeh_bg(ctx,t,"#3A2466","#1C1838",seed=2,tint=(1,0.9,0.6))
        backlight(ctx,300,760,450,(1,0.85,0.4),0.3); backlight(ctx,790,760,450,(1,0.5,0.75),0.25)
        k=ease_out((t-S2)/0.4)
        draw_character(ctx,"golu",300-(1-k)*600,780+bob(t,1.6),1.2,mouth=m("golu"),expr="happy" if m("golu")<0.1 else "normal",t=t,look=(1,0),arm=("thumbs","down"),blink=blink(t,0.5))
        draw_character(ctx,"nikki",800,800+bob(t,1.1,1),1.2,mouth=m("nikki"),expr="doubt",t=t,look=(-1,0),arm=("down","phone"),blink=blink(t,1.4))
    elif t<S4:   # badges
        burst_bg(ctx,t,c1="#0F3B8C",c2="#0A2A66",cy=700,n=20,speed=0.1)
        bokeh_bg_alpha=None
        paint_text(ctx,"100% LEGIT STORE",W/2,300,66,fill=(255,255,255),stroke=(10,30,80),font="LuckiestGuy.ttf",glow=(80,160,255),
                   scale=max(ease_out_back((t-S3)/0.4),0.01))
        badge(ctx,W/2,560,t,GST_T,"GST","REGISTERED","#FFD23F","#F4A300")
        badge(ctx,W/2,900,t,UDY_T,"UDYAM","MSME REGISTERED","#3BCEAC","#16946F")
        backlight(ctx,840,1300,380,(0.4,1,0.8),0.25)
        draw_character(ctx,"raju",840,1250+bob(t,1.0),0.95,mouth=m("raju"),expr="normal",t=t,look=(-0.6,-0.8),arm=("point","down"),blink=blink(t,0.9))
    elif t<S5:   # Nikki close-up sass
        burst_bg(ctx,t,c1="#FF8FB1",c2="#FF5D8F",cy=650,speed=0.2)
        draw_character(ctx,"nikki",W/2,820+bob(t,1.4),1.55,mouth=m("nikki"),expr="doubt",t=t,look=(0.8,0),arm=("hip","hip"),blink=False)
    elif t<S6:   # 2000+ counter
        bokeh_bg(ctx,t,"#2B0B57","#12062B",seed=5,tint=(1,0.8,0.3))
        u=t-CNT_T; val=int(2000*ease_out(min(max(u,0)/1.4,1)))
        txt=f"{val:,}"+("+" if u>1.45 else "")
        pk=1+0.12*max(0,1-abs(u-1.45)/0.2)
        backlight(ctx,W/2,520,500,(1,0.8,0.2),0.35)
        paint_text(ctx,txt,W/2,500,230,scale=pk,fill=(255,255,255),stroke=(60,20,0),font="Baloo2.ttf",grad=((255,240,140),(255,150,0)),glow=(255,190,40))
        paint_text(ctx,"HAPPY CUSTOMERS",W/2,690,78,scale=max(ease_out_back((u-1.3)/0.4),0.01),fill=(255,255,255),stroke=(40,20,70),font="LuckiestGuy.ttf")
        for i in range(12):  # avatar faces popping
            r_,c_=divmod(i,6); ax=110+c_*172; ay=850+r_*170
            kk=ease_out_back((u-0.15-i*0.08)/0.3)
            if kk<=0: continue
            ctx.save(); ctx.translate(ax,ay); ctx.scale(kk,kk)
            ellipse(ctx,0,0,62,62); fill_stroke(ctx,hexc(["#C68B59","#A86E46","#D49A6A","#B9784F"][i%4]),6)
            for sx in (-20,20): ellipse(ctx,sx,-10,7,9); ctx.set_source_rgb(*INK); ctx.fill()
            ctx.arc(0,8,24,0.2,math.pi-0.2); ctx.set_source_rgb(*INK); ctx.set_line_width(6); ctx.stroke()
            ctx.restore()
            if kk>0.9:
                hy=ay-80-((t*60+i*37)%120); ctx.save(); ctx.translate(ax+30,hy); ctx.scale(0.6,0.6)
                ctx.move_to(0,22); ctx.curve_to(-46,-6,-24,-44,0,-18); ctx.curve_to(24,-44,46,-6,0,22); ctx.close_path()
                ctx.set_source_rgba(1,0.25,0.42,0.85); ctx.fill(); ctx.restore()
        draw_character(ctx,"raju",230,1330+bob(t,1.0),0.85,mouth=m("raju"),expr="happy" if m("raju")<0.1 else "normal",t=t,look=(0.5,-1),arm=("down","point"))
    elif t<S7:   # website scroll to WhatsApp proofs
        bokeh_bg(ctx,t,"#0B6E4F","#04301F",seed=7,tint=(0.6,1,0.7))
        PX,PY,PW,PH=610,770,640,1150
        u=t-SCROLL_T
        sc=780*ease_out(min(max(u,0)/2.2,1)) + 60*max(0,u-2.2)
        draw_phone(ctx,PX,PY,PW,PH)
        website(ctx,PX-PW/2+22,PY-PH/2+22,PW-44,PH-44,sc,t)
        # finger swipe icon
        if 0<u<2.8:
            fy=PY+250-((u*1.3)%1)*400
            ellipse(ctx,PX+170,fy,34,34); ctx.set_source_rgba(1,1,1,0.75); ctx.fill_preserve(); ctx.set_source_rgb(*INK); ctx.set_line_width(5); ctx.stroke()
        # zoom on a proof card
        zk=ease_out_back((t-ZOOM_T)/0.4)
        if zk>0:
            ctx.save(); ctx.translate(PX,PY+80); ctx.scale(zk,zk); ctx.rotate(0.04)
            wa_card(ctx,-230,-260,460,520,seed=3)
            ctx.restore()
            w_,_=paint_text(ctx,"DELIVERED",PX+30,PY+420,58,scale=max(zk,0.01),fill=(255,255,255),stroke=(10,90,50),font="Baloo2.ttf",box=(37,211,102),pad=16)
            if zk>0.05: check_badge(ctx,PX+30-w_/2-34,PY+420,30*zk)
        pk=ease_out_back((t-S6-0.2)/0.4)
        draw_character(ctx,"golu",150+(1-pk)*-400,1080,0.85,mouth=m("golu"),expr="normal",t=t,look=(1,-0.4),blink=blink(t,1.0))
    elif t<S8:   # Nikki convinced
        burst_bg(ctx,t,c1="#FFB3C6",c2="#FF85A1",cy=700,speed=0.25)
        backlight(ctx,W/2,760,520,(1,1,1),0.35)
        draw_character(ctx,"golu",210,880+bob(t,2.2),0.95,mouth=m("golu"),expr="happy",t=t,arm=("cheer","down"))
        draw_character(ctx,"nikki",700,800+bob(t,2.0,1),1.25,mouth=m("nikki"),expr="love",t=t,arm=("down","thumbs"))
        for i in range(10):
            hx=(i*113+40)%W; hy=H-((t-S7)*420+i*160)%(H+200)
            ctx.save(); ctx.translate(hx,hy); ctx.scale(1.1,1.1); ctx.rotate(0.3*math.sin(t*3+i))
            ctx.move_to(0,22); ctx.curve_to(-46,-6,-24,-44,0,-18); ctx.curve_to(24,-44,46,-6,0,22); ctx.close_path()
            ctx.set_source_rgba(1,0.2,0.4,0.8); ctx.fill(); ctx.restore()
    else:        # end card
        burst_bg(ctx,t,c1="#7B2CBF",c2="#5A189A",cy=600)
        u=t-S8
        chips=[("GST",(255,210,63)),("UDYAM",(59,206,172)),("2000+",(255,133,161))]
        for i,(txt,col) in enumerate(chips):
            kk=ease_out_back((u-0.1-i*0.18)/0.35)
            cx_=185+i*355
            w_,_=paint_text(ctx,txt,cx_-22,300,54,scale=max(kk,0.01),fill=(30,25,28),stroke=col,sw=0,font="Baloo2.ttf",box=col,pad=18)
            if kk>0.05: check_badge(ctx,cx_-22+w_/2+8,300,26*kk)
        k1=ease_out_back((u-0.5)/0.4)
        paint_text(ctx,"GAMES SIRF",W/2,460,92,scale=max(k1,0.01),fill=(255,255,255),stroke=(40,20,70),font="LuckiestGuy.ttf",rot=-0.03)
        paint_text(ctx,"₹99 SE!",W/2,620,180,scale=max(ease_out_back((u-0.7)/0.4),0.01)*(1+0.03*math.sin(t*6)),fill=(255,255,255),stroke=(40,20,70),
                   font="Baloo2.ttf",rot=-0.03,grad=((255,245,150),(255,160,0)),glow=(255,200,60))
        paint_text(ctx,"cheappcgames.in.net",W/2,800,56,scale=max(ease_out_back((u-0.9)/0.4),0.01),fill=(30,25,28),stroke=(255,255,255),sw=0,font="Baloo2.ttf",box=(255,255,255))
        paint_text(ctx,"LINK IN BIO",W/2,915,60,scale=max(ease_out_back((u-1.1)/0.4),0.01)*(1+0.05*math.sin(t*8)),fill=(255,255,255),stroke=(230,57,70),font="LuckiestGuy.ttf")
        draw_character(ctx,"golu",190,1250+bob(t,2),0.9,mouth=m("golu"),expr="happy",t=t,arm=("cheer","down"))
        draw_character(ctx,"raju",890,1260+bob(t,2,1),0.9,mouth=m("raju"),expr="normal",t=t,look=(-0.3,0.3),arm=("down","up"),blink=blink(t,0.4))
        draw_character(ctx,"nikki",540,1180+bob(t,2,2),1.0,mouth=m("nikki"),expr="love",t=t,arm=("down","thumbs"))
        confetti(ctx,t,S8+0.3,seed=11,n=120,dur=END-S8)
    ctx.identity_matrix()
    vignette(ctx); flash(ctx,t,STARTS)
    paint_text(ctx,"CHEAP PC GAMES STORE",W/2,165,44,fill=(255,255,255),stroke=(40,25,70),font="LuckiestGuy.ttf",alpha=0.95)
    caption(ctx,tl,t)
    return surf

COVER=S6+0.0
if __name__=="__main__":
    meta={"cover_ms":int((GST_T+UDY_T)/2*1000+1800),"duration":END}
    if PREVIEW:
        pts=[("1",L["01"]["start"]+2.5),("2",L["02"]["start"]+1.5),("3",UDY_T+1.0),("4",L["04"]["start"]+0.8),("5",CNT_T+2.0),("6a",SCROLL_T+2.0),("6b",ZOOM_T+1.0),("7",L["07"]["start"]+1.5),("8",S8+2.0)]
        for n_,tt in pts: frame(tt).write_to_png(f"out/r2_{n_}.png")
        json.dump(meta,open("out/reel002_meta.json","w")); print(meta); sys.exit()
    encode(frame,NF,"out/reel002_mix.wav",OUT); json.dump(meta,open("out/reel002_meta.json","w")); print("done",OUT,meta)
