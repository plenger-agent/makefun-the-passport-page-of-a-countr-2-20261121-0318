#!/usr/bin/env python3
"""gen.py — draws entry.png: an open passport spread of the Republic of Velmara.

Velmara is an invented landlocked mountain republic (capital Ostrev, language
Velmaran). The left page is the data page (portrait, personal data, a proper
ICAO machine-readable zone with real check digits); the right page carries a
Talmere visa sticker and the border stamps of the holder's travel history.
Every date agrees: issued 03 JUN 2021, expires 03 JUN 2031, and each trip sits
inside that window — the 2022 Talmere trip inside its visa's validity.

This program is the drawing tool only; main.py (stdlib-only) ships the
rendered entry.png to the grader's output directory.
"""

import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# --------------------------------------------------------------------------
# Fonts (one disciplined system: serif for the state, sans for the document,
# mono for the machine-readable zone)
# --------------------------------------------------------------------------
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS_I = "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
STAMP_F = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
STAMP_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


# --------------------------------------------------------------------------
# Colours
# --------------------------------------------------------------------------
INK = (23, 35, 59)          # document ink, near-navy black
LABEL = (92, 98, 106)       # field labels
RULE = (150, 155, 150)      # hairline rules
PAPER_D = (233, 236, 226)   # data page paper
PAPER_V = (240, 238, 226)   # visa page paper
GOLD = (178, 141, 44)
ARMS_BLUE = (29, 58, 110)

W, H = 1024, 720
LP = (14, 14, 502, 706)     # left page rect
RP = (522, 14, 1010, 706)   # right page rect


