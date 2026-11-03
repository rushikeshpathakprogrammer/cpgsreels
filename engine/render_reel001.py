"""Reel 001 - 'Jeb.exe Has Stopped Working' (Golu & Raju, ₹99 hook)."""
import math, subprocess, sys, json, os, colorsys
import numpy as np, cairo, soundfile as sf
sys.path.insert(0, os.path.dirname(__file__))
from draw import *
import sfx

FPS = 30
AUD = "audio/reel001"
OUT = sys.argv[1] if len(sys.argv)>1 else "out/reel001.mp4"
PREVIEW = "--preview" in sys.argv

LINES = [  # id, speaker, caption chunks (highlight with *word*)
 ("01","golu",["YESSS! *NAYA GAME*","AA GAYA BHAI!","CHALO, PRICE","CHECK KARTE HAIN..."]),
 ("02","golu",["KYAAA?! ITNA","*MEHENGA?!*","ARRE BAAP RE...","PRICE DEKH KE TOH","MERA PC BHI","*HANG* HO GAYA!"]),
 ("03","raju",["ARRE GOLU,","*FULL PRICE* KAUN","DETA HAI AAJKAL?","*CHEAP PC GAMES*","PE DEKH NA!"]),
 ("04","golu",["SIRF *₹99?!*","SACH MEIN?!"]),
 ("05","raju",["HAAN BHAI!","YAHAN GAMES","SHURU HI HOTE HAIN","SIRF *₹99* SE!"]),
 ("06","golu",["WAH! *GAME*","BHI KHELA...","AUR *JEB* BHI","BACHI! HEHE!"]),
 ("07","raju",["TOH DER KIS","BAAT KI?","GAMES *₹99* SE SHURU...","*SASTE* MEIN KHARIDO,","APNI *JEB BACHAO!*"]),
]
GAPS = {"01":0.55,"02":0.5,"03":1.3,"04":0.45,"05":0.5,"06":0.55}  # gap after line (03 -> phone reveal)

# ---------- timeline ----------
SR = sfx.SR
voice = {}; t = 0.6; timeline = []
for lid, spk, chunks in LINES:
    a, sr = sf.read(f"{AUD}/{lid}.wav", dtype="float32")
    if a.ndim>1: a=a.mean(1)
    if sr != SR:
        x = np.linspace(0, len(a)/sr, int(len(a)*SR/sr), endpoint=False)
        a = np.interp(x, np.arange(len(a))/sr, a).astype(np.float32)
    d = len(a)/SR
    timeline.append(dict(id=lid, spk=spk, chunks=chunks, start=t, end=t+d, audio=a))
    t += d + GAPS.get(lid, 0.6)
END = timeline[-1]["end"] + 1.8
L = {x["id"]: x for x in timeline}
NF = int(END*FPS)
print("duration", round(END,2), "frames", NF)

# scene boundaries
S_RAJU_IN = L["02"]["end"] + 0.25
S_PHONE   = L["03"]["end"] + 0.15
S_TWO_B   = L["04"]["end"] + 0.2
S_GAMING  = L["05"]["end"] + 0.25
S_END     = L["06"]["end"] + 0.25
PRICE_SHOW = L["02"]["start"] + 0.05
ERROR_POP  = L["02"]["start"] + 3.0
DROP_T     = S_PHONE + 0.75

# ---------- audio mix ----------
N = int(END*SR)+SR
mix = np.zeros(N, np.float32); vtrack = np.zeros(N, np.float32)
spk_env = {"golu": np.zeros(NF+2), "raju": np.zeros(NF+2)}
for ln in timeline:
    s = int(ln["start"]*SR); a = ln["audio"]; a = a/ (np.abs(a).max()+1e-6) * 0.9
    vtrack[s:s+len(a)] += a
    # per-frame RMS envelope for lip sync
    hop = SR//FPS
    for i in range(0, len(a), hop):
        fi = int((ln["start"] + i/SR)*FPS)
        if fi < NF: spk_env[ln["spk"]][fi] = float(np.sqrt(np.mean(a[i:i+hop]**2)))
for k in spk_env:
    e = spk_env[k]; m = np.percentile(e[e>0], 90) if (e>0).any() else 1
    spk_env[k] = np.clip(e/m, 0, 1)

def add(snd, at, gain=1.0):
    s=int(at*SR); e=min(N, s+len(snd)); mix[s:e]+=snd[:e-s]*gain
