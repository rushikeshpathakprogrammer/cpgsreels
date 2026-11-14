"""Cartoon drawing primitives (pycairo): characters, room, phone, effects."""
import math, cairo
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
INK = (0.12, 0.10, 0.11)
def hexc(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))
def ease_out_back(x, s=1.70158):
    x=min(max(x,0),1); x-=1; return x*x*((s+1)*x+s)+1
def ease_out(x): x=min(max(x,0),1); return 1-(1-x)**3
def clamp(x,a=0,b=1): return max(a,min(b,x))

def fill_stroke(ctx, fill, lw=7, stroke=INK):
    ctx.set_source_rgb(*fill); ctx.fill_preserve(); ctx.set_source_rgb(*stroke); ctx.set_line_width(lw); ctx.stroke()
def ellipse(ctx, x, y, rx, ry):
    ctx.save(); ctx.translate(x,y); ctx.scale(rx,ry); ctx.arc(0,0,1,0,2*math.pi); ctx.restore()
def rrect(ctx, x, y, w, h, r):
    ctx.new_sub_path(); ctx.arc(x+w-r,y+r,r,-math.pi/2,0); ctx.arc(x+w-r,y+h-r,r,0,math.pi/2)
    ctx.arc(x+r,y+h-r,r,math.pi/2,math.pi); ctx.arc(x+r,y+r,r,math.pi,1.5*math.pi); ctx.close_path()
def star(ctx, x, y, r, n=5, inner=0.45, rot=-math.pi/2):
    for i in range(2*n):
        rr = r if i%2==0 else r*inner; a = rot + i*math.pi/n
        (ctx.move_to if i==0 else ctx.line_to)(x+rr*math.cos(a), y+rr*math.sin(a))
    ctx.close_path()