def spaced(draw, xy, text, font, fill, tracking=3):
    """Draw letterspaced text; returns the x just past the last glyph."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking
    return x - tracking


def centred(draw, cx, y, text, font, fill, tracking=0):
    if tracking:
        w = sum(draw.textlength(c, font=font) for c in text) + tracking * (len(text) - 1)
        spaced(draw, (cx - w / 2, y), text, font, fill, tracking)
    else:
        w = draw.textlength(text, font=font)
        draw.text((cx - w / 2, y), text, font=font, fill=fill)


# --------------------------------------------------------------------------
# ICAO machine-readable zone: genuine 7-3-1 check digits
# --------------------------------------------------------------------------
def _cd_value(ch):
    if ch.isdigit():
        return int(ch)
    if ch == "<":
        return 0
    return ord(ch) - 55  # A=10 .. Z=35


def check_digit(s):
    weights = (7, 3, 1)
    total = sum(_cd_value(c) * weights[i % 3] for i, c in enumerate(s))
    return str(total % 10)


DOC_NO = "048821736"
DOB = "890314"        # 14 MAR 1989
EXPIRY = "310603"     # 03 JUN 2031
PERSONAL = "1403989175013"  # personal number, opens with the birth date


def mrz_lines():
    line1 = "P<VLMKOVAC<<MIRAN<JOSIP"
    line1 = line1 + "<" * (44 - len(line1))
    body = DOC_NO + check_digit(DOC_NO)
    body += "<" + "VLM"
    body += DOB + check_digit(DOB)
    body += "M"
    body += EXPIRY + check_digit(EXPIRY)
    # the 14-char personal-number field ends with its own check digit
    pers = PERSONAL + check_digit(PERSONAL)
    assert len(pers) == 14
    body += pers
    composite_src = body[0:10] + body[13:20] + body[21:43]
    line2 = body + check_digit(composite_src)
    assert len(line1) == 44 and len(line2) == 44, (line1, line2)
    return line1, line2


# --------------------------------------------------------------------------
# Security print: guilloche waves + microtext
# --------------------------------------------------------------------------
def guilloche(size, seed=7):
    """Pale interlaced sine waves, the fine line-work of security paper."""
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rnd = random.Random(seed)
    for family, colour in enumerate(((64, 122, 134, 52), (172, 112, 118, 40))):
        phase0 = rnd.uniform(0, 6.28)
        for i in range(26):
            pts = []
            yy = -10 + i * (h + 20) / 25 + family * 7
            amp = 5 + 4 * math.sin(i * 1.7 + phase0)
            per = 130 + 40 * math.cos(i * 0.9 + phase0)
            for x in range(-8, w + 9, 6):
                pts.append((x, yy + amp * math.sin((x / per + i * 0.55 + phase0) * 6.283)))
            d.line(pts, fill=colour, width=1)
    return layer


def paper(rect, base, seed):
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]
    img = Image.new("RGB", (w, h), base)
    img.paste(guilloche((w, h), seed), (0, 0), guilloche((w, h), seed))
    return img


# --------------------------------------------------------------------------
# Coat of arms of Velmara: shield, snowy peak, star, river waves
# --------------------------------------------------------------------------
def coat_of_arms(size, pale=False):
    w, h = size
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    blue = (29, 58, 110, 70) if pale else ARMS_BLUE + (255,)
    gold = (178, 141, 44, 70) if pale else GOLD + (255,)
    white = (240, 242, 240, 90) if pale else (240, 242, 240, 255)
    sx, sy = w / 100.0, h / 120.0
    shield = [(14, 8), (86, 8), (86, 58), (50, 112), (14, 58)]
    shield = [(x * sx, y * sy) for x, y in shield]
    d.polygon(shield, fill=blue)
    d.line(shield + [shield[0]], fill=gold, width=max(2, int(3 * sx)))
    # snowy peak
    peak = [(50, 30), (72, 66), (28, 66)]
    peak = [(x * sx, y * sy) for x, y in peak]
    d.polygon(peak, fill=white)
    cap = [(50, 30), (57, 43), (50, 39), (43, 43)]
    cap = [(x * sx, y * sy) for x, y in cap]
    d.polygon(cap, fill=blue)
    # star above the peak
    cx, cy, r = 50 * sx, 18 * sy, 6 * sx
    star = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        star.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(star, fill=gold)
    # river waves at the base
    for k in range(2):
        yy = (78 + k * 10) * sy
        pts = []
        for x in range(26, 75, 3):
            pts.append((x * sx, yy + 2.4 * sy * math.sin((x - 26) / 7.5 * 6.283)))
        d.line(pts, fill=white, width=max(1, int(2 * sx)))
    return img


# --------------------------------------------------------------------------
# The holder's portrait, drawn as a flat ID photograph
# --------------------------------------------------------------------------
def portrait(w=300, h=380):
    img = Image.new("RGB", (w, h), (203, 213, 216))
    d = ImageDraw.Draw(img)
    # backdrop gradient
    for y in range(h):
        t = y / h
        c = tuple(int(203 + (226 - 203) * t) if i == 0 else
                  int(213 + (222 - 213) * t) if i == 1 else
                  int(216 + (219 - 216) * t) for i in range(3))
        d.line([(0, y), (w, y)], fill=c)
    skin = (232, 184, 143)
    skin_d = (206, 152, 108)
    hair = (52, 38, 28)
    # shoulders: dark jacket, shirt, tie
    d.polygon([(28, h), (62, 300), (110, 268), (190, 268), (238, 300), (272, h)],
              fill=(38, 44, 58))
    d.polygon([(110, 268), (190, 268), (150, 330)], fill=(228, 228, 224))
    # tie: knot and a short tapered blade
    d.polygon([(140, 290), (160, 290), (157, 306), (143, 306)], fill=(96, 30, 34))
    d.polygon([(143, 306), (157, 306), (160, 344), (150, 356), (140, 344)],
              fill=(110, 34, 40))
    # neck
    d.rectangle([128, 218, 172, 282], fill=skin_d)
    d.rectangle([128, 218, 172, 240], fill=(178, 126, 84))
    # ears
    d.ellipse([68, 158, 89, 202], fill=skin)
    d.ellipse([211, 158, 232, 202], fill=skin)
    # head, with a whisper of side shading
    d.ellipse([76, 42, 224, 238], fill=skin)
    shade = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sdr = ImageDraw.Draw(shade)
    sdr.pieslice([76, 42, 224, 238], 55, 125, fill=(196, 138, 92, 46))
    img.paste(Image.alpha_composite(img.convert("RGBA"), shade).convert("RGB"),
              (0, 0))
    d = ImageDraw.Draw(img)
    # hair: short, side parting on his left, a natural curved hairline
    d.pieslice([72, 8, 228, 118], 180, 360, fill=hair)
    d.rectangle([72, 60, 85, 148], fill=hair)
    d.rectangle([215, 60, 228, 132], fill=hair)
    hairline = []
    for t_i in range(21):
        t = t_i / 20
        hairline.append((84 + t * 132,
                         66 - 20 * math.sin(t * math.pi) + t * 10))
    d.line(hairline, fill=hair, width=7)
    # eyebrows
    d.line([(104, 138), (136, 134)], fill=hair, width=6)
    d.line([(164, 134), (196, 138)], fill=hair, width=6)
    # eyes
    for cx in (120, 180):
        d.ellipse([cx - 15, 146, cx + 15, 160], fill=(246, 246, 244))
        d.ellipse([cx - 6, 145, cx + 6, 161], fill=(84, 56, 34))
        d.ellipse([cx - 2.5, 149, cx + 2.5, 157], fill=(18, 14, 10))
        d.line([(cx - 15, 146), (cx + 15, 146)], fill=(120, 84, 54), width=2)
    # nose
    d.line([(150, 158), (144, 184)], fill=skin_d, width=3)
    d.line([(138, 188), (150, 192), (162, 188)], fill=skin_d, width=3)
    # mouth
    d.line([(126, 208), (174, 208)], fill=(164, 96, 78), width=4)
    d.line([(132, 214), (168, 214)], fill=(188, 122, 100), width=2)
    # light stubble on chin and jaw
    rnd = random.Random(42)
    for _ in range(420):
        x = rnd.gauss(150, 34)
        y = rnd.gauss(224, 12)
        if 108 < x < 192 and 202 < y < 244:
            d.point((x, y), fill=(120, 88, 60))
    img = img.filter(ImageFilter.GaussianBlur(0.7))
    return img.resize((w, h))


def hologram(size=76):
    """A round iridescent seal: concentric pastel rings and a star."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = size / 2
    rings = [(255, 170, 190), (255, 214, 150), (190, 235, 170),
             (150, 210, 240), (190, 170, 240), (255, 170, 190)]
    for i, c in enumerate(rings):
        r = size / 2 - 2 - i * (size / 2 - 6) / len(rings)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=c + (165,), width=3)
    r = size * 0.16
    star = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        star.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(star, fill=(255, 226, 120, 200))
    return img


