#!/usr/bin/env python3
"""
sff_lib - Lecteur/ecrivain SFF v1 & v2 fidele au moteur Ikemen GO.
Decodeurs portes depuis Ikemen-GO-0.99.0/src/image.go (RlePcx, Rle8, Rle5, Lz5, PNG).
Ecriture: SFF v2.01 (RLE8 pour 8-bit indexe, PNG32 pour RGBA).
"""

import io
import struct
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image

SIG = b"ElecbyteSpr\x00"


@dataclass
class SffSprite:
    group: int = 0
    number: int = 0
    width: int = 0
    height: int = 0
    axisx: int = 0
    axisy: int = 0
    palidx: int = -1
    coldepth: int = 8
    pixels: bytes = b""        # indexe 8-bit (w*h) si coldepth<=8
    rgba: bytes = b""          # RGBA brut (w*h*4) si coldepth>8
    link: int = -1             # index du sprite source si lie (size==0)

    @property
    def is_linked(self):
        return self.link >= 0

    def to_image(self, palettes):
        """Retourne une PIL.Image RGBA."""
        if self.is_linked:
            raise ValueError("sprite lie, resoudre le lien d'abord")
        if self.rgba:
            return Image.frombytes("RGBA", (self.width, self.height), bytes(self.rgba))
        if not self.pixels:
            return None
        img = Image.frombytes("P", (self.width, self.height), bytes(self.pixels))
        pal = palettes[self.palidx] if 0 <= self.palidx < len(palettes) else None
        if pal is None:
            pal = [(i, i, i, 255) for i in range(256)]
        flat = []
        for (r, g, b, a) in pal:
            flat += [r, g, b]
        img.putpalette(flat)
        rgba = img.convert("RGBA")
        # index 0 = transparent (convention MUGEN), + alpha palette
        px = bytearray(rgba.tobytes())
        idx = bytes(self.pixels)
        for i, ci in enumerate(idx):
            a = pal[ci][3] if ci < len(pal) else 255
            if ci == 0:
                a = 0
            px[i * 4 + 3] = a
        return Image.frombytes("RGBA", (self.width, self.height), bytes(px))


@dataclass
class SffFile:
    version: tuple = (0, 0, 0, 2)
    sprites: list = field(default_factory=list)     # [SffSprite]
    palettes: list = field(default_factory=list)    # [[(r,g,b,a)x256]]
    pal_meta: list = field(default_factory=list)    # [(group, number, numcols, link)]


# ---------------------------------------------------------------- decodeurs

def _rle_pcx_decode(rle, w, h, bpl):
    if not rle or bpl <= 0:
        return bytes(rle)
    p = bytearray(w * h)
    i = j = k = 0
    n_p, n_rle = len(p), len(rle)
    while j < n_p:
        n, d = 1, rle[i]
        if i < n_rle - 1:
            i += 1
        if d >= 0xC0:
            n = d & 0x3F
            d = rle[i]
            if i < n_rle - 1:
                i += 1
        while n > 0:
            if k < w and j < n_p:
                p[j] = d
                j += 1
            k += 1
            if k == bpl:
                k = 0
                n = 1
            n -= 1
    return bytes(p)


def _rle8_decode(rle, w, h):
    if not rle:
        return rle
    p = bytearray(w * h)
    i = j = 0
    n_p, n_rle = len(p), len(rle)
    while j < n_p:
        n, d = 1, rle[i]
        if i < n_rle - 1:
            i += 1
        if d & 0xC0 == 0x40:
            n = d & 0x3F
            d = rle[i]
            if i < n_rle - 1:
                i += 1
        while n > 0:
            if j < n_p:
                p[j] = d
                j += 1
            n -= 1
    return bytes(p)


def _rle5_decode(rle, w, h):
    if not rle:
        return rle
    p = bytearray(w * h)
    i = j = 0
    n_p, n_rle = len(p), len(rle)
    while j < n_p:
        rl = rle[i]
        if i < n_rle - 1:
            i += 1
        dl = rle[i] & 0x7F
        c = 0
        if rle[i] >> 7 != 0:
            if i < n_rle - 1:
                i += 1
            c = rle[i]
        if i < n_rle - 1:
            i += 1
        while True:
            if j < n_p:
                p[j] = c
                j += 1
            rl -= 1
            if rl < 0:
                dl -= 1
                if dl < 0:
                    break
                c = rle[i] & 0x1F
                rl = rle[i] >> 5
                if i < n_rle - 1:
                    i += 1
    return bytes(p)


