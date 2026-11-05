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
        lift = -22 if (expr=="doubt" and side==1) else (8 if (expr=="doubt" and side==-1) else 0)
        ctx.move_to(side*ex-25,by+tilt*-0.5+lift); ctx.line_to(side*ex+25,by-6+tilt*0.5+lift); ctx.stroke()
    # nose
    ctx.move_to(-4,22); ctx.curve_to(12,40,10,52,-6,56); ctx.set_line_width(6); ctx.stroke()
    # cheeks
    for side in (-1,1):
        ellipse(ctx,side*75,55,20,12); ctx.set_source_rgba(1,0.45,0.45,0.35); ctx.fill()
    # mouth
    my=82
    if mouth>0.08 or expr in ("shock","laugh","cry"):
        base={"shock":0.7,"laugh":0.55+0.35*abs(math.sin(t*14)),"cry":0.6+0.2*abs(math.sin(t*9))}.get(expr,0)
        o = max(mouth, base)
        mw = 26 if expr=="shock" else (50 if expr in ("laugh","cry") else 42); mh = 10+34*o
        ellipse(ctx,0,my,mw,mh); fill_stroke(ctx,hexc("#5A1622"),6)
        ellipse(ctx,0,my+mh*0.45,mw*0.6,mh*0.35); ctx.set_source_rgb(*hexc("#E2697A")); ctx.fill()
        if expr not in ("shock","cry"):
            ctx.rectangle(-mw*0.7,my-mh+2,mw*1.4,mh*0.28); ctx.set_source_rgb(1,1,1); ctx.fill()
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