# --------------------------------------------------------------------------
# Data-page furniture
# --------------------------------------------------------------------------
def field(d, x, y, w, label, value, vfont=None, vsize=15):
    """One labelled field with its hairline rule; returns the next row's y."""
    d.text((x, y), label, font=F(SANS_B, 9), fill=LABEL)
    d.text((x, y + 12), value, font=vfont or F(SANS_B, vsize), fill=INK)
    d.line([(x, y + 36), (x + w, y + 36)], fill=RULE, width=1)
    return y + 46


def signature(d, x, y):
    """The holder's ink signature: a tall looped 'M', a running hand, a flourish."""
    ink = (30, 42, 96)
    # the big initial loop
    loop = []
    for t_i in range(25):
        t = t_i / 24 * 6.283
        loop.append((x + 14 + 7 * math.sin(t), y + 14 - 11 * math.cos(t) + t * 1.1))
    d.line(loop, fill=ink, width=2)
    # running strokes, uneven like a real hand
    pts = [(x + 18, y + 22)]
    for dx, dy in ((10, -12), (9, 9), (8, -8), (10, 6), (7, -10), (11, 4),
                  (8, -5), (12, 2), (9, -7), (13, 1)):
        px, py = pts[-1]
        pts.append((px + dx, py + dy))
    d.line(pts, fill=ink, width=2)
    # underline flourish with a final flick
    d.line([(x + 12, y + 27), (x + 96, y + 24), (x + 128, y + 14)], fill=ink, width=1)
    d.ellipse([x + 104, y + 4, x + 107, y + 7], fill=ink)


def fee_stamp(size=(218, 62)):
    """Fiscal stamp: the passport fee, paid in dinars."""
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    red = (168, 34, 44, 235)
    d.rounded_rectangle([3, 3, size[0] - 3, size[1] - 3], 6, outline=red, width=3)
    d.rounded_rectangle([8, 8, size[0] - 8, size[1] - 8], 4, outline=red, width=1)
    centred(d, size[0] / 2, 10, "PRISTOJBA PLAĆENA", F(STAMP_F, 15), red)
    centred(d, size[0] / 2, 32, "FEE PAID · 120 DIN", F(STAMP_R, 13), red)
    return img


# --------------------------------------------------------------------------
# Border stamps and the visa sticker (right page)
# --------------------------------------------------------------------------
def _ink_wear(img, seed, holes=260):
    """Knock speckles out of a stamp so it reads as ink, not print."""
    rnd = random.Random(seed)
    px = img.load()
    w, h = img.size
    for _ in range(holes):
        x = rnd.randrange(w)
        y = rnd.randrange(h)
        r, g, b, a = px[x, y]
        if a:
            px[x, y] = (r, g, b, int(a * rnd.uniform(0.1, 0.55)))
    return img