def _lz5_decode(rle, w, h):
    if not rle:
        return rle
    p = bytearray(w * h)
    i = j = n = 0
    n_p, n_rle = len(p), len(rle)
    ct, cts, rb, rbc = rle[0], 0, 0, 0
    if i < n_rle - 1:
        i += 1
    while j < n_p:
        d = rle[i]
        if i < n_rle - 1:
            i += 1
        if ct & (1 << cts):
            if d & 0x3F == 0:
                d = (d << 2 | rle[i]) + 1
                if i < n_rle - 1:
                    i += 1
                n = rle[i] + 2
                if i < n_rle - 1:
                    i += 1
            else:
                rb |= (d & 0xC0) >> rbc
                rbc += 2
                n = d & 0x3F
                if rbc < 8:
                    d = rle[i] + 1
                    if i < n_rle - 1:
                        i += 1
                else:
                    d = rb + 1
                    rb, rbc = 0, 0
            while True:
                if j < n_p:
                    p[j] = p[j - d]
                    j += 1
                n -= 1
                if n < 0:
                    break
        else:
            if d & 0xE0 == 0:
                n = rle[i] + 8
                if i < n_rle - 1:
                    i += 1
            else:
                n = d >> 5
                d &= 0x1F
            while n > 0:
                if j < n_p:
                    p[j] = d
                    j += 1
                n -= 1
        cts += 1
        if cts >= 8:
            ct, cts = rle[i], 0
            if i < n_rle - 1:
                i += 1
    return bytes(p)


# ---------------------------------------------------------------- lecture

def read_sff(path, want_palettes=True):
    """Lit un SFF v1 ou v2, retourne SffFile (liens resolus en place)."""
    data = Path(path).read_bytes()
    if data[:12] != SIG:
        raise ValueError(f"{path}: signature SFF invalide")
    ver3, ver2, ver1, ver0 = data[12], data[13], data[14], data[15]
    out = SffFile(version=(ver3, ver2, ver1, ver0))
    if ver0 == 1:
        _read_v1(data, out)
    elif ver0 == 2:
        _read_v2(data, out)
    else:
        raise ValueError(f"{path}: version SFF inconnue {ver0}")
    _resolve_links(out)
    return out


def _resolve_links(sff):
    for s in sff.sprites:
        if s.is_linked and 0 <= s.link < len(sff.sprites):
            src = sff.sprites[s.link]
            s.width, s.height = src.width, src.height
            s.pixels, s.rgba = src.pixels, src.rgba
            s.coldepth = src.coldepth
            if s.palidx < 0:
                s.palidx = src.palidx


def _read_v1(data, out):
    # header: sig12 ver4 ngroups4 nimages4 firstofs4 subhdrsize4 paltype1 ...
    nimages = struct.unpack_from("<I", data, 20)[0]
    first = struct.unpack_from("<I", data, 24)[0]
    ofs = first
    prev_pal_idx = -1
    pal_map = {}  # raw palette bytes -> index
    for i in range(nimages):
        if ofs + 32 > len(data):
            break
        nxt, size = struct.unpack_from("<II", data, ofs)
        ax, ay, grp, num, link = struct.unpack_from("<hhhhH", data, ofs + 8)
        same_pal = data[ofs + 18]
        spr = SffSprite(group=grp, number=num, axisx=ax, axisy=ay)
        if size == 0:
            spr.link = link
        else:
            pcx_ofs = ofs + 32
            end = nxt if (nxt > ofs and nxt <= len(data)) else pcx_ofs + size
            pcx = data[pcx_ofs:end]
            if len(pcx) >= 128:
                bpp = pcx[3]
                x0, y0, x1, y1 = struct.unpack_from("<4H", pcx, 4)
                w, h = x1 - x0 + 1, y1 - y0 + 1
                bpl = struct.unpack_from("<H", pcx, 66)[0]
                enc = pcx[2]
                pal_same = same_pal != 0 and prev_pal_idx >= 0
                pal_size = 0 if pal_same else 768
                px_data = pcx[128:len(pcx) - pal_size if pal_size else len(pcx)]
                if bpp == 8 and w > 0 and h > 0:
                    if enc == 1:
                        spr.pixels = _rle_pcx_decode(px_data, w, h, bpl)
                    else:
                        spr.pixels = bytes(px_data[:w * h])
                    spr.width, spr.height = w, h
                    if pal_same:
                        spr.palidx = prev_pal_idx
                    else:
                        praw = pcx[-768:]
                        if praw in pal_map:
                            spr.palidx = pal_map[praw]
                        else:
                            pal = [(praw[k * 3], praw[k * 3 + 1], praw[k * 3 + 2], 255)
                                   for k in range(256)] if len(praw) >= 768 else \
                                  [(k, k, k, 255) for k in range(256)]
                            out.palettes.append(pal)
                            out.pal_meta.append((1, len(out.palettes), 256, -1))
                            spr.palidx = len(out.palettes) - 1
                            pal_map[praw] = spr.palidx
                        prev_pal_idx = spr.palidx
        out.sprites.append(spr)
        if nxt == 0 or nxt <= ofs:
            break
        ofs = nxt


