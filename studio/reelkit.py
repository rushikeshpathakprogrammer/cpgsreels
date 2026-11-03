"""Shared reel pipeline: voice timeline, audio mix, lip-sync envelopes, captions, encoder."""
import math, subprocess, os, json
import numpy as np, cairo, soundfile as sf
from draw import *
import sfx
FPS = 30; SR = sfx.SR

def load_voice(path, trim_db=-42):
    a, sr = sf.read(path, dtype="float32")
    if a.ndim>1: a=a.mean(1)
    if sr != SR:
        x = np.linspace(0, len(a)/sr, int(len(a)*SR/sr), endpoint=False)
        a = np.interp(x, np.arange(len(a))/sr, a).astype(np.float32)
    thr = 10**(trim_db/20)*np.abs(a).max()
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx): a = a[max(0,idx[0]-int(0.03*SR)): idx[-1]+int(0.08*SR)]
    return a/(np.abs(a).max()+1e-6)*0.9

def build_timeline(aud_dir, lines, gaps, lead=0.5, default_gap=0.35):
    t = lead; tl = []
    for lid, spk, chunks in lines:
        a = load_voice(f"{aud_dir}/{lid}.wav"); d = len(a)/SR
        tl.append(dict(id=lid, spk=spk, chunks=chunks, start=t, end=t+d, audio=a))
        t += d + gaps.get(lid, default_gap)
    return tl