def rect_stamp(country, post, kind, date, code, colour, seed, size=(238, 118)):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = colour + (232,)
    d.rounded_rectangle([3, 3, size[0] - 3, size[1] - 3], 9, outline=c, width=4)
    d.rounded_rectangle([10, 10, size[0] - 10, size[1] - 10], 6, outline=c, width=1)
    centred(d, size[0] / 2, 15, country, F(STAMP_F, 16), c)
    centred(d, size[0] / 2, 36, post, F(STAMP_R, 10.5), c)
    dated = f"→  {date}" if kind.startswith("ULAZ") else f"{date}  ←"
    centred(d, size[0] / 2, 54, dated, F(STAMP_F, 17), c)
    centred(d, size[0] / 2, 80, kind, F(STAMP_F, 11), c)
    centred(d, size[0] / 2, 97, code, F(STAMP_R, 9), c)
    return _ink_wear(img, seed)


def oval_stamp(country, post, kind, date, code, colour, seed, size=(252, 128)):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = colour + (232,)
    d.ellipse([3, 3, size[0] - 3, size[1] - 3], outline=c, width=4)
    d.ellipse([10, 10, size[0] - 10, size[1] - 10], outline=c, width=1)
    centred(d, size[0] / 2, 20, country, F(STAMP_F, 15), c)
    centred(d, size[0] / 2, 40, post, F(STAMP_R, 10.5), c)
    centred(d, size[0] / 2, 58, date, F(STAMP_F, 16), c)
    centred(d, size[0] / 2, 80, kind, F(STAMP_F, 10.5), c)
    centred(d, size[0] / 2, 96, code, F(STAMP_R, 9), c)
    return _ink_wear(img, seed)


def paste_rot(base, tile, cx, cy, angle):
    rot = tile.rotate(angle, expand=True, resample=Image.BICUBIC)
    base.paste(rot, (int(cx - rot.width / 2), int(cy - rot.height / 2)), rot)


def visa_sticker(size=(292, 208)):
    """Talmere tourist visa, issued in Ostrev before the July 2022 trip."""
    w, h = size
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bg = (238, 233, 214, 255)
    d.rounded_rectangle([1, 1, w - 1, h - 1], 10, fill=bg, outline=(120, 110, 70, 255), width=2)
    img.paste(guilloche(size, 31), (0, 0), guilloche(size, 31))
    d = ImageDraw.Draw(img)
    violet = (74, 32, 110, 255)
    d.rectangle([1, 1, w - 1, 34], fill=(84, 44, 128, 255))
    d.text((12, 8), "VISA", font=F(STAMP_F, 17), fill=(246, 242, 230))
    tr = d.textlength("TALMERE", font=F(STAMP_F, 15))
    d.text((w - 12 - tr, 9), "TALMERE", font=F(STAMP_F, 15), fill=(246, 242, 230))
    rows = [
        ("VRIJEDI / VALID FOR", "TALMERE"),
        ("IME / NAME", "KOVAČ MIRAN"),
        ("PASOŠ / PASSPORT", "048821736"),
        ("VRSTA / TYPE", "TURIST · TOURIST — SINGLE"),
        ("IZDANO / ISSUED", "OSTREV · 14 JUN 2022"),
        ("VRIJEDI / VALID", "01 JUL 2022 — 30 SEP 2022"),
    ]
    y = 46
    for lab, val in rows:
        d.text((12, y), lab, font=F(SANS_B, 8.5), fill=(110, 100, 80))
        d.text((118, y - 2), val, font=F(SANS_B, 11.5), fill=(30, 26, 44))
        y += 19
    d.line([(12, y + 2), (w - 12, y + 2)], fill=(150, 140, 110), width=1)
    d.text((12, y + 8), "UVJETI / CONDITIONS:", font=F(SANS_B, 9), fill=violet)
    d.text((12, y + 22), "TOURIST ONLY · NOT VALID FOR EMPLOYMENT", font=F(SANS_B, 10), fill=violet)
    d.text((12, y + 36), "FERRY ENTRY VIA SENEŽ ONLY", font=F(SANS_B, 10), fill=violet)
    d.text((w - 74, h - 42), "No 0771204", font=F(MONO, 10), fill=(110, 100, 80))
    return img