# ---------- text via PIL (cached) ----------
FONTS = "/home/claude/fonts/"
_cache = {}
def text_surface(text, size, fill=(255,255,255), stroke=(25,20,22), sw=None, font="LuckiestGuy.ttf", box=None, pad=18, grad=None, glow=None):
    key=(text,size,fill,stroke,sw,font,box,grad,glow)
    if key in _cache: return _cache[key]
    f = ImageFont.truetype(FONTS+font, size)
    if font=="Baloo2.ttf": f.set_variation_by_axes([800])
    sw = sw if sw is not None else max(2,size//9)
    if glow: pad = max(pad, size//3)
    l,t,r,b = f.getbbox(text, stroke_width=sw)
    w,h = r-l+2*pad, b-t+2*pad
    im = Image.new("RGBA",(w,h),(0,0,0,0)); d=ImageDraw.Draw(im)
    if box: d.rounded_rectangle([0,0,w-1,h-1], radius=h//4, fill=box+(255,), outline=(25,20,22,255), width=6)
    if glow:
        from PIL import ImageFilter
        gl = Image.new("RGBA",(w,h),(0,0,0,0)); ImageDraw.Draw(gl).text((pad-l,pad-t), text, font=f, fill=glow+(255,), stroke_width=sw+10, stroke_fill=glow+(255,))
        gl = gl.filter(ImageFilter.GaussianBlur(size/7)); im = Image.alpha_composite(im, gl); d = ImageDraw.Draw(im)
    d.text((pad-l,pad-t), text, font=f, fill=fill+(255,), stroke_width=sw, stroke_fill=stroke+(255,))
    if grad:
        mask = Image.new("L",(w,h),0); ImageDraw.Draw(mask).text((pad-l,pad-t), text, font=f, fill=255)
        g = Image.new("RGBA",(w,h)); gd=ImageDraw.Draw(g); top,bot = grad
        for yy in range(h):
            u=yy/max(1,h-1); gd.line([(0,yy),(w,yy)], fill=tuple(int(top[i]*(1-u)+bot[i]*u) for i in range(3))+(255,))
        im.paste(g,(0,0),mask)
    a = np.array(im).astype(np.float32); al=a[...,3:4]/255.0
    bgra = np.dstack([a[...,2:3]*al, a[...,1:2]*al, a[...,0:1]*al, a[...,3:4]]).astype(np.uint8)
    bgra = np.ascontiguousarray(bgra)
    surf = cairo.ImageSurface.create_for_data(memoryview(bgra), cairo.FORMAT_ARGB32, w, h, w*4)
    _cache[key]=(surf,w,h,bgra); return _cache[key]

def paint_text(ctx, text, cx, cy, size, scale=1.0, alpha=1.0, rot=0, **kw):
    if scale <= 0.005 or alpha <= 0: return 0, 0
    surf,w,h,_ = text_surface(text,size,**kw)
    ctx.save(); ctx.translate(cx,cy); ctx.rotate(rot); ctx.scale(scale,scale)
    ctx.set_source_surface(surf,-w/2,-h/2); ctx.paint_with_alpha(alpha); ctx.restore()
    return w*scale, h*scale

# ---------- characters ----------
CHARS = {
 "golu": dict(skin="#C68B59", top="#F2C14E", top2="#E0A92E", hair="curly", glasses=False, name="GOLU"),
 "raju": dict(skin="#A86E46", top="#2FA58A", top2="#23806B", hair="neat", glasses=True, name="RAJU"),
 "nikki": dict(skin="#D49A6A", top="#FF5D8F", top2="#E04374", hair="long", glasses=False, name="NIKKI"),
}
def draw_character(ctx, kind, x, y, s=1.0, mouth=0.0, expr="normal", t=0.0, look=(0,0), arm="down", prop=None, blink=False):
    c=CHARS[kind]; skin=hexc(c["skin"]); lw=7*s
    ctx.save(); ctx.translate(x,y); ctx.scale(s,s); lw=7
    # body
    ctx.move_to(-170,160); ctx.curve_to(-180,330,-200,520,-215,1100); ctx.line_to(215,1100)
    ctx.curve_to(200,520,180,330,170,160); ctx.curve_to(90,120,-90,120,-170,160); ctx.close_path()
    fill_stroke(ctx, hexc(c["top"]), lw)
    if kind=="golu":  # hoodie strings + pocket
        for dx in (-35,35):
            ctx.move_to(dx,150); ctx.line_to(dx*1.1,290); ctx.set_source_rgb(1,1,1); ctx.set_line_width(10); ctx.stroke()
            ellipse(ctx,dx*1.1,295,9,9); fill_stroke(ctx,(1,1,1),4)
        ctx.move_to(-110,470); ctx.line_to(110,470); ctx.set_source_rgb(*hexc(c["top2"])); ctx.set_line_width(8); ctx.stroke()
    else:  # jacket opening with white tee
        ctx.move_to(-60,140); ctx.line_to(-35,1100); ctx.line_to(35,1100); ctx.line_to(60,140); ctx.close_path()
        fill_stroke(ctx,(0.96,0.96,0.94),5)
    if c["hair"]=="long":  # hair behind shoulders
        ctx.move_to(-135,-40); ctx.curve_to(-175,120,-190,260,-150,360); ctx.line_to(150,360)
        ctx.curve_to(190,260,175,120,135,-40); ctx.close_path(); ctx.set_source_rgb(0.13,0.08,0.07); ctx.fill()
    # arms
    def arm_shape(side, mode):
        sx = side*175
        ctx.save()
        if mode=="up":  # waving
            ang = -2.4 + 0.35*math.sin(t*10)
        elif mode=="hold":  # holding something in front
            ang = -0.9
        elif mode=="type":
            ang = -0.6 + 0.08*math.sin(t*25+side)
        elif mode=="cheer":
            ang = -2.7 + 0.2*math.sin(t*12+side)
        elif mode=="point":
            ang = -1.9 + 0.06*math.sin(t*6)
        elif mode=="phone":
            ang = -2.75
        elif mode=="thumbs":
            ang = -2.35 + 0.1*math.sin(t*8)
        elif mode=="hip":
            ang = 0.55
        elif mode=="head":
            ang = 2.93 + 0.04*math.sin(t*20)
        elif mode=="shrug":
            ang = -0.95 + 0.05*math.sin(t*6)
        elif mode=="pad":
            ang = 0.35 + 0.03*math.sin(t*18+side)
        else:
            ang = 0.15*side*-1
        ctx.translate(sx,200); ctx.rotate(ang*side if mode!="down" else ang)
        rrect(ctx,-45,0,90,300,40); fill_stroke(ctx, hexc(c["top"]), lw)
        if mode!="head":
            ellipse(ctx,0,320,44,44); fill_stroke(ctx, skin, lw)
        if mode=="thumbs":
            rrect(ctx,-12,330,24,60,12); fill_stroke(ctx, skin, 5)
        if mode=="phone":
            rrect(ctx,-38,300,76,130,14); fill_stroke(ctx, hexc("#1D1D24"), 5)
            rrect(ctx,-28,312,56,106,8); ctx.set_source_rgb(*hexc("#7FD3FF")); ctx.fill()
        ctx.restore()
    arms = arm if isinstance(arm,tuple) else (arm,arm)
    arm_shape(-1, arms[0]); arm_shape(1, arms[1])
    # neck + head
    rrect(ctx,-40,90,80,80,20); fill_stroke(ctx, skin, lw)
    ellipse(ctx,-118,10,26,34); fill_stroke(ctx, skin, lw); ellipse(ctx,118,10,26,34); fill_stroke(ctx, skin, lw)
    ellipse(ctx,0,0,118,132); fill_stroke(ctx, skin, lw)
    # hair
    hair=(0.11,0.09,0.09)
    if c["hair"]=="curly":
        for (hx,hy,r) in [(-95,-70,42),(-55,-110,46),(0,-125,48),(55,-110,46),(95,-70,42),(-30,-90,40),(30,-92,40),(-110,-25,28),(110,-25,28)]:
            ellipse(ctx,hx,hy,r,r); ctx.set_source_rgb(*hair); ctx.fill()
        for (hx,hy,r) in [(-55,-122,14),(20,-140,12),(80,-100,10)]:
            ellipse(ctx,hx,hy,r,r*0.6); ctx.set_source_rgba(1,1,1,0.18); ctx.fill()
    elif c["hair"]=="long":
        ellipse(ctx,0,-150,44,34); ctx.set_source_rgb(0.13,0.08,0.07); ctx.fill()  # bun
        ctx.move_to(-128,30); ctx.curve_to(-140,-110,-50,-160,10,-150); ctx.curve_to(90,-150,140,-100,128,30)
        ctx.curve_to(110,-40,60,-80,20,-95); ctx.curve_to(-20,-60,-80,-50,-128,30); ctx.close_path()
        ctx.set_source_rgb(0.13,0.08,0.07); ctx.fill()
        rrect(ctx,-36,-136,72,16,8); ctx.set_source_rgb(*hexc("#FFD23F")); ctx.fill()  # hair band
        for side in (-1,1):
            ellipse(ctx,side*122,48,10,10); ctx.set_source_rgb(*hexc("#FFD23F")); ctx.fill_preserve(); ctx.set_source_rgb(*INK); ctx.set_line_width(3); ctx.stroke()
    else:
        ctx.move_to(-122,-10); ctx.curve_to(-130,-120,-40,-160,30,-148); ctx.curve_to(110,-140,135,-70,122,-10)
        ctx.curve_to(100,-60,40,-95,-20,-80); ctx.curve_to(-70,-70,-100,-40,-122,-10); ctx.close_path()
        ctx.set_source_rgb(*hair); ctx.fill()
    # eyes
    ex = 44; ey = -10
    big = expr in ("shock",); er = 40 if big else 31
    for side in (-1,1):
        cx = side*ex
        if expr=="happy":
            ctx.arc(cx,ey+8,22,math.pi*1.1,math.pi*1.9); ctx.set_source_rgb(*INK); ctx.set_line_width(8); ctx.stroke()
            continue
        if expr=="excited":
            star(ctx,cx,ey,34+3*math.sin(t*12)); ctx.set_source_rgb(*hexc("#FFC21A")); ctx.fill_preserve(); ctx.set_source_rgb(*INK); ctx.set_line_width(4); ctx.stroke()
            continue
        if expr=="confused":
            rr = er*(1.25 if side==1 else 0.75)
            ellipse(ctx,cx,ey,rr,rr*1.1); fill_stroke(ctx,(1,1,1),6)
            ellipse(ctx,cx+math.sin(t*4+side)*8,ey+math.cos(t*4)*6,11 if side==1 else 8,11 if side==1 else 8); ctx.set_source_rgb(*INK); ctx.fill()
            continue
        if expr=="smirk":
            ellipse(ctx,cx,ey,er,er*1.1); fill_stroke(ctx,(1,1,1),6)
            ellipse(ctx,cx+look[0]*10,ey+6,13,13); ctx.set_source_rgb(*INK); ctx.fill()
            ctx.save(); ellipse(ctx,cx,ey,er,er*1.1); ctx.clip(); ctx.rectangle(cx-er,ey-er*1.2,2*er,er*0.85); ctx.set_source_rgb(*skin); ctx.fill(); ctx.restore()
            ctx.move_to(cx-er,ey-er*0.35); ctx.line_to(cx+er,ey-er*0.35); ctx.set_source_rgb(*INK); ctx.set_line_width(6); ctx.stroke()
            continue
        if expr in ("cry","laugh"):
            if expr=="cry":
                ctx.arc(cx,ey-4,22,math.pi*0.1,math.pi*0.9); ctx.set_source_rgb(*INK); ctx.set_line_width(8); ctx.stroke()
                for k in range(2):
                    ty=ey+18+((t*260+k*90)%150)
                    ellipse(ctx,cx+side*8,ty,9,14); ctx.set_source_rgba(0.45,0.8,1,0.9); ctx.fill()
                ctx.rectangle(cx-10+side*4,ey+14,20,6); ctx.set_source_rgba(0.45,0.8,1,0.8); ctx.fill()
            else:
                ctx.arc(cx,ey+8,22,math.pi*1.1,math.pi*1.9); ctx.set_source_rgb(*INK); ctx.set_line_width(8); ctx.stroke()
                ellipse(ctx,cx+side*30,ey+22,7,10); ctx.set_source_rgba(0.45,0.8,1,0.85); ctx.fill()
            continue
        if expr=="love":
            ctx.save(); ctx.translate(cx,ey); sc=1.3+0.15*math.sin(t*10); ctx.scale(sc,sc)
            ctx.move_to(0,22); ctx.curve_to(-46,-6,-24,-44,0,-18); ctx.curve_to(24,-44,46,-6,0,22); ctx.close_path()
            ctx.set_source_rgb(*hexc("#FF3B6B")); ctx.fill_preserve(); ctx.set_source_rgb(*INK); ctx.set_line_width(4); ctx.stroke(); ctx.restore()
            continue
        if expr=="doubt" and side==-1:
            ellipse(ctx,cx,ey+6,er,er*0.45); fill_stroke(ctx,(1,1,1),6)
            ellipse(ctx,cx+look[0]*10,ey+6,12,10); ctx.set_source_rgb(*INK); ctx.fill()
            continue
        hscale = 0.12 if blink else 1.0
        ellipse(ctx,cx,ey,er,er*1.1*hscale); fill_stroke(ctx,(1,1,1),6)
        if blink: continue
        if expr=="star":
            star(ctx,cx+look[0]*6,ey+look[1]*6,24); ctx.set_source_rgb(*hexc("#FFC21A")); ctx.fill_preserve()
            ctx.set_source_rgb(*INK); ctx.set_line_width(3); ctx.stroke()
        else:
            pr = 9 if big else 14
            ellipse(ctx,cx+look[0]*10,ey+look[1]*10,pr,pr); ctx.set_source_rgb(*INK); ctx.fill()
            ellipse(ctx,cx+look[0]*10-4,ey+look[1]*10-5,4,4); ctx.set_source_rgb(1,1,1); ctx.fill()
    if kind=="nikki" and expr not in ("happy","love","laugh","cry"):
        for side in (-1,1):
            for k in range(3):
                a=-1.9+k*0.35 if side==-1 else -1.25-k*0.35
                ctx.move_to(side*ex+32*math.cos(a),ey+35*math.sin(a)); ctx.line_to(side*ex+46*math.cos(a),ey+48*math.sin(a))
                ctx.set_source_rgb(*INK); ctx.set_line_width(5); ctx.stroke()
    if c["glasses"]:
        for side in (-1,1):
            ellipse(ctx,side*ex,ey,44,44); ctx.set_source_rgb(*INK); ctx.set_line_width(6); ctx.stroke()
        ctx.move_to(-ex+44,ey); ctx.line_to(ex-44,ey); ctx.stroke()
    # brows
    ctx.set_source_rgb(*INK); ctx.set_line_width(9); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    by = ey-55 - (14 if expr in ("shock","star") else 0)
    for side in (-1,1):
        tilt = {"angry":12,"sad":-10}.get(expr,0)*side
        lift = -22 if (expr in ("doubt","smirk") and side==1) else (8 if (expr in ("doubt","smirk") and side==-1) else 0)
        if expr=="confused": lift = -26 if side==1 else 10
        if expr=="excited": lift = -18
        ctx.move_to(side*ex-25,by+tilt*-0.5+lift); ctx.line_to(side*ex+25,by-6+tilt*0.5+lift); ctx.stroke()
    # nose
    ctx.move_to(-4,22); ctx.curve_to(12,40,10,52,-6,56); ctx.set_line_width(6); ctx.stroke()
    # cheeks
    for side in (-1,1):
        ellipse(ctx,side*75,55,20,12); ctx.set_source_rgba(1,0.45,0.45,0.35); ctx.fill()
    # mouth
    my=82
    if mouth>0.08 or expr in ("shock","laugh","cry","excited"):
        base={"shock":0.7,"laugh":0.55+0.35*abs(math.sin(t*14)),"cry":0.6+0.2*abs(math.sin(t*9)),"excited":0.75}.get(expr,0)
        o = max(mouth, base)
        mw = 26 if expr=="shock" else (54 if expr in ("laugh","cry","excited") else 42); mh = 10+34*o
        ellipse(ctx,0,my,mw,mh); fill_stroke(ctx,hexc("#5A1622"),6)
        ellipse(ctx,0,my+mh*0.45,mw*0.6,mh*0.35); ctx.set_source_rgb(*hexc("#E2697A")); ctx.fill()
        if expr not in ("shock","cry"):
            ctx.rectangle(-mw*0.7,my-mh+2,mw*1.4,mh*0.28); ctx.set_source_rgb(1,1,1); ctx.fill()
    elif expr=="smirk":
        ctx.move_to(-34,my-4); ctx.curve_to(-10,my+10,20,my+6,40,my-22); ctx.set_source_rgb(*INK); ctx.set_line_width(8); ctx.stroke()
    elif expr=="confused":
        ctx.move_to(-34,my); 
        for k in range(1,7): ctx.line_to(-34+k*11.5,my+(8 if k%2 else -8))
        ctx.set_source_rgb(*INK); ctx.set_line_width(7); ctx.stroke()
    elif expr=="doubt":
        ctx.move_to(-30,my+4); ctx.curve_to(-5,my-4,15,my+2,32,my-10); ctx.set_source_rgb(*INK); ctx.set_line_width(8); ctx.stroke()
    else:
        ctx.arc(0,my-22,40,math.pi*0.2,math.pi*0.8); ctx.set_source_rgb(*INK); ctx.set_line_width(8); ctx.stroke()
    for side,mode in ((-1,arms[0]),(1,arms[1])):
        if mode=="head":
            a_=(2.93 + 0.04*math.sin(t*20))*side
            hx=side*175 - 320*math.sin(a_); hy=200 + 320*math.cos(a_)
            ellipse(ctx,hx,hy,46,46); fill_stroke(ctx, skin, lw)
            for k in range(3):
                ctx.move_to(hx-20+k*18,hy-10); ctx.line_to(hx-20+k*18,hy+18); ctx.set_source_rgb(*INK); ctx.set_line_width(4); ctx.stroke()
    # sweat drop for shock
    if expr=="shock":
        ctx.move_to(120,-80); ctx.curve_to(105,-40,110,-20,128,-18); ctx.curve_to(146,-20,148,-45,120,-80)
        ctx.set_source_rgb(*hexc("#7FD3FF")); ctx.fill_preserve(); ctx.set_source_rgb(*INK); ctx.set_line_width(4); ctx.stroke()
    ctx.restore()

# ---------- props ----------
def draw_phone(ctx, x, y, w, h, s=1.0):
    ctx.save(); ctx.translate(x,y); ctx.scale(s,s)
    rrect(ctx,-w/2,-h/2,w,h,56); fill_stroke(ctx,hexc("#1D1D24"),10)
    rrect(ctx,-w/2+22,-h/2+22,w-44,h-44,38); ctx.set_source_rgb(*hexc("#FFFFFF")); ctx.fill()
    rrect(ctx,-60,-h/2+30,120,26,13); ctx.set_source_rgb(*hexc("#1D1D24")); ctx.fill()
    ctx.restore()

def draw_monitor(ctx, x, y, w, h, t, content=None):
    rrect(ctx,x-30,y+h-10,60,90,10); fill_stroke(ctx,hexc("#2B2B33"),6)
    rrect(ctx,x-110,y+h+70,220,30,12); fill_stroke(ctx,hexc("#2B2B33"),6)
    rrect(ctx,x-w/2,y,w,h,22); fill_stroke(ctx,hexc("#15151B"),8)
    # RGB edge glow
    hue=(t*0.4)%1
    import colorsys
    r,g,b = colorsys.hsv_to_rgb(hue,0.8,1)
    rrect(ctx,x-w/2-6,y-6,w+12,h+12,26); ctx.set_source_rgba(r,g,b,0.55); ctx.set_line_width(5); ctx.stroke()
    ctx.save(); rrect(ctx,x-w/2+18,y+18,w-36,h-36,12); ctx.clip()
    if content: content(ctx, x-w/2+18, y+18, w-36, h-36)
    ctx.restore()

def burst_bg(ctx, t, c1="#FFC93C", c2="#FF9F1C", cx=W/2, cy=H*0.42, n=18, speed=0.15):
    ctx.set_source_rgb(*hexc(c2)); ctx.paint()
    ctx.save(); ctx.translate(cx,cy); ctx.rotate(t*speed)
    for i in range(n):
        a0=2*math.pi*i/n; a1=a0+math.pi/n
        ctx.move_to(0,0); ctx.line_to(3000*math.cos(a0),3000*math.sin(a0)); ctx.line_to(3000*math.cos(a1),3000*math.sin(a1)); ctx.close_path()
        ctx.set_source_rgb(*hexc(c1)); ctx.fill()
    ctx.restore()
    g=cairo.RadialGradient(cx,cy,100,cx,cy,1400); g.add_color_stop_rgba(0,1,1,1,0.0); g.add_color_stop_rgba(1,0,0,0,0.35)
    ctx.set_source(g); ctx.paint()

def confetti(ctx, t, t0, seed=7, n=90, dur=4.0):
    if t<t0 or t>t0+dur: return
    rng=np.random.default_rng(seed); u=t-t0
    cols=["#FF4D6D","#FFD23F","#3BCEAC","#5E60CE","#FF9F1C","#FFFFFF"]
    for i in range(n):
        x0=rng.uniform(0,W); vy=rng.uniform(300,700); vx=rng.uniform(-80,80); rot=rng.uniform(0,6); sp=rng.uniform(-8,8)
        x=x0+vx*u+30*math.sin(u*3+i); y=-60+vy*u+rng.uniform(-400,0)
        if y<-50 or y>H+50: continue
        ctx.save(); ctx.translate(x,y); ctx.rotate(rot+sp*u); ctx.rectangle(-9,-5,18,10)
        ctx.set_source_rgb(*hexc(cols[i%len(cols)])); ctx.fill(); ctx.restore()

def draw_wallet(ctx, x, y, s, open_amt=0.0, happy=False, t=0):
    ctx.save(); ctx.translate(x,y); ctx.scale(s,s)
    rrect(ctx,-90,-60,180,120,22); fill_stroke(ctx,hexc("#8B5A2B"),7)
    rrect(ctx,30,-25,70,50,14); fill_stroke(ctx,hexc("#6E4520"),6)
    ellipse(ctx,62,0,9,9); fill_stroke(ctx,hexc("#E9C46A"),4)
    if happy:
        for sx in (-35,15):
            ctx.arc(sx,-10,12,math.pi*1.1,math.pi*1.9); ctx.set_source_rgb(*INK); ctx.set_line_width(6); ctx.stroke()
        ctx.arc(-10,15,22,0.2,math.pi-0.2); ctx.stroke()
    ctx.restore()

def draw_moth(ctx, x, y, t):
    ctx.save(); ctx.translate(x,y)
    flap=abs(math.sin(t*18))
    for side in (-1,1):
        ctx.save(); ctx.scale(side,1); ctx.move_to(0,0); ctx.curve_to(30,-50*flap-10,70,-30*flap,50,10); ctx.close_path()
        ctx.set_source_rgb(*hexc("#CFC6B8")); ctx.fill_preserve(); ctx.set_source_rgb(*INK); ctx.set_line_width(3); ctx.stroke(); ctx.restore()
    ellipse(ctx,0,0,10,22); fill_stroke(ctx,hexc("#8A7F70"),3)
    ctx.restore()

def coin(ctx, x, y, r, t):
    sx = abs(math.cos(t*6)) * 0.85 + 0.15
    ctx.save(); ctx.translate(x,y); ctx.scale(sx,1)
    ellipse(ctx,0,0,r,r); fill_stroke(ctx,hexc("#FFD23F"),5)
    ctx.restore()
    if sx>0.5: paint_text(ctx,"₹",x,y+2,int(r*1.1),fill=(201,140,0),stroke=(201,140,0),sw=0,font="Baloo2.ttf",pad=4)


def gamepad(ctx, x, y, s=1.0, rot=0.0, col="#2B2B36"):
    ctx.save(); ctx.translate(x,y); ctx.rotate(rot); ctx.scale(s,s)
    ctx.move_to(-120,-40); ctx.curve_to(-60,-60,60,-60,120,-40); ctx.curve_to(175,-30,190,60,165,85)
    ctx.curve_to(140,110,105,80,80,45); ctx.line_to(-80,45); ctx.curve_to(-105,80,-140,110,-165,85)
    ctx.curve_to(-190,60,-175,-30,-120,-40); ctx.close_path(); fill_stroke(ctx,hexc(col),7)
    for dx,dy,w_,h_ in [(-95,0,14,44),(-95,0,44,14)]:
        ctx.rectangle(-95-w_/2,-h_/2,w_,h_); ctx.set_source_rgb(0.85,0.85,0.9); ctx.fill()
    for (bx,by,bc) in [(95,-22,"#FF4D6D"),(122,0,"#3BCEAC"),(95,22,"#4CC9F0"),(68,0,"#FFD23F")]:
        ellipse(ctx,bx,by,11,11); ctx.set_source_rgb(*hexc(bc)); ctx.fill()
    for sx in (-38,38):
        ellipse(ctx,sx,30,16,16); fill_stroke(ctx,hexc("#15151B"),4)
    ctx.restore()

def skull(ctx, x, y, r=40):
    ctx.save(); ctx.translate(x,y)
    ellipse(ctx,0,-6,r,r*0.95); fill_stroke(ctx,(0.97,0.97,0.95),5)
    rrect(ctx,-r*0.55,r*0.55,r*1.1,r*0.55,8); fill_stroke(ctx,(0.97,0.97,0.95),5)
    for sx in (-1,1): ellipse(ctx,sx*r*0.38,-2,r*0.24,r*0.28); ctx.set_source_rgb(*INK); ctx.fill()
    ctx.move_to(0,r*0.22); ctx.line_to(-r*0.1,r*0.42); ctx.line_to(r*0.1,r*0.42); ctx.close_path(); ctx.fill()
    for k in (-1,0,1): ctx.move_to(k*r*0.25,r*0.6); ctx.line_to(k*r*0.25,r*1.05); ctx.set_line_width(4); ctx.stroke()
    ctx.restore()

GAME_TILE_COLS=[("#F72585","#7209B7"),("#4CC9F0","#3A0CA3"),("#FFD23F","#FF6B35"),("#3BCEAC","#0B6E4F"),("#FF4D6D","#590D22"),("#B8F2E6","#5E60CE"),("#F4A261","#9D0208"),("#90BE6D","#277DA1")]
def game_tile(ctx, x, y, w, h, seed, glow=0.0):
    """Generic, original 'game cover' tile (abstract art only)."""
    c1,c2=GAME_TILE_COLS[seed%len(GAME_TILE_COLS)]
    rrect(ctx,x,y,w,h,min(w,h)*0.12)
    g=cairo.LinearGradient(x,y,x,y+h); g.add_color_stop_rgb(0,*hexc(c1)); g.add_color_stop_rgb(1,*hexc(c2)); ctx.set_source(g); ctx.fill_preserve()
    ctx.set_source_rgb(*INK); ctx.set_line_width(max(2,w*0.03)); ctx.stroke()
    cx,cy,r=x+w/2,y+h*0.45,min(w,h)*0.26; kind=seed%5
    ctx.set_source_rgba(1,1,1,0.92)
    if kind==0: star(ctx,cx,cy,r); ctx.fill()
    elif kind==1: ellipse(ctx,cx,cy,r,r); ctx.fill(); ellipse(ctx,cx,cy,r*1.6,r*0.35); ctx.set_line_width(max(2,w*0.025)); ctx.stroke()
    elif kind==2:
        ctx.move_to(cx-r,cy+r); ctx.line_to(cx,cy-r); ctx.line_to(cx+r,cy+r); ctx.close_path(); ctx.fill()
    elif kind==3:
        ctx.move_to(cx-r*0.2,cy+r); ctx.line_to(cx-r*0.2,cy-r*0.6); ctx.line_to(cx,cy-r); ctx.line_to(cx+r*0.2,cy-r*0.6); ctx.line_to(cx+r*0.2,cy+r); ctx.close_path(); ctx.fill()
        ctx.rectangle(cx-r*0.6,cy+r*0.4,r*1.2,r*0.18); ctx.fill()
    else:
        rrect(ctx,cx-r,cy-r*0.4,r*2,r*0.8,r*0.3); ctx.fill(); ellipse(ctx,cx-r*0.55,cy+r*0.45,r*0.28,r*0.28); ctx.fill(); ellipse(ctx,cx+r*0.55,cy+r*0.45,r*0.28,r*0.28); ctx.fill()
    rrect(ctx,x+w*0.15,y+h*0.78,w*0.7,h*0.08,h*0.04); ctx.set_source_rgba(1,1,1,0.75); ctx.fill()
    if glow>0:
        rrect(ctx,x-6,y-6,w+12,h+12,min(w,h)*0.14); ctx.set_source_rgba(1,0.85,0.2,glow); ctx.set_line_width(8); ctx.stroke()

def beret(ctx, x, y, s=1.0, rot=-0.25):
    ctx.save(); ctx.translate(x,y); ctx.rotate(rot); ctx.scale(s,s)
    ellipse(ctx,0,0,150,55); fill_stroke(ctx,hexc("#C1121F"),7)
    ellipse(ctx,0,-48,14,14); fill_stroke(ctx,hexc("#C1121F"),5)
    ctx.restore()
def palette(ctx, x, y, s=1.0, t=0):
    ctx.save(); ctx.translate(x,y); ctx.scale(s,s); ctx.rotate(0.15*math.sin(t*3))
    ctx.move_to(-110,0); ctx.curve_to(-110,-90,90,-100,110,-20); ctx.curve_to(120,40,40,30,40,60); ctx.curve_to(40,100,-110,90,-110,0); ctx.close_path()
    fill_stroke(ctx,hexc("#E9C46A"),7)
    ellipse(ctx,10,40,16,14); ctx.set_source_rgb(*hexc("#2A1B54")); ctx.fill()
    for (px,py,c) in [(-60,-30,"#E63946"),(-15,-55,"#3A86FF"),(35,-50,"#FFD23F"),(-70,25,"#2EC45A"),(75,-25,"#F72585")]:
        ellipse(ctx,px,py,17,15); ctx.set_source_rgb(*hexc(c)); ctx.fill()
    ctx.restore()
def clock(ctx, x, y, r, t, speed=6):
    ellipse(ctx,x,y,r,r); fill_stroke(ctx,(1,1,1),8)
    for i in range(12):
        a=i*math.pi/6; ctx.move_to(x+r*0.82*math.cos(a),y+r*0.82*math.sin(a)); ctx.line_to(x+r*0.92*math.cos(a),y+r*0.92*math.sin(a))
        ctx.set_source_rgb(*INK); ctx.set_line_width(5); ctx.stroke()
    for L_,sp,lw_ in [(0.5,speed/12,10),(0.75,speed,6)]:
        a=t*sp-math.pi/2; ctx.move_to(x,y); ctx.line_to(x+r*L_*math.cos(a),y+r*L_*math.sin(a)); ctx.set_line_width(lw_); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
def moon(ctx, x, y, r):
    ctx.save(); ellipse(ctx,x,y,r,r); ctx.clip()
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD); ellipse(ctx,x,y,r,r); ellipse(ctx,x+r*0.45,y-r*0.2,r*0.85,r*0.85)
    ctx.set_source_rgb(*hexc("#FFE45E")); ctx.fill(); ctx.restore()

def diya(ctx, x, y, s=1.0, t=0.0, seed=0):
    ctx.save(); ctx.translate(x,y); ctx.scale(s,s)
    fl=1+0.12*math.sin(t*17+seed*2.1)+0.06*math.sin(t*29+seed)
    g=cairo.RadialGradient(0,-55,0,0,-55,120*fl); g.add_color_stop_rgba(0,1,0.85,0.3,0.55); g.add_color_stop_rgba(1,1,0.6,0.1,0)
    ctx.set_source(g); ctx.arc(0,-55,120*fl,0,2*math.pi); ctx.fill()
    ctx.move_to(-70,-8); ctx.curve_to(-60,45,60,45,70,-8); ctx.curve_to(40,6,-40,6,-70,-8); ctx.close_path(); fill_stroke(ctx,hexc("#C8553D"),6)
    ctx.move_to(-62,-4); ctx.curve_to(-30,10,30,10,62,-4); ctx.set_source_rgb(*hexc("#F2CC8F")); ctx.set_line_width(5); ctx.stroke()
    for k in (-30,0,30): ellipse(ctx,k,18,6,6); ctx.set_source_rgb(*hexc("#F2CC8F")); ctx.fill()
    ctx.save(); ctx.translate(0,-14); ctx.scale(1,fl)
    ctx.move_to(0,-58); ctx.curve_to(22,-30,18,-6,0,0); ctx.curve_to(-18,-6,-22,-30,0,-58); ctx.close_path()
    fg=cairo.LinearGradient(0,-58,0,0); fg.add_color_stop_rgb(0,*hexc("#FFF3B0")); fg.add_color_stop_rgb(1,*hexc("#FF8C1A")); ctx.set_source(fg); ctx.fill()
    ctx.restore(); ctx.restore()

def firework(ctx, x, y, t, t0, col=(1,0.8,0.2), n=26, R=230, dur=1.4):
    u=t-t0
    if u<0 or u>dur: return
    p=ease_out(u/dur); a_=max(0,1-u/dur)
    for i in range(n):
        a=i*2*math.pi/n; rr=R*p
        x1=x+rr*math.cos(a); y1=y+rr*math.sin(a)+60*p*p
        x0=x+rr*0.75*math.cos(a); y0=y+rr*0.75*math.sin(a)+45*p*p
        ctx.move_to(x0,y0); ctx.line_to(x1,y1); ctx.set_source_rgba(*col,a_); ctx.set_line_width(6); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
        ellipse(ctx,x1,y1,5,5); ctx.set_source_rgba(1,1,1,a_); ctx.fill()

def lantern(ctx, x, y, s, t, col="#FF4D6D"):
    ctx.save(); ctx.translate(x,y); ctx.rotate(0.06*math.sin(t*2+x)); ctx.scale(s,s)
    ctx.move_to(0,-200); ctx.line_to(0,-70); ctx.set_source_rgb(*INK); ctx.set_line_width(4); ctx.stroke()
    ctx.move_to(0,-70); ctx.line_to(70,0); ctx.line_to(0,70); ctx.line_to(-70,0); ctx.close_path(); fill_stroke(ctx,hexc(col),6)
    ctx.move_to(0,-70); ctx.line_to(0,70); ctx.move_to(-70,0); ctx.line_to(70,0); ctx.set_source_rgba(1,1,1,0.6); ctx.set_line_width(3); ctx.stroke()
    for k in range(-2,3): ctx.move_to(k*12,70); ctx.line_to(k*14,130); ctx.set_source_rgb(*hexc("#FFD23F")); ctx.set_line_width(4); ctx.stroke()
    g=cairo.RadialGradient(0,0,0,0,0,140); g.add_color_stop_rgba(0,1,0.8,0.3,0.25); g.add_color_stop_rgba(1,1,0.6,0.2,0); ctx.set_source(g); ctx.arc(0,0,140,0,2*math.pi); ctx.fill()
    ctx.restore()

def coupon_ticket(ctx, cx, cy, w, h, k, t):
    if k<=0.02: return
    ctx.save(); ctx.translate(cx,cy); ctx.rotate(-0.05+0.02*math.sin(t*3)); ctx.scale(k,k)
    r=34
    ctx.move_to(-w/2+r,-h/2); ctx.line_to(w/2-r,-h/2); ctx.arc(w/2-r,-h/2+r,r,-math.pi/2,0)
    ctx.line_to(w/2,-20); ctx.arc_negative(w/2,0,20,-math.pi/2,math.pi/2); ctx.line_to(w/2,h/2-r); ctx.arc(w/2-r,h/2-r,r,0,math.pi/2)
    ctx.line_to(-w/2+r,h/2); ctx.arc(-w/2+r,h/2-r,r,math.pi/2,math.pi); ctx.line_to(-w/2,20); ctx.arc_negative(-w/2,0,20,math.pi/2,-math.pi/2)
    ctx.line_to(-w/2,-h/2+r); ctx.arc(-w/2+r,-h/2+r,r,math.pi,1.5*math.pi); ctx.close_path()
    g=cairo.LinearGradient(0,-h/2,0,h/2); g.add_color_stop_rgb(0,*hexc("#FFD23F")); g.add_color_stop_rgb(1,*hexc("#FF9F1C")); ctx.set_source(g); ctx.fill_preserve()
    ctx.set_source_rgb(*INK); ctx.set_line_width(8); ctx.stroke()
    ctx.set_dash([14,12]); ctx.move_to(w*0.18,-h/2+16); ctx.line_to(w*0.18,h/2-16); ctx.set_line_width(5); ctx.stroke(); ctx.set_dash([])
    ctx.restore()

def money_note(ctx, x, y, s=1.0, rot=0.0, t=0.0, amount="₹500"):
    """Simplified cartoon banknote (not a currency replica)."""
    ctx.save(); ctx.translate(x,y); ctx.rotate(rot+0.05*math.sin(t*5)); ctx.scale(s,s)
    rrect(ctx,-150,-70,300,140,14)
    g=cairo.LinearGradient(-150,0,150,0); g.add_color_stop_rgb(0,*hexc("#A8A48C")); g.add_color_stop_rgb(1,*hexc("#8C8A70")); ctx.set_source(g); ctx.fill_preserve()
    ctx.set_source_rgb(*INK); ctx.set_line_width(6); ctx.stroke()
    rrect(ctx,-130,-52,260,104,10); ctx.set_source_rgba(1,1,1,0.25); ctx.set_line_width(3); ctx.stroke()
    ellipse(ctx,-70,0,38,38); ctx.set_source_rgba(1,1,1,0.25); ctx.fill()
    ctx.restore()
    paint_text(ctx,amount,x+40*s*math.cos(rot),y+40*s*math.sin(rot),int(62*s),fill=(40,45,30),stroke=(220,220,200),sw=max(1,int(3*s)),font="Baloo2.ttf",pad=4,rot=rot+0.05*math.sin(t*5))

def genre_icon(ctx, kind, x, y, s=1.0, t=0.0):
    ctx.save(); ctx.translate(x,y); ctx.scale(s,s)
    if kind=="action":
        star(ctx,0,0,90,n=10,inner=0.55,rot=t*0.5); ctx.set_source_rgb(*hexc("#FF4D6D")); ctx.fill_preserve(); ctx.set_source_rgb(*INK); ctx.set_line_width(6); ctx.stroke()
        star(ctx,0,0,50,n=8,inner=0.5,rot=-t); ctx.set_source_rgb(*hexc("#FFD23F")); ctx.fill()
    elif kind=="adventure":
        ctx.move_to(-95,60); ctx.line_to(-25,-55); ctx.line_to(15,5); ctx.line_to(45,-30); ctx.line_to(100,60); ctx.close_path(); fill_stroke(ctx,hexc("#3BCEAC"),6)
        ctx.move_to(-25,-55); ctx.line_to(-8,-28); ctx.line_to(-42,-28); ctx.close_path(); ctx.set_source_rgb(1,1,1); ctx.fill()
        ctx.move_to(45,-30); ctx.line_to(45,-90); ctx.set_source_rgb(*INK); ctx.set_line_width(5); ctx.stroke()
        ctx.move_to(45,-90); ctx.line_to(85,-77); ctx.line_to(45,-64); ctx.close_path(); ctx.set_source_rgb(*hexc("#FFD23F")); ctx.fill()
    elif kind=="racing":
        rrect(ctx,-95,-10,190,55,20); fill_stroke(ctx,hexc("#4CC9F0"),6)
        ctx.move_to(-55,-10); ctx.line_to(-30,-45); ctx.line_to(35,-45); ctx.line_to(60,-10); ctx.close_path(); fill_stroke(ctx,hexc("#4CC9F0"),6)
        for wx in (-50,50): ellipse(ctx,wx,48,24,24); fill_stroke(ctx,hexc("#1D1D24"),5)
        for i in range(4):
            for j in range(2):
                ctx.rectangle(60+i*12,-95+j*12,12,12); ctx.set_source_rgb(*((0,0,0) if (i+j)%2 else (1,1,1))); ctx.fill()
        ctx.move_to(60,-95); ctx.line_to(60,-40); ctx.set_source_rgb(*INK); ctx.set_line_width(4); ctx.stroke()
    else:  # story
        ctx.move_to(0,-55); ctx.curve_to(-40,-75,-80,-70,-100,-60); ctx.line_to(-100,60); ctx.curve_to(-80,50,-40,45,0,65); ctx.close_path(); fill_stroke(ctx,hexc("#FFF6D6"),6)
        ctx.move_to(0,-55); ctx.curve_to(40,-75,80,-70,100,-60); ctx.line_to(100,60); ctx.curve_to(80,50,40,45,0,65); ctx.close_path(); fill_stroke(ctx,hexc("#FFF6D6"),6)
        for k in range(4):
            ctx.move_to(-82,-38+k*22); ctx.line_to(-18,-38+k*22+4); ctx.move_to(18,-38+k*22+4); ctx.line_to(82,-38+k*22)
        ctx.set_source_rgba(0,0,0,0.35); ctx.set_line_width(4); ctx.stroke()
    ctx.restore()

def genre_card(ctx, kind, label, cx, cy, k, t, col):
    if k<=0.02: return
    ctx.save(); ctx.translate(cx,cy); ctx.scale(k,k)
    rrect(ctx,-150,-170,300,340,34)
    g=cairo.LinearGradient(0,-170,0,170); g.add_color_stop_rgb(0,*hexc(col[0])); g.add_color_stop_rgb(1,*hexc(col[1])); ctx.set_source(g); ctx.fill_preserve()
    ctx.set_source_rgb(*INK); ctx.set_line_width(8); ctx.stroke()
    genre_icon(ctx,kind,0,-30,1.0,t)
    ctx.restore()
    paint_text(ctx,label,cx,cy+120*k,int(46),scale=k,fill=(255,255,255),stroke=(20,10,30),font="LuckiestGuy.ttf",pad=6)

def icon_sysreq(ctx,x,y,s=1.0):
    ctx.save(); ctx.translate(x,y); ctx.scale(s,s)
    rrect(ctx,-70,-60,100,120,10); fill_stroke(ctx,hexc("#2B2B36"),5)
    for i in range(3): rrect(ctx,-58,-45+i*22,76,12,5); ctx.set_source_rgb(*hexc("#4CC9F0")); ctx.fill()
    ctx.arc(55,30,45,math.pi,2*math.pi); ctx.set_source_rgb(1,1,1); ctx.set_line_width(12); ctx.stroke()
    ctx.move_to(55,30); ctx.line_to(85,0); ctx.set_source_rgb(*hexc("#E63946")); ctx.set_line_width(7); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
    ctx.restore()
def icon_platform(ctx,x,y,s=1.0):
    ctx.save(); ctx.translate(x,y); ctx.scale(s,s)
    rrect(ctx,-95,-65,190,130,14); fill_stroke(ctx,hexc("#1B1F3B"),5)
    ctx.rectangle(-95,-65,190,28); ctx.set_source_rgb(*hexc("#5E60CE")); ctx.fill()
    for i,c in enumerate(["#FF4D6D","#FFD23F","#3BCEAC"]): ellipse(ctx,-75+i*18,-51,6,6); ctx.set_source_rgb(*hexc(c)); ctx.fill()
    for r in range(2):
        for c in range(3): rrect(ctx,-80+c*56,-28+r*44,46,36,6); ctx.set_source_rgb(*hexc(["#F72585","#4CC9F0","#FFD23F","#3BCEAC","#FF9F1C","#B8F2E6"][r*3+c])); ctx.fill()
    ctx.restore()
def icon_key(ctx,x,y,s=1.0):
    ctx.save(); ctx.translate(x,y); ctx.scale(s,s)
    ctx.arc(45,0,40,math.pi,2*math.pi); ctx.set_source_rgb(*hexc("#ADB5BD")); ctx.set_line_width(14); ctx.stroke()
    rrect(ctx,0,-5,90,80,12); fill_stroke(ctx,hexc("#FFD23F"),5); ellipse(ctx,45,30,10,10); ctx.set_source_rgb(*INK); ctx.fill()
    ellipse(ctx,-55,10,28,28); fill_stroke(ctx,hexc("#F4A261"),5); ellipse(ctx,-55,10,10,10); ctx.set_source_rgb(*hexc("#1B1F3B")); ctx.fill()
    ctx.move_to(-28,10); ctx.line_to(5,10); ctx.set_source_rgb(*hexc("#F4A261")); ctx.set_line_width(12); ctx.stroke()
    ctx.restore()
def check_card(ctx,num,title,icon,cx,cy,k,t,col,checked=True,w=860,h=200):
    if k<=0.02: return
    ctx.save(); ctx.translate(cx,cy); ctx.scale(k,k)
    for gw,ga in [(26,0.12),(10,0.4)]:
        rrect(ctx,-w/2,-h/2,w,h,34); ctx.set_source_rgba(*col,ga); ctx.set_line_width(gw); ctx.stroke()
    rrect(ctx,-w/2,-h/2,w,h,34); ctx.set_source_rgba(0.06,0.03,0.16,0.92); ctx.fill_preserve(); ctx.set_source_rgb(*col); ctx.set_line_width(6); ctx.stroke()
    ellipse(ctx,-w/2+75,0,52,52); ctx.set_source_rgb(*col); ctx.fill()
    icon(ctx,-w/2+195,0,0.72)
    if checked:
        ellipse(ctx,w/2-70,0,40,40); ctx.set_source_rgb(*hexc("#2EC45A")); ctx.fill()
        ctx.move_to(w/2-88,0); ctx.line_to(w/2-74,16); ctx.line_to(w/2-50,-14); ctx.set_source_rgb(1,1,1); ctx.set_line_width(9); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
    ctx.restore()
    paint_text(ctx,str(num),cx+(-w/2+75)*k,cy,64,scale=k,fill=(20,10,30),stroke=tuple(int(c*255) for c in col),sw=0,font="LuckiestGuy.ttf",pad=4)
    paint_text(ctx,title,cx+(110 if w>=860 else 100)*k,cy,56 if len(title)<18 else 48,scale=k,fill=(255,255,255),stroke=(20,5,40),font="LuckiestGuy.ttf",pad=6)
def shades(ctx,x,y,s=1.0):
    ctx.save(); ctx.translate(x,y); ctx.scale(s,s)
    for sx in (-1,1): rrect(ctx,sx*48-40,-30,80,48,14); ctx.set_source_rgb(0.08,0.08,0.1); ctx.fill()
    ctx.move_to(-10,-18); ctx.line_to(10,-18); ctx.set_source_rgb(0.08,0.08,0.1); ctx.set_line_width(8); ctx.stroke()
    for sx in (-1,1): ctx.move_to(sx*48-25,-20); ctx.line_to(sx*48-5,-20); ctx.set_source_rgba(1,1,1,0.6); ctx.set_line_width(5); ctx.stroke()
    ctx.restore()
def buy_screen(c,x,y,w,h,t,blocked=False):
    c.set_source_rgb(*hexc("#0F1220")); c.rectangle(x,y,w,h); c.fill()
    game_tile(c,x+w*0.06,y+h*0.1,w*0.36,h*0.7,3)
    for i in range(3): rrect(c,x+w*0.48,y+h*(0.14+i*0.1),w*(0.42-i*0.08),h*0.05,6); c.set_source_rgba(1,1,1,0.3); c.fill()
    rrect(c,x+w*0.48,y+h*0.58,w*0.44,h*0.18,12); c.set_source_rgb(*hexc("#2EC45A")); c.fill()
    paint_text(c,"BUY NOW",x+w*0.70,y+h*0.67,int(h*0.09),fill=(255,255,255),stroke=(46,196,90),sw=0,font="LuckiestGuy.ttf",pad=4)
    if blocked:
        c.move_to(x+w*0.47,y+h*0.56); c.line_to(x+w*0.93,y+h*0.78); c.move_to(x+w*0.47,y+h*0.78); c.line_to(x+w*0.93,y+h*0.56)
        c.set_source_rgb(*hexc("#E63946")); c.set_line_width(10); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