def _read_v2(data, out):
    f = io.BytesIO(data)
    f.seek(16)
    f.read(4)                              # dummy
    f.read(16)                             # 4x dummy
    spr_ofs, n_spr, pal_ofs, n_pal, lofs, _ldlen, tofs = struct.unpack(
        "<7I", f.read(28))
    ver2 = out.version[1]
    # palettes
    for i in range(n_pal):
        o = pal_ofs + i * 16
        grp, num, ncols, link = struct.unpack_from("<hhhH", data, o)
        pofs, psiz = struct.unpack_from("<II", data, o + 10)
        if psiz == 0 and link < len(out.palettes):
            pal = list(out.palettes[link])
        else:
            pal = []
            base = lofs + pofs
            for k in range(min(psiz // 4, 256)):
                chunk = data[base + k * 4: base + k * 4 + 4]
                if len(chunk) < 4:
                    break
                r, g, b, a = chunk
                if ver2 == 0:
                    a = 255
                pal.append((r, g, b, a))
            while len(pal) < 256:
                pal.append((0, 0, 0, 255))
        out.palettes.append(pal)
        out.pal_meta.append((grp, num, ncols, link))
    # sprites
    for i in range(n_spr):
        o = spr_ofs + i * 28
        grp, num, w, h, ax, ay, link = struct.unpack_from("<hhHHhhH", data, o)
        fmt, depth = data[o + 14], data[o + 15]
        dofs, dsiz = struct.unpack_from("<II", data, o + 16)
        palidx, flags = struct.unpack_from("<HH", data, o + 24)
        base = (tofs if flags & 1 else lofs) + dofs
        spr = SffSprite(group=grp, number=num, width=w, height=h,
                        axisx=ax, axisy=ay, palidx=palidx, coldepth=depth)
        if dsiz == 0:
            spr.link = link
        else:
            try:
                if fmt == 0:
                    raw = data[base: base + dsiz]
                    if depth == 8:
                        spr.pixels = raw[:w * h]
                    elif depth in (24, 32):
                        if depth == 24:
                            img = Image.frombytes("RGB", (w, h), bytes(raw[:w * h * 3]))
                            spr.rgba = img.convert("RGBA").tobytes()
                        else:
                            spr.rgba = bytes(raw[:w * h * 4])
                        spr.coldepth = 32
                elif fmt in (2, 3, 4):
                    comp = data[base + 4: base + dsiz]
                    if fmt == 2:
                        spr.pixels = _rle8_decode(comp, w, h)
                    elif fmt == 3:
                        spr.pixels = _rle5_decode(comp, w, h)
                    else:
                        spr.pixels = _lz5_decode(comp, w, h)
                elif fmt in (10, 11, 12):
                    img = Image.open(io.BytesIO(data[base + 4: base + dsiz]))
                    if fmt == 10 and img.mode == "P":
                        spr.pixels = img.tobytes()
                        spr.width, spr.height = img.size
                    else:
                        spr.rgba = img.convert("RGBA").tobytes()
                        spr.width, spr.height = img.size
                        spr.coldepth = 32
            except Exception:
                pass  # sprite corrompu: garde vide
        out.sprites.append(spr)


# ---------------------------------------------------------------- ecriture

def _rle8_encode(px):
    """RLE8 SFFv2 vectorise numpy (runs <=63, litteraux sauf prefixe 0x40)."""
    try:
        import numpy as _np
    except ImportError:
        return _rle8_encode_slow(px)
    a = _np.frombuffer(bytes(px), dtype=_np.uint8)
    if a.size == 0:
        return b""
    # bornes des runs de valeurs identiques
    cut = _np.flatnonzero(a[1:] != a[:-1]) + 1
    starts = _np.concatenate(([0], cut))
    ends = _np.concatenate((cut, [a.size]))
    out = bytearray()
    for s, e in zip(starts.tolist(), ends.tolist()):
        d = int(a[s])
        ln = e - s
        if ln == 1 and (d & 0xC0) != 0x40:
            out.append(d)
            continue
        while ln > 0:
            c = min(ln, 63)
            out.append(0x40 | c)
            out.append(d)
            ln -= c
    return bytes(out)


def _rle8_encode_slow(px):
    outb = bytearray()
    i, n = 0, len(px)
    while i < n:
        d = px[i]
        run = 1
        while i + run < n and px[i + run] == d and run < 63:
            run += 1
        if run > 1 or (d & 0xC0) == 0x40:
            outb.append(0x40 | run)
            outb.append(d)
        else:
            outb.append(d)
        i += run
    return bytes(outb)


def write_sff_v2(sff, path):
    """Ecrit un SFF v2.01 lisible par Ikemen GO.
    8-bit indexe -> fmt 2 (RLE8) ; RGBA -> fmt 12 (PNG32, prefixe 4 octets)."""
    # restaure les liens: sprites partageant les memes pixels
    spr_headers = []
    ldata = bytearray()
    tdata = bytearray()
    seen = {}
    for s in sff.sprites:
        key = (id(s.pixels) if s.pixels else 0, id(s.rgba) if s.rgba else 0,
               bytes(s.pixels[:64]) if s.pixels else bytes(s.rgba[:64]) if s.rgba else b"")
        link_idx, dofs, dsiz, fmt, flags, depth = 0, 0, 0, 0, 0, s.coldepth
        if not s.pixels and not s.rgba:
            # sprite vide -> 1x1 transparent indexe
            fmt, depth = 2, 8
            comp = _rle8_encode(b"\x00")
            dofs = len(ldata)
            ldata += struct.pack("<I", 1) + comp
            dsiz = 4 + len(comp)
            w, h = 1, 1
        elif key in seen:
            link_idx = seen[key]
            w, h = s.width, s.height
            dsiz = 0
        elif s.pixels:
            fmt, depth = 2, 8
            comp = _rle8_encode(bytes(s.pixels))
            dofs = len(ldata)
            ldata += struct.pack("<I", len(s.pixels)) + comp
            dsiz = 4 + len(comp)
            w, h = s.width, s.height
            seen[key] = len(spr_headers)
        else:
            fmt, depth, flags = 12, 32, 1
            img = Image.frombytes("RGBA", (s.width, s.height), bytes(s.rgba))
            buf = io.BytesIO()
            img.save(buf, "PNG", optimize=False, compress_level=6)
            png = buf.getvalue()
            dofs = len(tdata)
            tdata += struct.pack("<I", len(s.rgba)) + png
            dsiz = 4 + len(png)
            w, h = s.width, s.height
            seen[key] = len(spr_headers)
        palidx = max(0, s.palidx) if depth == 8 else max(0, s.palidx)
        spr_headers.append((s.group, s.number, w, h, s.axisx, s.axisy,
                            link_idx, fmt, depth, dofs, dsiz, palidx, flags))

    # palettes -> ldata (apres les sprites ldata)
    pal_headers = []
    for i, pal in enumerate(sff.palettes):
        meta = sff.pal_meta[i] if i < len(sff.pal_meta) else (1, i + 1, 256, -1)
        grp, num, ncols, _ = meta
        pofs = len(ldata)
        for (r, g, b, a) in pal[:256]:
            ldata += bytes((r, g, b, a))
        pal_headers.append((grp, num, ncols if ncols else 256, 0, pofs, 1024))

    header_size = 0x44  # sig12+ver4+res4+res16+7*4+tdatalen4
    spr_list_ofs = header_size
    spr_list_len = 28 * len(spr_headers)
    pal_list_ofs = spr_list_ofs + spr_list_len
    pal_list_len = 16 * len(pal_headers)
    lofs = pal_list_ofs + pal_list_len
    tofs = lofs + len(ldata)

    with open(path, "wb") as f:
        f.write(SIG)
        f.write(bytes((0, 1, 0, 2)))                     # v2.01
        f.write(b"\x00" * 4)                             # reserved
        f.write(b"\x00" * 16)                            # compat+reserved
        f.write(struct.pack("<7I", spr_list_ofs, len(spr_headers),
                            pal_list_ofs, len(pal_headers),
                            lofs, len(ldata), tofs))
        f.write(struct.pack("<I", len(tdata)))
        pad = header_size - f.tell()
        if pad > 0:
            f.write(b"\x00" * pad)
        for (grp, num, w, h, ax, ay, link, fmt, depth, dofs, dsiz, palidx,
             flags) in spr_headers:
            f.write(struct.pack("<hhHHhhHBBIIHH", grp, num, w, h, ax, ay,
                                link, fmt, depth, dofs, dsiz, palidx, flags))
        for (grp, num, ncols, link, pofs, psiz) in pal_headers:
            f.write(struct.pack("<hhhHII", grp, num, ncols, link, pofs, psiz))
        f.write(ldata)
        f.write(tdata)