class Mixer:
    def __init__(self, timeline, end, speakers):
        self.tl=timeline; self.end=end; self.N=int(end*SR)+SR; self.NF=int(end*FPS)
        self.fx=np.zeros(self.N,np.float32); self.v=np.zeros(self.N,np.float32)
        self.env={k: np.zeros(self.NF+2) for k in speakers}
        hop=SR//FPS
        for ln in timeline:
            s=int(ln["start"]*SR); a=ln["audio"]; self.v[s:s+len(a)]+=a
            for i in range(0,len(a),hop):
                fi=int((ln["start"]+i/SR)*FPS)
                if fi<self.NF: self.env[ln["spk"]][fi]=float(np.sqrt(np.mean(a[i:i+hop]**2)))
        for k,e in self.env.items():
            m=np.percentile(e[e>0],90) if (e>0).any() else 1; self.env[k]=np.clip(e/m,0,1)
    def add(self, snd, at, gain=1.0):
        s=int(at*SR); e=min(self.N,s+len(snd))
        if e>s: self.fx[s:e]+=snd[:e-s]*gain
    def render(self, path, bpm=124, music_gain=0.5):
        N=self.N; music=sfx.chiptune(self.end+1, bpm=bpm)[:N]; music=np.pad(music,(0,max(0,N-len(music))))
        venv=np.convolve(np.abs(self.v),np.ones(SR//10)/(SR//10),mode="same")
        duck=np.where(venv>0.01,0.35,1.0).astype(np.float32); duck=np.convolve(duck,np.ones(SR//8)/(SR//8),mode="same")
        out=self.v*1.0+self.fx*0.55+music*music_gain*duck
        E=int(self.end*SR); f=int(SR*1.0); out[E-f:E]*=np.linspace(1,0,f); out=out[:E]
        out=out/max(1.0,np.abs(out).max()/0.95); sf.write(path,out,SR)
    def mouth(self, kind, t):
        fi=int(t*FPS); e=self.env.get(kind)
        if e is None or fi>=len(e): return 0.0
        return float(e[max(0,fi-1):fi+2].max())

def active_line(tl, t):
    for ln in tl:
        if ln["start"]<=t<ln["end"]: return ln
    return None

TAG = {"golu":(242,193,78), "raju":(47,165,138), "nikki":(255,93,143)}
def caption(ctx, tl, t, cy=1390, size=84):
    ln=active_line(tl,t)
    if not ln: return
    n=len(ln["chunks"]); dur=ln["end"]-ln["start"]
    lens=[len(c.replace("*",""))+4 for c in ln["chunks"]]; tot=sum(lens); acc=ln["start"]; idx=n-1; cst=acc
    for i,lx in enumerate(lens):
        seg=dur*lx/tot
        if t<acc+seg: idx=i; cst=acc; break
        acc+=seg
    else: cst=acc
    k=ease_out_back((t-cst)/0.18)
    parts=[]; hl=False
    for w_ in ln["chunks"][idx].split(" "):
        if w_.startswith("*"): hl=True
        parts.append((w_.replace("*",""),hl))
        if w_.endswith("*"): hl=False
    def style(h): return dict(fill=(30,25,28) if h else (255,255,255), stroke=(255,210,63) if h else (30,25,28),
                              sw=0 if h else 8, font="Baloo2.ttf", box=(255,210,63) if h else None, pad=14)
    items=[]; total=0
    for txt,h in parts:
        _,w,_,_=text_surface(txt,size,**style(h)); items.append((txt,h,w)); total+=w+6
    scale=min(1.0,(W-80)/total)*k; x=W/2-total*scale/2
    for txt,h,w in items:
        paint_text(ctx,txt,x+w*scale/2,cy,size,scale=scale,**style(h)); x+=(w+6)*scale
    col=TAG.get(ln["spk"],(255,255,255))
    paint_text(ctx,ln["spk"].upper(),W/2,cy-95,40,fill=(30,25,28),stroke=col,sw=0,font="LuckiestGuy.ttf",box=col,pad=12)

def bokeh_bg(ctx, t, c_top, c_bot, seed=1, n=26, tint=(1,1,1)):
    g=cairo.LinearGradient(0,0,0,H); g.add_color_stop_rgb(0,*hexc(c_top)); g.add_color_stop_rgb(1,*hexc(c_bot)); ctx.set_source(g); ctx.paint()
    rng=np.random.default_rng(seed)
    for i in range(n):
        x=rng.uniform(0,W); y=rng.uniform(0,H); r=rng.uniform(30,110); sp=rng.uniform(8,25)
        yy=(y - t*sp) % (H+200) - 100; xx=x+20*math.sin(t*0.5+i)
        rg=cairo.RadialGradient(xx,yy,0,xx,yy,r); rg.add_color_stop_rgba(0,*tint,0.16); rg.add_color_stop_rgba(1,*tint,0)
        ctx.set_source(rg); ctx.arc(xx,yy,r,0,2*math.pi); ctx.fill()

def vignette(ctx):
    g=cairo.RadialGradient(W/2,H*0.45,500,W/2,H*0.45,1300); g.add_color_stop_rgba(0,0,0,0,0); g.add_color_stop_rgba(1,0,0,0,0.45)
    ctx.set_source(g); ctx.paint()

def backlight(ctx, x, y, r=420, col=(1,1,1), a=0.25):
    g=cairo.RadialGradient(x,y,0,x,y,r); g.add_color_stop_rgba(0,*col,a); g.add_color_stop_rgba(1,*col,0)
    ctx.set_source(g); ctx.arc(x,y,r,0,2*math.pi); ctx.fill()

def flash(ctx, t, starts, dur=0.12):
    for s in starts:
        if s<=t<s+dur:
            ctx.set_source_rgba(1,1,1,0.55*(1-(t-s)/dur)); ctx.paint()

def encode(frame_fn, NF, wav, out):
    cmd=["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","bgra","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
         "-i",wav,"-c:v","libx264","-preset","medium","-crf","21","-maxrate","4500k","-bufsize","9000k",
         "-pix_fmt","yuv420p","-profile:v","high","-g","60","-c:a","aac","-b:a","128k","-ar","44100","-ac","2",
         "-af","loudnorm=I=-14:TP=-1.5:LRA=11","-movflags","+faststart","-shortest",out]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    for i in range(NF):
        p.stdin.write(frame_fn(i/FPS).get_data())
        if i%300==0: print("frame",i,"/",NF,flush=True)
    p.stdin.close(); p.wait()
