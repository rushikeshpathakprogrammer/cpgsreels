"""Synthesized, copyright-free sound effects and chiptune music (numpy only)."""
import numpy as np
SR = 44100

def _t(d): return np.arange(int(SR*d))/SR
def env(n, a=0.005, r=0.1):
    e = np.ones(n); A=int(SR*a); R=int(SR*r)
    if A: e[:A]=np.linspace(0,1,A)
    if R: e[-R:]*=np.linspace(1,0,R)
    return e

def pop(): t=_t(0.12); f=np.linspace(900,250,len(t)); return 0.6*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*30)
def ding():
    t=_t(1.2); s=sum(a*np.sin(2*np.pi*f*t) for f,a in [(1568,1),(2349,.5),(3136,.25)])
    return 0.35*s*np.exp(-t*4)
def chaching():
    a=ding()*0.8; b=np.zeros(int(SR*0.12)); out=np.concatenate([b,a])
    t=_t(0.25); n=np.random.default_rng(1).normal(0,1,len(t))*np.exp(-t*25)*0.3
    out[:len(n)]+=n; return out
def whoosh():
    t=_t(0.45); rng=np.random.default_rng(2); n=rng.normal(0,1,len(t))
    k=np.linspace(0.02,0.4,len(t)); y=np.zeros_like(n); acc=0
    for i in range(len(n)): acc+=k[i]*(n[i]-acc); y[i]=acc
    return 0.5*y*np.sin(np.pi*t/t[-1])
def error_buzz():
    t=_t(0.5); s=np.sign(np.sin(2*np.pi*110*t))*0.25+np.sign(np.sin(2*np.pi*116*t))*0.2
    return s*env(len(t),0.01,0.08)
def boing():
    t=_t(0.5); f=220+120*np.sin(2*np.pi*9*t)*np.exp(-t*5)
    return 0.45*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*5)
def sparkle():
    out=np.zeros(int(SR*0.8)); rng=np.random.default_rng(3)
    for i in range(7):
        st=int(SR*0.09*i); t=_t(0.25); f=rng.uniform(2000,4200)
        out[st:st+len(t)]+=0.12*np.sin(2*np.pi*f*t)*np.exp(-t*18)
    return out
def shock():  # comedic descending slide-whistle
    t=_t(0.7); f=np.linspace(1400,300,len(t)); return 0.3*np.sin(2*np.pi*np.cumsum(f)/SR)*env(len(t),0.01,0.1)

def chiptune(duration, bpm=118, seed=0):
    beat=60/bpm; step=beat/4; n=int(duration/step)+1
    prog=[[60,64,67,72],[55,59,62,67],[57,60,64,69],[53,57,60,65]]  # C G Am F
    out=np.zeros(int(SR*(duration+1)))
    sq=lambda f,t,d=0.25: np.where((t*f)%1<d,1.0,-1.0)
    for i in range(n):
        bar=(i//16)%4; chord=prog[bar]; st=int(i*step*SR)
        t=_t(step*0.9); note=chord[i%4] + (12 if (i//4)%2 else 0)
        f=440*2**((note-69)/12)
        out[st:st+len(t)]+=0.045*sq(f,t,0.25)*env(len(t),0.002,0.03)
        if i%4==0:  # bass
            tb=_t(beat*0.95); fb=440*2**((chord[0]-24-69)/12)
            out[st:st+len(tb)]+=0.07*sq(fb,tb,0.5)*env(len(tb),0.005,0.05)
        if i%8==4:  # snare-ish
            tn=_t(0.08); out[st:st+len(tn)]+=0.05*np.random.default_rng(i).normal(0,1,len(tn))*np.exp(-tn*40)
        if i%8==0:  # kick
            tk=_t(0.15); fk=np.linspace(150,40,len(tk))
            out[st:st+len(tk)]+=0.18*np.sin(2*np.pi*np.cumsum(fk)/SR)*np.exp(-tk*20)
    return out[:int(SR*duration)]

def stamp():
    t=_t(0.35); f=np.linspace(120,45,len(t)); thump=0.8*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*14)
    n=np.random.default_rng(5).normal(0,1,len(t))*np.exp(-t*40)*0.25
    return thump+n
def ticks(dur=1.4, n=22):
    out=np.zeros(int(SR*(dur+0.1))); 
    for i in range(n):
        st=int(SR*dur*(1-(1-i/n)**1.6)); t=_t(0.03)
        out[st:st+len(t)]+=0.18*np.sin(2*np.pi*2600*t)*np.exp(-t*120)
    return out
def heart_pop():
    t=_t(0.25); f=np.linspace(600,1300,len(t)); return 0.35*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*12)

def siren(dur=1.2):
    t=_t(dur); f=700+350*np.sin(2*np.pi*2.2*t); return 0.22*np.sin(2*np.pi*np.cumsum(f)/SR)*env(len(t),0.02,0.2)
def boom():
    t=_t(0.9); f=np.linspace(90,30,len(t)); b=0.9*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*4)
    n=np.random.default_rng(9).normal(0,1,len(t))*np.exp(-t*25)*0.3; return b+n