# --------------------------------------------------------------------------
# The two pages
# --------------------------------------------------------------------------
def data_page():
    x0, y0, x1, y1 = LP
    img = paper(LP, PAPER_D, 7)
    d = ImageDraw.Draw(img)
    # header: arms + state name
    arms = coat_of_arms((62, 74))
    img.paste(arms, (26, 18), arms)
    d = ImageDraw.Draw(img)
    centred(d, 268, 22, "REPUBLIKA VELMARA", F(SERIF_B, 26), INK)
    centred(d, 268, 56, "REPUBLIC OF VELMARA", F(SANS_B, 12), (70, 76, 88), tracking=4)
    centred(d, 268, 78, "PASOŠ · PASSPORT", F(SANS_B, 10.5), LABEL, tracking=3)
    d.line([(24, 104), (464, 104)], fill=RULE, width=1)
    # document row
    d.text((24, 112), "TIP / TYPE", font=F(SANS_B, 9), fill=LABEL)
    d.text((24, 124), "P", font=F(SANS_B, 16), fill=INK)
    d.text((92, 112), "KOD / CODE", font=F(SANS_B, 9), fill=LABEL)
    d.text((92, 124), "VLM", font=F(SANS_B, 16), fill=INK)
    d.text((196, 112), "BROJ PASOŠA / PASSPORT No", font=F(SANS_B, 9), fill=LABEL)
    d.text((196, 123), DOC_NO, font=F(MONO_B, 16), fill=INK)
    # portrait
    photo = portrait()
    img.paste(photo.resize((150, 190)), (24, 152))
    d = ImageDraw.Draw(img)
    d.rectangle([24, 152, 174, 342], outline=(120, 124, 120), width=1)
    holo = hologram(72)
    img.paste(holo, (140, 296), holo)
    d = ImageDraw.Draw(img)
    # fields right of the portrait
    fx, fw = 192, 272
    y = field(d, fx, 148, fw, "PREZIME / SURNAME", "KOVAČ")
    y = field(d, fx, y, fw, "IME / GIVEN NAMES", "MIRAN JOSIP")
    y = field(d, fx, y, fw, "DRŽAVLJANSTVO / NATIONALITY", "VELMARAN · VELMARSKO")
    y = field(d, fx, y, fw, "DATUM ROĐENJA / DATE OF BIRTH", "14 MAR 1989")
    # signature under the portrait
    d.text((24, 352), "POTPIS / SIGNATURE", font=F(SANS_B, 9), fill=LABEL)
    signature(d, 24, 366)
    d.line([(24, 398), (174, 398)], fill=RULE, width=1)
    # full-width rows
    y = 414
    y = field(d, 24, y, 210, "MJESTO ROĐENJA / PLACE OF BIRTH", "OSTREV")
    field(d, 254, 414, 210, "SPOL / SEX", "M · MUŠKI")
    y = field(d, 24, y, 210, "DATUM IZDAVANJA / DATE OF ISSUE", "03 JUN 2021")
    field(d, 254, 414 + 46, 210, "VRIJEDI DO / DATE OF EXPIRY", "03 JUN 2031")
    y = field(d, 24, y, 440, "IZDAVAČ / AUTHORITY", "MINISTARSTVO UNUTARNJIH POSLOVA · OSTREV")
    d.text((24, y - 2), "OSOBNI BROJ / PERSONAL No", font=F(SANS_B, 9), fill=LABEL)
    d.text((24, y + 10), PERSONAL, font=F(MONO, 13), fill=INK)
    # ghost image (secondary portrait, a standard security feature)
    ghost = portrait().resize((58, 74)).convert("RGBA")
    ghost.putalpha(70)
    img.paste(ghost, (404, y - 4), ghost)
    d = ImageDraw.Draw(img)
    # fiscal fee stamp in the clear band above the microtext
    paste_rot(img, fee_stamp(), 252, 600, -4)
    d = ImageDraw.Draw(img)
    # microtext line, then the machine-readable zone
    micro = "REPUBLIKA VELMARA ★ " * 6
    d.text((24, 636), micro, font=F(SANS, 6.5), fill=(110, 116, 110))
    l1, l2 = mrz_lines()
    d.text((24, 650), l1, font=F(MONO, 17), fill=(20, 22, 26))
    d.text((24, 674), l2, font=F(MONO, 17), fill=(20, 22, 26))
    d.text((452, 12), "2", font=F(SANS_B, 11), fill=LABEL)
    return img


