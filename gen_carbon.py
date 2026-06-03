#!/usr/bin/env python3
"""
Carbon badge — the embodied, 8-bit "photo" of an elemental (the .tiff to the
silicon .png). Aether wears a human face: a robed, blindfolded figure among
floating stones laced with entanglement threads — the one who feels the unseen
pull and lets the weight of things hang in the air. Emo register: the patient,
impermanent force (mono no aware), not a brawler.

Pure stdlib: hand-rolled Deflate baseline TIFF, no deps. Writes agents/<slug>.tiff.
"""
import json, re, struct, zlib, hashlib
from pathlib import Path

ROOT = Path(__file__).parent
R = json.loads((ROOT/"roster.json").read_text(encoding="utf-8"))
AG = ROOT/"agents"; AG.mkdir(exist_ok=True)
CLS = {c["id"]: c for c in R["classes"]}

LW, LH, S = 64, 80, 5
W, H = LW*S, LH*S

VOID=(7,6,13); GOLD=(214,178,90); GOLD_L=(240,212,137); INDIGO=(124,143,208)
def slug(s): return re.sub(r"[^a-z0-9]+","-",s.lower()).strip("-") or "agent"
def clamp(v): return 0 if v<0 else 255 if v>255 else int(round(v))
def mix(a,b,t): return tuple(clamp(a[i]+(b[i]-a[i])*t) for i in range(3))
def shade(c,t): return mix(c,(0,0,0),t)
def tint(c,t): return mix(c,(255,255,255),t)

def tiff(path, w, h, pixels):
    raw = bytearray()
    for (r,g,b) in pixels: raw += bytes((r,g,b))
    strip = zlib.compress(bytes(raw), 9)
    BPS=8+len(strip); IFD=BPS+6
    hdr=b"II"+struct.pack("<H",42)+struct.pack("<I",IFD)
    bps=struct.pack("<HHH",8,8,8)
    def e(t,ty,c,v): return struct.pack("<HHI",t,ty,c)+v
    def sh(v): return struct.pack("<HH",v,0)
    def lo(v): return struct.pack("<I",v)
    ent=[e(256,3,1,sh(w)),e(257,3,1,sh(h)),e(258,3,3,lo(BPS)),e(259,3,1,sh(8)),
         e(262,3,1,sh(2)),e(273,4,1,lo(8)),e(277,3,1,sh(3)),e(278,3,1,sh(h)),
         e(279,4,1,lo(len(strip))),e(284,3,1,sh(1))]
    ifd=struct.pack("<H",len(ent))+b"".join(ent)+struct.pack("<I",0)
    Path(path).write_bytes(hdr+strip+bps+ifd)

def png(path,w,h,px):     # preview only
    raw=bytearray()
    for y in range(h):
        raw.append(0)
        for x in range(w): raw+=bytes(px[y*w+x])
    comp=zlib.compress(bytes(raw),9)
    def ch(t,d): return struct.pack(">I",len(d))+t+d+struct.pack(">I",zlib.crc32(t+d)&0xffffffff)
    Path(path).write_bytes(b"\x89PNG\r\n\x1a\n"+ch(b"IHDR",struct.pack(">IIBBBBB",w,h,8,2,0,0,0))+ch(b"IDAT",comp)+ch(b"IEND",b""))