def riser(dur=0.8):
    t=_t(dur); n=np.random.default_rng(4).normal(0,1,len(t)); f=np.linspace(200,2000,len(t))
    return 0.12*(n*0.5+np.sin(2*np.pi*np.cumsum(f)/SR))*np.linspace(0,1,len(t))

def synthwave_track(duration, bpm=118, seed=0):
    """Original synthwave bed: four-on-the-floor kick, snare on 2/4, 8th hats, saw bass, detuned pad. Am-F-C-G."""
    from scipy.signal import butter, lfilter
    N=int(SR*(duration+1)); out=np.zeros(N); beat=60/bpm
    roots=[57,53,48,55]  # A F C G (midi)
    chords=[[57,60,64],[53,57,60],[48,52,55],[55,59,62]]
    hz=lambda m: 440*2**((m-69)/12)
    rng=np.random.default_rng(seed)
    nb=int(duration/beat)+2
    side=np.ones(N)
    for b in range(nb):
        st=int(b*beat*SR)
        if st>=N: break
        tk=_t(0.28); fk=np.linspace(140,42,len(tk)); k=0.85*np.sin(2*np.pi*np.cumsum(fk)/SR)*np.exp(-tk*11)
        e=min(N,st+len(k)); out[st:e]+=k[:e-st]
        sd=int(0.22*SR); e2=min(N,st+sd); side[st:e2]=np.minimum(side[st:e2],np.linspace(0.35,1,e2-st))
        if b%2==1:
            ts=_t(0.2); sn=rng.normal(0,1,len(ts))*np.exp(-ts*18)*0.35+0.25*np.sin(2*np.pi*190*ts)*np.exp(-ts*25)
            e=min(N,st+len(sn)); out[st:e]+=sn[:e-st]
        for h in (0,0.5):
            hs=int((b+h)*beat*SR); th=_t(0.05); hh=rng.normal(0,1,len(th))*np.exp(-th*90)*0.12
            e=min(N,hs+len(hh)); 
            if hs<N: out[hs:e]+=np.diff(np.concatenate([[0],hh]))[:e-hs]*3
    # bass (8ths) + pad per bar
    bar=4*beat; nbar=int(duration/bar)+2
    b_,a_=butter(2,900/(SR/2)); bp,ap=butter(2,2200/(SR/2))
    bass=np.zeros(N); pad=np.zeros(N)
    for i in range(nbar):
        r=roots[i%4]; st=int(i*bar*SR)
        for j in range(8):
            s=st+int(j*beat/2*SR); tt=_t(beat/2*0.9); f=hz(r-12 + (12 if j%4==3 else 0))
            saw=2*((tt*f)%1)-1; seg=0.25*saw*env(len(tt),0.003,0.04)
            e=min(N,s+len(seg))
            if s<N: bass[s:e]+=seg[:e-s]
        tt=_t(bar); seg=np.zeros(len(tt))
        for m in chords[i%4]:
            for dt in (-0.12,0.12):
                f=hz(m+dt); seg+=0.05*(2*((tt*f+rng.random())%1)-1)
        seg*=env(len(tt),0.25,0.4); e=min(N,st+len(seg))
        if st<N: pad[st:e]+=seg[:e-st]
    bass=lfilter(b_,a_,bass); pad=lfilter(bp,ap,pad)
    out=out*0.55+bass*side*1.0+pad*side*0.9
    out=out/ (np.abs(out).max()+1e-6)*0.8
    return out[:int(SR*duration)]