add(sfx.pop(), 0.15); add(sfx.boing(), 0.35, 0.6)
add(sfx.shock(), PRICE_SHOW, 0.9); add(sfx.error_buzz(), ERROR_POP, 0.8)
add(sfx.whoosh(), S_RAJU_IN, 1.0); add(sfx.whoosh(), S_PHONE, 1.0); add(sfx.pop(), S_PHONE+0.5, 0.8)
add(sfx.chaching(), DROP_T, 1.0); add(sfx.sparkle(), DROP_T+0.2, 1.0)
add(sfx.whoosh(), S_TWO_B, 0.8); add(sfx.whoosh(), S_GAMING, 0.8); add(sfx.sparkle(), S_GAMING+0.6, 0.8)
add(sfx.whoosh(), S_END, 1.0); add(sfx.chaching(), S_END+0.4, 0.8)
music = sfx.chiptune(END+1)[:N]; music = np.pad(music, (0, N-len(music)))
# duck music under voice
venv = np.convolve(np.abs(vtrack), np.ones(SR//10)/(SR//10), mode="same")
duck = np.where(venv>0.01, 0.35, 1.0).astype(np.float32)
duck = np.convolve(duck, np.ones(SR//8)/(SR//8), mode="same")
final = vtrack*1.0 + mix*0.55 + music*0.55*duck
fade = int(SR*1.0); final[int(END*SR)-fade:int(END*SR)] *= np.linspace(1,0,fade)
final = final[:int(END*SR)]; final = final/ max(1.0, np.abs(final).max()/0.95)
os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
sf.write("out/reel001_mix.wav", final, SR)

# ---------- visuals ----------
def active_line(t):
    for ln in timeline:
        if ln["start"] <= t < ln["end"]: return ln
    return None
def mouth_of(kind, t):
    fi = int(t*FPS); e = spk_env[kind]
    return float(max(e[max(0,fi-1):fi+2].max(), 0)) if fi < len(e) else 0.0
def blink(t, seed): return ((t + seed) % 3.1) < 0.12

BG = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
def build_room():
    c = cairo.Context(BG)
    g = cairo.LinearGradient(0,0,0,H); g.add_color_stop_rgb(0,*hexc("#3A2466")); g.add_color_stop_rgb(1,*hexc("#1C1838"))
    c.set_source(g); c.paint()
    for i in range(0,W,90):  # wall panels
        c.rectangle(i,0,2,1350); c.set_source_rgba(1,1,1,0.04); c.fill()
    # shelves with game boxes
    cols = ["#FF4D6D","#5E60CE","#FFD23F","#3BCEAC","#FF9F1C","#4CC9F0"]
    for sy, xs in [(420,(40,260)),(700,(40,220))]:
        rrect(c,xs[0]-10,sy,xs[1]-xs[0]+40,24,6); fill_stroke(c,hexc("#8A5A3C"),5)
        x=xs[0]
        for k in range(4):
            rrect(c,x,sy-150+k*6,42,150-k*6,6); fill_stroke(c,hexc(cols[(k+sy)%6]),5); x+=48
    # poster
    rrect(c,760,250,240,320,14); fill_stroke(c,hexc("#26214A"),6)
    star(c,880,370,70); c.set_source_rgb(*hexc("#FFD23F")); c.fill()
    # floor
    c.rectangle(0,1350,W,H-1350); c.set_source_rgb(*hexc("#2A1F3D")); c.fill()
build_room()

def led_strip(ctx, t):
    for i in range(24):
        h=(i/24 + t*0.25)%1; r,g,b=colorsys.hsv_to_rgb(h,0.75,1)
        ellipse(ctx, 25+i*45, 70, 14, 14); ctx.set_source_rgba(r,g,b,0.95); ctx.fill()
        ellipse(ctx, 25+i*45, 70, 32, 32); ctx.set_source_rgba(r,g,b,0.18); ctx.fill()

def brand(ctx, t):
    paint_text(ctx, "CHEAP PC GAMES STORE", W/2, 165, 44, fill=(255,255,255), stroke=(40,25,70), font="LuckiestGuy.ttf", alpha=0.95)

def screen_game_shop(ctx, x, y, w, h, t):
    ctx.set_source_rgb(*hexc("#101827")); ctx.rectangle(x,y,w,h); ctx.fill()
    if t < PRICE_SHOW:
        k = ease_out_back((t-0.3)/0.4)
        paint_text(ctx, "NEW GAME!", x+w/2, y+h/2, 64, scale=max(k,0.01), fill=(255,210,63), font="LuckiestGuy.ttf")
    else:
        g=cairo.LinearGradient(x,y,x,y+h*0.55); g.add_color_stop_rgb(0,*hexc("#6A4C93")); g.add_color_stop_rgb(1,*hexc("#1982C4"))
        ctx.set_source(g); ctx.rectangle(x,y,w,h*0.55); ctx.fill()
        star(ctx,x+w/2,y+h*0.27,60); ctx.set_source_rgb(1,1,1); ctx.fill()
        k = ease_out_back((t-PRICE_SHOW)/0.35)
        paint_text(ctx, "₹3,999", x+w/2, y+h*0.77, 74, scale=max(k,0.01), fill=(255,77,109), font="Baloo2.ttf")
    if t >= ERROR_POP:
        k = ease_out_back((t-ERROR_POP)/0.3); ctx.save(); ctx.translate(x+w/2, y+h/2); ctx.scale(k,k)
        rrect(ctx,-200,-95,400,190,14); fill_stroke(ctx,(0.95,0.95,0.97),5)
        ctx.rectangle(-200,-95,400,40); ctx.set_source_rgb(*hexc("#E63946")); ctx.fill()
        ctx.restore()
        if k>0.6:
            paint_text(ctx,"ERROR",x+w/2-130,y+h/2-75,26,fill=(255,255,255),stroke=(200,40,50),sw=1,font="Baloo2.ttf",pad=6)
            paint_text(ctx,"JEB.EXE HAS",x+w/2,y+h/2+5,36,fill=(30,30,30),stroke=(255,255,255),sw=0,font="Baloo2.ttf",pad=6)
            paint_text(ctx,"STOPPED WORKING",x+w/2,y+h/2+50,36,fill=(30,30,30),stroke=(255,255,255),sw=0,font="Baloo2.ttf",pad=6)

def screen_gaming(ctx, x, y, w, h, t):
    g=cairo.LinearGradient(x,y,x,y+h); g.add_color_stop_rgb(0,*hexc("#4CC9F0")); g.add_color_stop_rgb(1,*hexc("#F72585")); ctx.set_source(g); ctx.rectangle(x,y,w,h); ctx.fill()
    for i in range(6):  # road stripes racing
        yy = y + ((t*400 + i*80) % (h+80)) - 40
        ctx.rectangle(x+w/2-8, yy, 16, 40); ctx.set_source_rgb(1,1,1); ctx.fill()
    rrect(ctx, x+w/2-45+40*math.sin(t*3), y+h-110, 90, 70, 14); fill_stroke(ctx, hexc("#FFD23F"), 5)
    paint_text(ctx, "WIN!", x+w-90, y+50, 44, fill=(255,255,255), font="LuckiestGuy.ttf", scale=1+0.1*math.sin(t*8))

def desk(ctx, t):
    rrect(ctx,-20,1180,W+40,120,10); fill_stroke(ctx,hexc("#9C6B45"),8)
    ctx.rectangle(-20,1300,W+40,H-1300); ctx.set_source_rgb(*hexc("#7A5236")); ctx.fill()
    for yy in range(1420,H,140): ctx.rectangle(-20,yy,W+40,4); ctx.set_source_rgba(0,0,0,0.15); ctx.fill()
    rrect(ctx,560,1140,300,46,10); fill_stroke(ctx,hexc("#2B2B33"),6)  # keyboard
    for i in range(10):
        r,g,b = colorsys.hsv_to_rgb((i/10+t*0.3)%1,0.7,1); ctx.rectangle(575+i*28,1152,20,20); ctx.set_source_rgb(r,g,b); ctx.fill()
    # CPU tower with RGB fan
    rrect(ctx,900,880,150,300,14); fill_stroke(ctx,hexc("#1B1B22"),7)
    for fy in (960,1090):
        r,g,b = colorsys.hsv_to_rgb((t*0.5+fy/1000)%1,0.8,1)
        ellipse(ctx,975,fy,48,48); ctx.set_source_rgb(r,g,b); ctx.set_line_width(8); ctx.stroke()
        ctx.save(); ctx.translate(975,fy); ctx.rotate(t*12)
        for k in range(3): ctx.rotate(2.09); ctx.move_to(0,0); ctx.curve_to(20,-10,30,-30,10,-38); ctx.close_path(); ctx.set_source_rgba(r,g,b,0.7); ctx.fill()
        ctx.restore()

def caption(ctx, t):
    ln = active_line(t)
    if not ln: return
    n = len(ln["chunks"]); dur = ln["end"]-ln["start"]
    lens = [len(c.replace("*",""))+4 for c in ln["chunks"]]; tot=sum(lens)
    acc = ln["start"]; idx=0
    for i,lx in enumerate(lens):
        seg = dur*lx/tot
        if t < acc+seg: idx=i; cst=acc; break
        acc += seg
    else: idx=n-1; cst=acc
    chunk = ln["chunks"][idx]; k = ease_out_back((t-cst)/0.18)
    words = chunk.split(" "); parts=[]; hl=False
    for w_ in words:
        if w_.startswith("*"): hl=True
        parts.append((w_.replace("*",""), hl))
        if w_.endswith("*"): hl=False
    # layout
    size=84; cy = 1390
    items=[]; total=0
    for txt, h in parts:
        surf,w,hh,_ = text_surface(txt,size,fill=(30,25,28) if h else (255,255,255),stroke=(30,25,28) if not h else (255,210,63),
                                   sw=8 if not h else 0,font="Baloo2.ttf",box=(255,210,63) if h else None,pad=14)
        items.append((txt,h,w)); total += w + 6
    scale = min(1.0, (W-80)/total) * k
    x = W/2 - total*scale/2
    for txt,h,w in items:
        paint_text(ctx, txt, x + w*scale/2, cy, size, scale=scale, fill=(30,25,28) if h else (255,255,255),
                   stroke=(30,25,28) if not h else (255,210,63), sw=8 if not h else 0, font="Baloo2.ttf", box=(255,210,63) if h else None, pad=14)
        x += (w+6)*scale
    # speaker tag
    name = "GOLU" if ln["spk"]=="golu" else "RAJU"
    col = (242,193,78) if ln["spk"]=="golu" else (47,165,138)
    paint_text(ctx, name, W/2, cy-95, 40, fill=(30,25,28), stroke=col, sw=0, font="LuckiestGuy.ttf", box=col, pad=12)

def frame(t):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    shake = (0,0)
    if PRICE_SHOW <= t < PRICE_SHOW+0.6 or ERROR_POP <= t < ERROR_POP+0.4:
        shake = (12*math.sin(t*90), 9*math.cos(t*77))
    # scene punch-in zoom on each scene start
    starts=[0, S_RAJU_IN, S_PHONE, S_TWO_B, S_GAMING, S_END]
    last=max([s for s in starts if s<=t]); z = 1 + 0.07*(1-ease_out((t-last)/0.3))
    ctx.translate(W/2+shake[0], H/2+shake[1]); ctx.scale(z,z); ctx.translate(-W/2,-H/2)
    bob = lambda f,ph=0: 5*math.sin(t*2*math.pi*f+ph)
    if t < S_RAJU_IN:   # scene A: Golu at PC
        ctx.set_source_surface(BG,0,0); ctx.paint(); led_strip(ctx,t)
        expr = "normal"
        if t >= PRICE_SHOW: expr = "shock"
        if t < 0.6: expr="happy"
        k = ease_out_back(t/0.45)
        draw_character(ctx,"golu",320,760+bob(1.2)+ (1-k)*300,1.15,mouth=mouth_of("golu",t),expr=expr,t=t,
                       look=(1,0.2),arm=("type","type") if t<PRICE_SHOW else ("up","up") if t>ERROR_POP else ("down","down"),blink=blink(t,0.3))
        draw_monitor(ctx,700,760,440,330,t,lambda c,x,y,w,h: screen_game_shop(c,x,y,w,h,t))
        desk(ctx,t)
        if t > PRICE_SHOW+0.8:  # wallet with moth
            u=t-(PRICE_SHOW+0.8)
            draw_wallet(ctx,140,1235,1.0)
            ctx.save(); ctx.translate(140+50*math.sin(u*3)-u*70,1150-u*230); ctx.scale(1.7,1.7); draw_moth(ctx,0,0,t); ctx.restore()
    elif t < S_PHONE:   # scene B: Raju enters
        ctx.set_source_surface(BG,0,0); ctx.paint(); led_strip(ctx,t)
        k = ease_out((t-S_RAJU_IN)/0.5)
        draw_character(ctx,"golu",290,760+bob(1.1),1.2,mouth=mouth_of("golu",t),expr="sad" if t<L["03"]["start"]+1 else "normal",t=t,look=(1,0),blink=blink(t,0.7))
        draw_character(ctx,"raju",790+(1-k)*600,770+bob(1.0,1.3),1.2,mouth=mouth_of("raju",t),expr="normal",t=t,look=(-1,0),
                       arm=("down","hold"),blink=blink(t,1.9))
        if k>0.9: draw_phone(ctx,940,1150,110,200,1.0)
    elif t < S_TWO_B:   # scene C: phone close-up, price drop
        PX = 600
        burst_bg(ctx,t)
        pk = ease_out_back((t-S_PHONE-0.2)/0.4)
        draw_character(ctx,"golu",200+(1-pk)*-400,1030,0.95,mouth=mouth_of("golu",t),expr="star" if t>DROP_T+0.3 else "shock",t=t,look=(1,-0.3),blink=False)
        k = ease_out_back((t-S_PHONE)/0.4)
        ctx.save(); ctx.translate(PX,800); ctx.scale(max(k,0.01)*0.88,max(k,0.01)*0.88); ctx.rotate(0.03*math.sin(t*2)); ctx.translate(-PX,-800)
        draw_phone(ctx,PX,800,600,1060)
        ctx.save(); rrect(ctx,PX-278,800-508,556,1016,38); ctx.clip()
        ctx.set_source_rgb(*hexc("#5E60CE")); ctx.rectangle(0,352,W,120); ctx.fill()
        paint_text(ctx,"CHEAP PC GAMES",PX,420,48,fill=(255,255,255),stroke=(40,30,90),font="LuckiestGuy.ttf")
        g=cairo.LinearGradient(0,500,0,880); g.add_color_stop_rgb(0,*hexc("#F72585")); g.add_color_stop_rgb(1,*hexc("#7209B7"))
        rrect(ctx,PX-230,500,460,380,24); ctx.set_source(g); ctx.fill()
        star(ctx,PX,690,110); ctx.set_source_rgb(1,1,1); ctx.fill()
        paint_text(ctx,"NAYA GAME",PX,930,56,fill=(30,25,28),stroke=(255,255,255),sw=0,font="LuckiestGuy.ttf")
        u = t-DROP_T
        old_a = 1.0 if u<0.25 else max(0.35, 1-(u-0.25)*2)
        paint_text(ctx,"₹3,999",PX,1020,70,fill=(150,150,150),stroke=(255,255,255),sw=0,font="Baloo2.ttf",alpha=old_a)
        if u>0:
            p=ease_out(u/0.25); ctx.move_to(PX-140,1022); ctx.line_to(PX-140+280*p,1022)
            ctx.set_source_rgb(*hexc("#E63946")); ctx.set_line_width(10); ctx.stroke()
        if u>0.3:
            kk=ease_out_back((u-0.3)/0.35)
            paint_text(ctx,"₹99",PX,1150,150,scale=max(kk,0.01)*(1+0.04*math.sin(t*10)),fill=(46,196,90),stroke=(20,70,35),font="Baloo2.ttf")
        pb = 1+0.05*math.sin(t*9)
        ctx.save(); ctx.translate(PX,1290); ctx.scale(pb,pb); rrect(ctx,-160,-40,320,80,40); fill_stroke(ctx,hexc("#FFD23F"),6); ctx.restore()
        paint_text(ctx,"BUY NOW",PX,1292,44,scale=pb,fill=(30,25,28),stroke=(255,210,63),sw=0,font="LuckiestGuy.ttf")
        ctx.restore(); ctx.restore()
        confetti(ctx,t,DROP_T+0.3,n=110,dur=3)
    elif t < S_GAMING:  # scene D: two-shot, Raju explains
        ctx.set_source_surface(BG,0,0); ctx.paint(); led_strip(ctx,t)
        draw_character(ctx,"golu",290,760+bob(1.6),1.2,mouth=mouth_of("golu",t),expr="star",t=t,look=(1,0),arm=("cheer","down"))
        draw_character(ctx,"raju",790,770+bob(1.0,1.3),1.2,mouth=mouth_of("raju",t),expr="normal",t=t,look=(-1,0),arm=("down","up"),blink=blink(t,1.1))
        for i in range(5):
            coin(ctx, 120+i*210, 330+40*math.sin(t*3+i), 38, t+i)
    elif t < S_END:     # scene E: happy gaming
        ctx.set_source_surface(BG,0,0); ctx.paint(); led_strip(ctx,t)
        draw_character(ctx,"golu",320,760+bob(2.2),1.15,mouth=mouth_of("golu",t),expr="happy",t=t,look=(1,0),arm=("type","type"))
        draw_monitor(ctx,700,760,440,330,t,lambda c,x,y,w,h: screen_gaming(c,x,y,w,h,t))
        desk(ctx,t)
        u=t-S_GAMING; wy = 1110 - 40*abs(math.sin(u*5))
        ctx.save(); ctx.translate(120,wy); ctx.rotate(0.25*math.sin(u*5)); draw_wallet(ctx,0,0,1.0,happy=True); ctx.restore()
        for i in range(4): coin(ctx, 60+i*45, wy-110-30*((u*2+i*0.3)%1)*5, 22, t+i)
    else:               # scene F: end card
        burst_bg(ctx,t,c1="#7B2CBF",c2="#5A189A",cy=700)
        u=t-S_END
        k1=ease_out_back(u/0.35); k2=ease_out_back((u-0.25)/0.35); k3=ease_out_back((u-0.5)/0.35)
        paint_text(ctx,"GAMES SIRF",W/2,420,96,scale=max(k1,0.01),fill=(255,255,255),stroke=(40,20,70),font="LuckiestGuy.ttf",rot=-0.03)
        paint_text(ctx,"₹99 SE!",W/2,590,190,scale=max(k2,0.01)*(1+0.03*math.sin(t*6)),fill=(255,210,63),stroke=(40,20,70),font="Baloo2.ttf",rot=-0.03)
        paint_text(ctx,"cheappcgames.in.net",W/2,780,58,scale=max(k3,0.01),fill=(30,25,28),stroke=(255,255,255),sw=0,font="Baloo2.ttf",box=(255,255,255))
        k4=ease_out_back((u-0.8)/0.35)
        paint_text(ctx,"LINK IN BIO",W/2,900,62,scale=max(k4,0.01)*(1+0.05*math.sin(t*8)),fill=(255,255,255),stroke=(230,57,70),font="LuckiestGuy.ttf")
        draw_character(ctx,"golu",300,1180+bob(2),1.1,mouth=mouth_of("golu",t),expr="happy",t=t,arm=("cheer","cheer"))
        draw_character(ctx,"raju",790,1190+bob(2,1),1.1,mouth=mouth_of("raju",t),expr="normal",t=t,look=(0,0.3),arm=("down","up"),blink=blink(t,0.4))
        confetti(ctx,t,S_END+0.2,seed=11,n=120,dur=END-S_END)
    ctx.identity_matrix()
    brand(ctx,t); caption(ctx,t)
    return surf

if __name__ == "__main__":
    if PREVIEW:
        from PIL import Image
        for name, tt in [("A",L["01"]["start"]+1.5),("A2",ERROR_POP+0.5),("B",L["03"]["start"]+1),("C",DROP_T+1.0),("D",L["05"]["start"]+1),("E",L["06"]["start"]+1),("F",S_END+1.5)]:
            s=frame(tt); s.write_to_png(f"out/prev_{name}.png")
        json.dump({"cover_ms":int((DROP_T+1.0)*1000),"duration":END}, open("out/reel001_meta.json","w"))
        sys.exit()
    cmd = ["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","bgra","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
           "-i","out/reel001_mix.wav","-c:v","libx264","-preset","medium","-crf","21","-maxrate","4500k","-bufsize","9000k",
           "-pix_fmt","yuv420p","-profile:v","high","-g","60","-c:a","aac","-b:a","128k","-ar","44100","-ac","2",
           "-movflags","+faststart","-shortest",OUT]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(NF):
        p.stdin.write(frame(i/FPS).get_data())
        if i % 150 == 0: print("frame", i, "/", NF, flush=True)
    p.stdin.close(); p.wait()
    json.dump({"cover_ms":int((DROP_T+1.0)*1000),"duration":END}, open("out/reel001_meta.json","w"))
    print("done", OUT)