def portrait(member):
    cls = CLS[member["class"]]
    rb = hashlib.sha256(("aether:"+member["name"]).encode()).digest()
    g = [VOID]*(LW*LH); drawn=[False]*(LW*LH)
    def put(x,y,c):
        if 0<=x<LW and 0<=y<LH: g[y*LW+x]=c; drawn[y*LW+x]=True
    def soft(x,y,c,a):                       # blend without marking (for glow/threads)
        if 0<=x<LW and 0<=y<LH:
            i=y*LW+x; g[i]=mix(g[i],c,a)
    def rect(x0,y0,x1,y1,c):
        for y in range(int(y0),int(y1)+1):
            for x in range(int(x0),int(x1)+1): put(x,y,c)
    def ell(cx,cy,rx,ry,c):
        for y in range(int(cy-ry),int(cy+ry)+1):
            for x in range(int(cx-rx),int(cx+rx)+1):
                if ((x-cx)/rx)**2+((y-cy)/ry)**2<=1.0: put(x,y,c)
    def thread(x0,y0,x1,y1):
        n=int(max(abs(x1-x0),abs(y1-y0)))+1
        for k in range(n+1):
            t=k/n; soft(round(x0+(x1-x0)*t), round(y0+(y1-y0)*t), INDIGO, 0.30)

    # faint gold horizon glow, top-center (the unseen pull)
    for y in range(LH):
        for x in range(LW):
            d=((x-32)**2/520.0+(y-10)**2/240.0)
            if d<1: soft(x,y, mix(GOLD,INDIGO,0.4), 0.10*(1-d))

    cx=32
    # floating stones (behind the figure) — deterministic placement + facets
    stones=[(12,15,5),(52,11,6),(50,30,4),(11,38,4),(54,52,5),(20,9,3)]
    for k,(sx,sy,sr) in enumerate(stones):
        sx+= (rb[k]%3)-1; sy+= (rb[k+6]%3)-1
        base=(116,120,130)
        ell(sx,sy,sr,sr-1, base)
        ell(sx-1,sy-1,max(1,sr-2),max(1,sr-2), tint(base,0.22))   # top-left facet
        ell(sx+1,sy+1,max(1,sr-2),max(1,sr-3), shade(base,0.35))  # underside
    # entanglement threads between stones (and toward the heart)
    pts=[(12,15),(52,11),(50,30),(11,38),(54,52),(32,40)]
    for a in range(len(pts)):
        b=(a+1)%len(pts); thread(*pts[a],*pts[b])
    thread(20,9,52,11); thread(50,30,32,40)

    skin=(226,192,160); skin_sh=shade(skin,0.22)
    robe=(140,98,58); robe_sh=shade(robe,0.32)
    hair=(22,20,28)

    # robe / shoulders
    rect(8,58,55,79, robe)
    for x in range(8,56):
        if x<13 or x>50: rect(x,58,x,60,VOID)
    rect(20,57,44,60, robe_sh)                     # collar shade
    for k in range(7): put(32-k,57+k, robe_sh); put(32+k,57+k, robe_sh)
    rect(30,58,34,68, shade(robe,0.18))            # inner fold
    # neck + head
    rect(27,47,37,57, skin_sh)
    ell(cx,33,14,17, skin)
    for y in range(16,52):                          # right-side shadow
        for x in range(cx+3,48):
            i=y*LW+x
            if drawn[i] and g[i]==skin: g[i]=mix(skin,skin_sh,0.5)
    # hair: crown + topknot bun, framing
    ell(cx,20,15,9, hair)
    rect(17,18,20,40, hair); rect(44,18,47,40, hair)
    ell(cx,9,5,5, hair)                             # the bun
    put(cx,4,hair); rect(31,3,33,5, hair)
    # serene mouth
    rect(28,44,36,45, shade(skin,0.34))
    put(27,44, skin_sh); put(37,44, skin_sh)
    # the blindfold — white gauze band across the eyes, with a frayed trailing tail
    band=(230,228,222); band_sh=(190,188,182)
    rect(16,30,48,37, band)
    rect(16,37,48,37, band_sh)
    rect(16,30,48,30, tint(band,0.25))
    for y in range(31,37): put(48, y, band_sh)
    # trailing tail off the right, lifting on an unfelt current
    tail=[(49,33),(51,32),(53,32),(55,31),(57,31),(58,30),(60,29)]
    for i,(tx,ty) in enumerate(tail):
        put(tx,ty, band if i%2 else band_sh); put(tx,ty+1, band_sh)
    put(61,28, band_sh); put(60,30, band_sh)        # fray

    # outline pass (8-bit sticker edge)
    based=list(drawn)
    for y in range(LH):
        for x in range(LW):
            if based[y*LW+x]: continue
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                nx,ny=x+dx,y+dy
                if 0<=nx<LW and 0<=ny<LH and based[ny*LW+nx]:
                    g[y*LW+x]=(10,9,16); break

    out=[VOID]*(W*H)
    for y in range(LH):
        for x in range(LW):
            c=g[y*LW+x]
            for yy in range(S):
                row=(y*S+yy)*W
                for xx in range(S): out[row+x*S+xx]=c
    return out

import sys
if __name__=="__main__" and len(sys.argv)>1 and sys.argv[1]=="--preview":
    m=R["members"][0]; px=portrait(m)
    tiff(ROOT/"_preview_carbon.tiff", W,H,px); png(ROOT/"_preview_carbon.png", W,H,px)
    print("preview written:", m["name"])
else:
    for m in R["members"]:
        tiff(AG/f"{slug(m['name'])}.tiff", W, H, portrait(m))
        print(f"carbon badge -> agents/{slug(m['name'])}.tiff  ({m['name']})")
