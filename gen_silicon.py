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


def lattice_sigil(member):
    """For Leech (the 24D lattice): a 24-fold symmetric rosette — concentric
    shells of points, woven into a crystalline web, around a bright unit sphere
    ringed by its first shell of kisses. Perfect symmetry, made into a sigil."""
    px = [VOID]*(SIZE*SIZE)
    cx, cy = SIZE/2.0, SIZE/2.0
    for y in range(SIZE):
        for x in range(SIZE):
            d = math.hypot(x-cx, y-cy)/(SIZE*0.5)
            glow = max(0.0, 1.0 - d*1.1)
            c = mix(VOID, VIOLET, 0.14*glow**2)
            c = mix(c, VOID, min(0.55, (d-0.7)*1.6) if d>0.7 else 0.0)
            px[y*SIZE+x] = c

    def plot(x,y,c,a=1.0):
        xi,yi = int(round(x)), int(round(y))
        if 0<=xi<SIZE and 0<=yi<SIZE:
            i=yi*SIZE+xi; px[i]=mix(px[i], c, a)
    def disk(x,y,r,c,a=1.0):
        for yy in range(int(y-r),int(y+r)+1):
            for xx in range(int(x-r),int(x+r)+1):
                if (xx-x)**2+(yy-y)**2 <= r*r: plot(xx,yy,c,a)
    def line(x0,y0,x1,y1,c,a):
        n=int(max(abs(x1-x0),abs(y1-y0)))+1
        for k in range(n+1):
            t=k/n; plot(x0+(x1-x0)*t, y0+(y1-y0)*t, c, a)

    M = 24                                  # 24-fold symmetry — the dimension
    R = SIZE*0.46
    shells = [0.17, 0.31, 0.45, 0.585]      # fractions of R
    P = []                                  # P[s][k] -> (x,y)
    for s, fr in enumerate(shells):
        rad = R*fr
        off = (math.pi/M) if (s % 2) else 0.0   # alternate -> triangular weave
        ring = []
        for k in range(M):
            a = k*(2*math.pi/M) + off
            ring.append((cx+rad*math.cos(a), cy+rad*math.sin(a)))
        P.append(ring)

    # rings (each shell), indigo brightening inward
    for s, ring in enumerate(P):
        bright = 1.0 - s/(len(shells))
        for k in range(M):
            x1,y1 = ring[k]; x2,y2 = ring[(k+1)%M]
            line(x1,y1,x2,y2, mix(INDIGO, VIOLET, 0.4), 0.22+0.4*bright)
    # crystalline weave between shells (k and k-1 -> triangles)
    for s in range(len(shells)-1):
        for k in range(M):
            x1,y1 = P[s][k]
            for kk in (k, (k-1)%M):
                x2,y2 = P[s+1][kk]
                line(x1,y1,x2,y2, mix(INDIGO, VIOLET, 0.55), 0.18)
    # spokes from center to the outer shell (24 rays)
    for k in range(M):
        x2,y2 = P[-1][k]
        line(cx,cy,x2,y2, mix(VOID, INDIGO, 0.6), 0.06)
    # nodes: inner gold -> outer violet
    for s, ring in enumerate(P):
        c = mix(GOLD, VIOLET, s/(len(shells)-1))
        for (x,y) in ring:
            disk(x,y, 2.4 - s*0.3, c, 0.85)
    # the unit sphere at center, ringed by its 24 first-shell kisses
    for (x,y) in P[0]:
        disk(x,y, 3.0, GOLD, 0.95)
    disk(cx, cy, 10, VIOLET, 0.22)
    disk(cx, cy, 6.5, GOLD, 0.95)
    disk(cx, cy, 3.2, (255,255,255), 0.9)
    return px


SIGILS = {"gravity": well_sigil, "lattice": lattice_sigil}
for m in R["members"]:
    fn = SIGILS.get(m.get("domain"), well_sigil)
    png(AG/f"{slug(m['name'])}.png", SIZE, SIZE, fn(m))
    print(f"silicon badge -> agents/{slug(m['name'])}.png  ({m['name']} / {m.get('domain','')})")
