#!/usr/bin/env python3
"""
Silicon badge — the abstract, computed essence of an elemental.

For Aether (gravity): an entanglement lattice pulled into a gravity well —
the pamphlet's thesis made into a sigil. Spacetime, sewn from threads, dimpling
toward a bright horizon of bits at the center. Deterministic, pure stdlib PNG.
Writes agents/<slug>.png.
"""
import json, re, zlib, struct, hashlib, math
from pathlib import Path

ROOT = Path(__file__).parent
R = json.loads((ROOT/"roster.json").read_text(encoding="utf-8"))
AG = ROOT/"agents"; AG.mkdir(exist_ok=True)
CLS = {c["id"]: c for c in R["classes"]}

SIZE = 360
VOID  = (7, 6, 13)
INDIGO= (124, 143, 208)
VIOLET= (167, 139, 250)
GOLD  = (240, 212, 137)
GOLD_D= (214, 178, 90)

def slug(s): return re.sub(r"[^a-z0-9]+","-",s.lower()).strip("-") or "agent"
def clamp(v): return 0 if v<0 else 255 if v>255 else int(round(v))
def mix(a,b,t): return tuple(clamp(a[i]+(b[i]-a[i])*t) for i in range(3))

def png(path, w, h, px):
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        for x in range(w): raw += bytes(px[y*w+x])
    comp = zlib.compress(bytes(raw), 9)
    def ch(t,d): return struct.pack(">I",len(d))+t+d+struct.pack(">I",zlib.crc32(t+d)&0xffffffff)
    Path(path).write_bytes(b"\x89PNG\r\n\x1a\n"
        + ch(b"IHDR", struct.pack(">IIBBBBB", w,h,8,2,0,0,0))
        + ch(b"IDAT", comp) + ch(b"IEND", b""))

def well_sigil(member):
    cls = CLS[member["class"]]
    # background: void with a faint gold horizon-glow at center, darker at the rim
    px = [VOID]*(SIZE*SIZE)
    cx, cy = SIZE/2, SIZE*0.52
    for y in range(SIZE):
        for x in range(SIZE):
            d = math.hypot(x-cx, y-cy)/(SIZE*0.5)
            glow = max(0.0, 1.0 - d*1.15)
            c = mix(VOID, mix(GOLD, VIOLET, 0.5), 0.16*glow**2)
            c = mix(c, VOID, min(0.55, (d-0.7)*1.6) if d>0.7 else 0.0)  # vignette
            px[y*SIZE+x] = c

    def plot(x,y,c,a=1.0):
        xi,yi = int(round(x)), int(round(y))
        if 0<=xi<SIZE and 0<=yi<SIZE:
            i=yi*SIZE+xi; px[i]=mix(px[i], c, a)
    def disk(x,y,r,c,a=1.0):
        for yy in range(int(y-r),int(y+r)+1):
            for xx in range(int(x-r),int(x+r)+1):
                if (xx-x)**2+(yy-y)**2 <= r*r: plot(xx,yy,c,a)
    def line(x0,y0,x1,y1,c,a,wd=1):
        n=int(max(abs(x1-x0),abs(y1-y0)))+1
        for k in range(n+1):
            t=k/n; x=x0+(x1-x0)*t; y=y0+(y1-y0)*t
            if wd<=1: plot(x,y,c,a)
            else: disk(x,y,wd/2.0,c,a)

    # the lattice, pulled toward a central well (top-down funnel)
    N = 15
    m = 26
    step = (SIZE-2*m)/(N-1)
    R0 = SIZE*0.40
    PULL = 0.62
    def warp(i,j):
        bx = m+i*step; by = m+j*step
        dx, dy = bx-cx, by-cy
        dist = math.hypot(dx,dy)+1e-6
        well = 1.0/(1.0+(dist/R0)**2)        # Lorentzian dip, deepest at center
        f = PULL*well
        return bx-dx*f, by-dy*f, well
    V = [[warp(i,j) for i in range(N)] for j in range(N)]

    # links (indigo, brightening to gold near the well)
    for j in range(N):
        for i in range(N):
            x,y,w = V[j][i]
            for di,dj in ((1,0),(0,1)):
                if i+di<N and j+dj<N:
                    x2,y2,w2 = V[j+dj][i+di]
                    ww=(w+w2)/2
                    c = mix(INDIGO, GOLD, min(1.0, ww*1.3))
                    a = 0.18 + 0.55*ww
                    line(x,y,x2,y2,c,a,wd=1 if ww<0.5 else 2)
    # vertices (boundary bits): bright dots, gold near center
    for j in range(N):
        for i in range(N):
            x,y,w = V[j][i]
            c = mix(INDIGO, GOLD, min(1.0, w*1.5))
            disk(x,y, 1.4+2.2*w, c, 0.5+0.5*w)

    # the horizon: a bright core of bits at the center
    disk(cx, cy, 9, GOLD, 0.9)
    disk(cx, cy, 16, GOLD_D, 0.35)
    disk(cx, cy, 26, VIOLET, 0.10)
    return px

for m in R["members"]:
    png(AG/f"{slug(m['name'])}.png", SIZE, SIZE, well_sigil(m))
    print(f"silicon badge -> agents/{slug(m['name'])}.png  ({m['name']} · {m.get('domain','')})")