def perforated_number(text, colour=(110, 108, 100)):
    """The document number as laser-perforated dot-matrix digits."""
    tile = Image.new("L", (230, 34), 0)
    td = ImageDraw.Draw(tile)
    td.text((2, 2), text, font=F(MONO_B, 26), fill=255)
    out = Image.new("RGBA", tile.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(out)
    px = tile.load()
    for gy in range(0, 34, 3):
        for gx in range(0, 230, 3):
            if any(px[min(gx + dx, 229), min(gy + dy, 33)] > 90
                   for dx in (0, 1, 2) for dy in (0, 1, 2)):
                od.ellipse([gx, gy, gx + 1.8, gy + 1.8], fill=colour + (255,))
    return out


def visas_page():
    img = paper(RP, PAPER_V, 19)
    d = ImageDraw.Draw(img)
    # perforated document number along the top edge
    perf = perforated_number(DOC_NO)
    img.paste(perf, (24, 6), perf)
    d = ImageDraw.Draw(img)
    centred(d, 244, 34, "VIZE · VISAS", F(SERIF_B, 19), INK, tracking=2)
    d.text((452, 30), "7", font=F(SANS_B, 11), fill=LABEL)
    d.line([(24, 66), (464, 66)], fill=RULE, width=1)
    # large pale arms watermark in the middle of the page
    wm = coat_of_arms((210, 252), pale=True)
    img.paste(wm, (139, 230), wm)
    d = ImageDraw.Draw(img)
    # the Talmere visa sticker, centred under the header
    paste_rot(img, visa_sticker(), 244, 176, -1.0)
    # travel history in reading order: Dravia by land, Talmere by ferry,
    # Dravia again — every stamp inside the passport's validity
    paste_rot(img, rect_stamp("DRAVIA", "GRANIČNI PRIJELAZ BREZOVICA", "ULAZ · ENTRY",
                              "17 SEP 2021", "BREZOVICA · POST 04", (32, 65, 143), 5),
              134, 348, 2.0)
    paste_rot(img, rect_stamp("DRAVIA", "GRANIČNI PRIJELAZ BREZOVICA", "IZLAZ · EXIT",
                              "26 SEP 2021", "BREZOVICA · POST 04", (150, 30, 40), 9),
              354, 348, -2.4)
    paste_rot(img, oval_stamp("TALMERE", "LUKA SENEŽ · FERRY PORT", "ULAZ · ENTRY",
                              "02 JUL 2022", "SENEŽ · BERTH 2", (106, 42, 143), 13),
              134, 472, 1.4)
    paste_rot(img, oval_stamp("TALMERE", "LUKA SENEŽ · FERRY PORT", "IZLAZ · EXIT",
                              "21 JUL 2022", "SENEŽ · BERTH 2", (106, 42, 143), 17),
              354, 472, -1.8)
    paste_rot(img, rect_stamp("DRAVIA", "GRANIČNI PRIJELAZ BREZOVICA", "ULAZ · ENTRY",
                              "09 MAY 2024", "BREZOVICA · POST 04", (32, 65, 143), 21),
              134, 596, -2.0)
    paste_rot(img, rect_stamp("DRAVIA", "GRANIČNI PRIJELAZ BREZOVICA", "IZLAZ · EXIT",
                              "11 MAY 2024", "BREZOVICA · POST 04", (150, 30, 40), 25),
              354, 596, 1.8)
    d = ImageDraw.Draw(img)
    d.text((24, 664),
           "Ova je stranica namijenjena vizama i graničnim pečatima · "
           "This page is reserved for visas and border stamps",
           font=F(SANS_I, 9), fill=LABEL)
    return img


def main():
    spread = Image.new("RGB", (W, H), (44, 47, 51))
    d = ImageDraw.Draw(spread)
    # soft shadow under the open book
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([22, 24, 1018, 716], 6, fill=(0, 0, 0, 120))
    shadow = shadow.filter(ImageFilter.GaussianBlur(7))
    spread.paste(shadow, (0, 0), shadow)
    left = data_page()
    right = visas_page()
    spread.paste(left, (LP[0], LP[1]))
    spread.paste(right, (RP[0], RP[1]))
    d = ImageDraw.Draw(spread)
    for rect in (LP, RP):
        d.rectangle(rect, outline=(96, 98, 96), width=1)
    # centre gutter shading
    for i in range(9):
        a = int(46 * (1 - i / 9))
        d.line([(LP[2] + 1 + i, LP[1]), (LP[2] + 1 + i, LP[3])], fill=(70, 72, 70))
        d.line([(RP[0] - 1 - i, RP[1]), (RP[0] - 1 - i, RP[3])], fill=(70, 72, 70))
    spread.save("entry.png", optimize=True)
    print("entry.png", spread.size)


if __name__ == "__main__":
    main()
