"""Builds tools/wiring_pdf.html, the source of EasyCliq-Wiring-Diagram.pdf.

Page 1 is the illustrated wiring picture; page 2 is the tick-off wire list.
Run this, then print the HTML to PDF with Edge:

    python tools/gen_wiring_pdf.py
    msedge --headless=new --no-pdf-header-footer         --print-to-pdf=EasyCliq-Wiring-Diagram.pdf tools/wiring_pdf.html
"""
import os
from html import escape

S = os.path.dirname(os.path.abspath(__file__))

# wire colours
RED, BLK, PUR = "#D62F22", "#1B1B1B", "#6A4FD6"
STEP, DIR, EN = "#0B8F78", "#E07B00", "#C2388B"
MBLUE, MRED, MBLK, MGRN = "#2F66CC", "#D62F22", "#1B1B1B", "#23893F"
BROWN, MAINS_BLUE, EARTH = "#8A5526", "#2F66CC", "#23893F"


def esc(s):
    return escape(s, quote=True)


def t(x, y, s, size=11, fill="#16201C", anchor="start", weight=400, halo=False, extra=""):
    h = ' stroke="#fff" stroke-width="3.5" paint-order="stroke" stroke-linejoin="round"' if halo else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}" dominant-baseline="central"{h}{extra}>{esc(s)}</text>')


def w(d, col, width=4, halo=True):
    out = ""
    if halo:
        out += f'<path d="{d}" fill="none" stroke="#fff" stroke-width="{width+3.5}" stroke-linecap="round" stroke-linejoin="round"/>'
    out += f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>'
    return out


# ------------------------------------------------------------ breadboard grid
def X(c):
    return 385 + 15 * (c - 1)


TP, TM = 310, 325
ROW = dict(j=355, i=370, h=385, g=400, f=415, e=460, d=475, c=490, b=505, a=520)
BP, BM = 550, 565


def breadboard():
    b = []
    b.append('<defs><pattern id="holes" x="377.5" y="302.5" width="15" height="15" patternUnits="userSpaceOnUse">'
             '<rect x="5.5" y="5.5" width="4" height="4" rx="0.8" fill="#9C9A90"/></pattern>'
             '<pattern id="mesh" x="0" y="0" width="9" height="9" patternUnits="userSpaceOnUse">'
             '<circle cx="4.5" cy="4.5" r="2.4" fill="#7E858B"/></pattern></defs>')
    b.append('<rect x="365" y="290" width="970" height="295" rx="8" fill="#F4F2EA" stroke="#BDB9AC" stroke-width="1.5"/>')
    b.append('<rect x="369" y="431" width="962" height="14" fill="#E0DDD2"/>')
    for y, h in ((302.5, 30), (347.5, 75), (452.5, 75), (542.5, 30)):
        b.append(f'<rect x="377.5" y="{y}" width="945" height="{h}" fill="url(#holes)"/>')
    for y, col in ((299, "#E0574C"), (336, "#4C7FE0"), (539, "#E0574C"), (576, "#4C7FE0")):
        b.append(f'<path d="M380 {y} H1320" stroke="{col}" stroke-width="1.6"/>')
    for y, s, col in ((TP, "+", "#D62F22"), (TM, "−", "#2F66CC"), (BP, "+", "#D62F22"), (BM, "−", "#2F66CC")):
        b.append(t(372, y, s, 11, col, "middle", 700))
    b.append(t(680, 281, "top rails:  + = 24 V   ·   − = GND", 11, "#56645E", "middle", 600))
    b.append(t(1040, 602, "bottom rails:  + = 3.3 V   ·   − = GND", 11, "#56645E", "middle", 600))
    return "".join(b)


def driver(x0, name):
    b = []
    b.append(f'<rect x="{x0-9}" y="391" width="123" height="93" rx="3" fill="#4B2E83" stroke="#2E1B57" stroke-width="1"/>')
    for k in range(8):
        for y in (ROW["g"], ROW["d"]):
            b.append(f'<rect x="{x0+15*k-3}" y="{y-3}" width="6" height="6" rx="1" fill="#E3C05A" stroke="#8A6F1E" stroke-width="0.6"/>')
    # tan capacitor, sense resistors, pot (EN corner), heatsink on the chip
    b.append(f'<rect x="{x0+1}" y="410" width="20" height="9" rx="1.5" fill="#C9AE7C"/>')
    b.append(f'<rect x="{x0+1}" y="424" width="16" height="7" rx="1" fill="#2B2B2B"/>')
    b.append(f'<rect x="{x0+1}" y="435" width="16" height="7" rx="1" fill="#2B2B2B"/>')
    b.append(f'<circle cx="{x0+11}" cy="456" r="8" fill="#C9CCD1" stroke="#6B7075" stroke-width="1"/>')
    b.append(f'<path d="M{x0+6} 456 H{x0+16} M{x0+11} 451 V461" stroke="#4A4F54" stroke-width="1.6"/>')
    b.append(f'<rect x="{x0+40}" y="412" width="60" height="50" rx="2" fill="#D5D8DC" stroke="#7C8288" stroke-width="1"/>')
    for i in range(1, 6):
        b.append(f'<path d="M{x0+40+10*i} 413 V461" stroke="#9AA0A6" stroke-width="1.4"/>')
    b.append(t(x0 + 70, 437, name, 17, "#16201C", "middle", 700,
               extra=' stroke="#D5D8DC" stroke-width="4" paint-order="stroke"'))
    return "".join(b)


def cap(x0, label=False):
    cx, cy = x0 + 7.5, 372
    b = [f'<circle cx="{cx}" cy="{cy}" r="12" fill="#1F3A6B" stroke="#0F1F3D" stroke-width="1"/>',
         f'<path d="M{cx+5} {cy-10.9} A12 12 0 0 1 {cx+5} {cy+10.9} Z" fill="#C9D3E6"/>',
         t(cx + 8.3, cy, "−", 10, "#1F3A6B", "middle", 700),
         f'<circle cx="{cx}" cy="{cy}" r="3.5" fill="none" stroke="#6F86B5" stroke-width="1"/>']
    if label:
        b.append(t(x0 - 12, 372, "100 µF", 11, "#16201C", "end", 600, True))
    return "".join(b)


def motor(x0, name):
    cx = x0 + 52.5
    b = []
    b.append(t(cx, 76, f"{name} motor", 14, "#16201C", "middle", 700))
    b.append(f'<rect x="{cx-65}" y="86" width="130" height="130" rx="12" fill="#C9CDD2" stroke="#6B7075" stroke-width="1.5"/>')
    b.append(f'<rect x="{cx-65}" y="102" width="130" height="98" fill="#2A2C2F" opacity="0.10"/>')
    for dx in (-50, 50):
        for dy in (-50, 50):
            b.append(f'<circle cx="{cx+dx}" cy="{151+dy}" r="5" fill="#5A5F65" stroke="#3A3E43" stroke-width="1"/>')
    b.append(f'<circle cx="{cx}" cy="151" r="33" fill="#B3B8BE" stroke="#6B7075" stroke-width="1.5"/>')
    b.append(f'<circle cx="{cx}" cy="151" r="9" fill="#ECEEF0" stroke="#4A4F54" stroke-width="1.5"/>')
    b.append(f'<path d="M{cx-6} 144.5 H{cx+6}" stroke="#4A4F54" stroke-width="1.5"/>')
    b.append(f'<rect x="{x0+20}" y="208" width="65" height="12" rx="2" fill="#F2F2EE" stroke="#8C8C86" stroke-width="1"/>')
    return "".join(b)


def psu():
    b = []
    b.append(t(30, 72, "24 V power supply", 14, "#16201C", "start", 700))
    b.append('<rect x="30" y="84" width="300" height="146" rx="3" fill="#C4C9CE" stroke="#6B7075" stroke-width="1.5"/>')
    b.append('<rect x="40" y="92" width="280" height="86" fill="url(#mesh)"/>')
    b.append('<rect x="44" y="120" width="70" height="40" fill="#F2D22E" stroke="#8A7611" stroke-width="0.8"/>')
    b.append(t(79, 133, "side switch", 9, "#3A3205", "middle", 600))
    b.append(t(79, 147, "set to 220 V", 9.5, "#3A3205", "middle", 700))
    b.append('<rect x="30" y="230" width="300" height="40" fill="#2B2E31" stroke="#16181A" stroke-width="1"/>')
    names = ["L", "N", "⏚", "−V", "−V", "+V", "+V"]
    for i, n in enumerate(names):
        x = 56 + 34 * i
        b.append(t(x, 215, n, 12, "#16201C", "middle", 700, extra=' stroke="#C4C9CE" stroke-width="4" paint-order="stroke"'))
        b.append(f'<circle cx="{x}" cy="250" r="11" fill="#D9DCDF" stroke="#7C8288" stroke-width="1"/>')
        b.append(f'<path d="M{x-6} 250 H{x+6} M{x} 244 V256" stroke="#4A4F54" stroke-width="1.8"/>')
        if i:
            b.append(f'<path d="M{x-17} 232 V268" stroke="#4A4E52" stroke-width="2"/>')
    b.append('<circle cx="292" cy="250" r="4.5" fill="#35C759"/>')
    b.append('<circle cx="313" cy="250" r="9" fill="#E8862A" stroke="#8A4A0C" stroke-width="1"/>')
    b.append('<path d="M308 245 L318 255" stroke="#5A2F06" stroke-width="1.6"/>')
    b.append('<path d="M38 209 V204 H142 V209 M174 209 V204 H278 V209" fill="none" stroke="#16201C" stroke-width="1"/>')
    b.append(t(90, 196, "230 V in", 10.5, "#A3241B", "middle", 700, extra=' stroke="#C4C9CE" stroke-width="4" paint-order="stroke"'))
    b.append(t(226, 196, "24 V out", 10.5, "#16201C", "middle", 700, extra=' stroke="#C4C9CE" stroke-width="4" paint-order="stroke"'))
    # mains cord
    b.append('<path d="M0 384 H66 Q90 384 90 362 V352" fill="none" stroke="#3A3E43" stroke-width="13" stroke-linecap="round"/>')
    b.append(w("M82 352 C82 318, 56 322, 56 262", BROWN))
    b.append(w("M90 352 V262", MAINS_BLUE))
    b.append(w("M98 352 C98 318, 124 322, 124 262", EARTH))
    b.append(t(10, 405, "cord to wall socket (230 V)", 10.5, "#56645E", "start", 600))
    b.append(t(150, 352, "brown → L", 10.5, BROWN, "start", 700))
    b.append(t(150, 367, "blue → N", 10.5, MAINS_BLUE, "start", 700))
    b.append(t(150, 382, "green → ⏚ (earth)", 10.5, EARTH, "start", 700))
    # 24 V out to the top rails
    b.append(w(f"M226 262 V{TP} H{X(1)}", RED))
    b.append(w(f"M192 262 V{TM} H{X(1)}", BLK))
    return "".join(b)


LEFT_TOP = ["VIN", "GND", "D13", "D12", "D14", "D27", "D26", "D25", "D33", "D32", "D35", "D34", "VN", "VP", "EN"]
LEFT_BOT = ["3V3", "GND", "D15", "D2", "D4", "RX2", "TX2", "D5", "D18", "D19", "D21", "RX0", "TX0", "D22", "D23"]
E0, EP = 630, 26
ETOP, EBOT = 705, 835


def EX(name, row):
    return E0 + EP * (LEFT_TOP if row == "top" else LEFT_BOT).index(name)


def esp32():
    used_top = {"D13": STEP, "D27": DIR, "D26": STEP, "D25": DIR}
    used_bot = {"3V3": PUR, "GND": BLK, "D21": EN, "D22": DIR, "D23": STEP}
    b = []
    b.append('<rect x="596" y="690" width="468" height="160" rx="6" fill="#15181B" stroke="#000" stroke-width="1"/>')
    # USB socket + plug
    b.append('<rect x="586" y="752" width="34" height="36" rx="2" fill="#C9CCD1" stroke="#6B7075" stroke-width="1"/>')
    b.append('<rect x="548" y="756" width="40" height="28" rx="3" fill="#4A4F54"/>')
    b.append(t(590, 742, "USB to laptop", 10.5, "#16201C", "end", 600, True))
    # buttons, regulator, USB chip
    for y, n in ((736, "EN"), (794, "BOOT")):
        b.append(f'<rect x="628" y="{y}" width="16" height="10" rx="2" fill="#C9CCD1" stroke="#6B7075" stroke-width="0.8"/>')
    b.append('<rect x="668" y="752" width="26" height="26" rx="2" fill="#2B2E31" stroke="#55595E" stroke-width="0.8"/>')
    b.append('<rect x="712" y="748" width="22" height="34" rx="2" fill="#2B2E31" stroke="#55595E" stroke-width="0.8"/>')
    # RF module + antenna
    b.append('<rect x="826" y="732" width="230" height="76" rx="2" fill="#0B0D0F" stroke="#3A3E43" stroke-width="1"/>')
    b.append('<rect x="832" y="738" width="158" height="64" rx="2" fill="#C9CCD1" stroke="#7C8288" stroke-width="1"/>')
    b.append(t(911, 762, "ESP-WROOM-32", 12, "#2B2E31", "middle", 700))
    b.append(t(911, 780, "ESP32-B (motion)", 10, "#2B2E31", "middle", 600))
    b.append('<path d="M1002 744 H1046 V754 H1010 V764 H1046 V774 H1010 V784 H1046 V796" fill="none" stroke="#C9A227" stroke-width="2.4"/>')
    for i, n in enumerate(LEFT_TOP):
        x = E0 + EP * i
        col = used_top.get(n)
        b.append(f'<rect x="{x-3.5}" y="{ETOP-3.5}" width="7" height="7" rx="1" fill="#E3C05A" stroke="#8A6F1E" stroke-width="0.6"/>')
        b.append(t(x, ETOP + 15, n, 9.5, "#fff" if col else "#7C8288", "middle", 700 if col else 400))
        if col:
            b.append(f'<circle cx="{x}" cy="{ETOP}" r="8" fill="none" stroke="{col}" stroke-width="2"/>')
    for i, n in enumerate(LEFT_BOT):
        x = E0 + EP * i
        col = used_bot.get(n) if not (n == "GND" and False) else None
        b.append(f'<rect x="{x-3.5}" y="{EBOT-3.5}" width="7" height="7" rx="1" fill="#E3C05A" stroke="#8A6F1E" stroke-width="0.6"/>')
        b.append(t(x, EBOT - 15, n, 9.5, "#fff" if col else "#7C8288", "middle", 700 if col else 400))
        if col:
            ring = "#E8E8E8" if col == BLK else col
            b.append(f'<circle cx="{x}" cy="{EBOT}" r="8" fill="none" stroke="{ring}" stroke-width="2"/>')
    return "".join(b)


def resistor(x1, y1, x2, y2):
    """4.7k from (x1,y1) hole, body vertical in column x2, down to (x2,y2) hole."""
    b = [w(f"M{x1} {y1} H{x2} V{y1+10} M{x2} {y2-12} V{y2}", "#8C8C86", 2.2)]
    b.append(f'<rect x="{x2-5}" y="{y1+8}" width="10" height="{y2-y1-20}" rx="4" fill="#D9C39A" stroke="#8A7243" stroke-width="0.8"/>')
    for k, col in enumerate(("#E0C21B", "#7A3FA0", "#C0392B", "#C9A227")):
        b.append(f'<rect x="{x2-5}" y="{y1+13+7*k}" width="10" height="2.6" fill="{col}"/>')
    return "".join(b)


def inset():
    b = []
    b.append('<rect x="30" y="424" width="300" height="548" rx="8" fill="#F7F9F8" stroke="#CBD5D0" stroke-width="1.2"/>')
    b.append(t(44, 445, "One driver, chip side up", 13.5, "#16201C", "start", 700))
    b.append(t(44, 462, "pin names are printed on the back of the board", 9.5, "#56645E"))
    px = lambda k: 68 + 32 * k
    b.append('<rect x="50" y="492" width="260" height="116" rx="4" fill="#4B2E83" stroke="#2E1B57" stroke-width="1"/>')
    top = ["VMOT", "GND", "2B", "1B", "1A", "2A", "FLT", "GND"]
    bot = ["EN", "M0", "M1", "M2", "RST", "SLP", "STEP", "DIR"]
    tcol = [RED, BLK, MRED, MBLK, MBLUE, MGRN, "#9AA0A6", BLK]
    bcol = [EN, "#9AA0A6", "#9AA0A6", "#9AA0A6", PUR, PUR, STEP, DIR]
    for k in range(8):
        for y, names, cols, ly in ((504, top, tcol, 481), (596, bot, bcol, 619)):
            b.append(f'<rect x="{px(k)-5}" y="{y-5}" width="10" height="10" rx="1.5" fill="#E3C05A" stroke="#8A6F1E" stroke-width="0.8"/>')
            b.append(t(px(k), ly, names[k], 10, cols[k], "middle", 700))
    b.append('<rect x="56" y="520" width="34" height="13" rx="2" fill="#C9AE7C"/>')
    b.append('<circle cx="86" cy="566" r="13" fill="#C9CCD1" stroke="#6B7075" stroke-width="1"/>')
    b.append('<path d="M78 566 H94 M86 558 V574" stroke="#4A4F54" stroke-width="2"/>')
    b.append(t(86, 543, "pot", 9, "#E8E2F5", "middle", 600))
    b.append('<rect x="150" y="518" width="112" height="64" rx="3" fill="#D5D8DC" stroke="#7C8288" stroke-width="1"/>')
    for i in range(1, 8):
        b.append(f'<path d="M{150+14*i} 519 V581" stroke="#9AA0A6" stroke-width="1.6"/>')
    b.append(t(206, 550, "heatsink", 10, "#2B2E31", "middle", 600, extra=' stroke="#D5D8DC" stroke-width="4" paint-order="stroke"'))
    rows = [
        ("VMOT", RED, "24 V rail"),
        ("GND", BLK, "GND rail (both GND pins)"),
        ("2B", MRED, "motor red"),
        ("1B", MBLK, "motor black"),
        ("1A", MBLUE, "motor blue"),
        ("2A", MGRN, "motor green"),
        ("FLT", "#7C8288", "leave empty"),
        ("EN", EN, "next driver's EN, and ESP32 D21"),
        ("M0 M1 M2", "#7C8288", "leave empty"),
        ("RST + SLP", PUR, "join together, then 3.3 V rail"),
        ("STEP", STEP, "ESP32 (table below)"),
        ("DIR", DIR, "ESP32 (table below)"),
    ]
    y = 650
    for name, col, dest in rows:
        b.append(f'<rect x="44" y="{y-4.5}" width="9" height="9" rx="2" fill="{col}"/>')
        b.append(t(60, y, name, 10.5, "#16201C", "start", 700))
        b.append(t(128, y, dest, 10.5, "#16201C"))
        y += 17
    b.append(t(44, y + 4, "100 µF capacitor: across VMOT and its GND,", 10, "#56645E", "start", 600))
    b.append(t(44, y + 18, "stripe (−) on the GND side.", 10, "#56645E", "start", 600))
    y += 42
    b.append(f'<path d="M44 {y-10} H316" stroke="#CBD5D0" stroke-width="1"/>')
    b.append(t(120, y + 4, "STEP pin", 10, STEP, "middle", 700))
    b.append(t(210, y + 4, "DIR pin", 10, DIR, "middle", 700))
    for i, (n, s, d) in enumerate((("J1", "D13", "D27"), ("J2", "D26", "D25"), ("J3", "D23", "D22"))):
        yy = y + 22 + 17 * i
        b.append(t(52, yy, n, 11, "#16201C", "start", 700))
        b.append(t(120, yy, s, 11, "#16201C", "middle", 600))
        b.append(t(210, yy, d, 11, "#16201C", "middle", 600))
    return "".join(b)


def page1():
    b = []
    b.append(t(30, 30, "EasyCliq core wiring", 24, "#16201C", "start", 700))
    b.append(t(30, 53, "24 V supply · 3 DRV8825 drivers · 3 NEMA17 motors · ESP32-B", 11.5, "#56645E"))
    b.append(t(1370, 30, "Wire with the plug OUT of the wall.", 12, "#A3241B", "end", 700))
    b.append(t(1370, 48, "Plug motors in or out only with the power off.", 11, "#56645E", "end", 600))
    b.append(breadboard())
    b.append(psu())
    drivers = [(X(6), "J1"), (X(28), "J2"), (X(50), "J3")]
    for x0, name in drivers:
        b.append(motor(x0, name))
    # ---- power-side jumpers, motor wires
    for x0, name in drivers:
        for k, col in zip(range(2, 6), (MRED, MBLK, MBLUE, MGRN)):
            b.append(w(f"M{x0+15*k} {ROW['j']} V219", col))
        b.append(w(f"M{x0} {ROW['j']} C{x0-11} 345, {x0-11} 322, {x0} {TP}", RED))
        b.append(w(f"M{x0+15} {ROW['j']} V{TM}", BLK))
        b.append(w(f"M{x0+105} {ROW['j']} V{TM}", BLK))
    # GND rail bridge, right end
    b.append(w(f"M{X(63)} {TM} C{X(63)+48} {TM+40}, {X(63)+48} {BM-40}, {X(63)} {BM}", BLK))
    b.append(t(1362, 445, "GND", 10, "#16201C", "start", 700))
    b.append(t(1362, 458, "link", 10, "#16201C", "start", 700))
    # ---- logic side
    for x0, name in drivers:
        b.append(w(f"M{x0+60} {ROW['c']} Q{x0+67.5} {ROW['c']+11} {x0+75} {ROW['c']}", PUR, 3.5))
        b.append(w(f"M{x0+75} {ROW['a']} V{BP}", PUR))
    a, b_, c_ = drivers[0][0], drivers[1][0], drivers[2][0]
    # EN chain
    b.append(w(f"M{a} {ROW['b']} L{a+8} 512.5 H{b_-8} L{b_} {ROW['b']}", EN, 3.5))
    b.append(w(f"M{b_} {ROW['a']} L{b_+8} 512.5 H{c_-8} L{c_} {ROW['b']}", EN, 3.5))
    # 4.7k resistor: J1 EN column -> 3.3 V rail
    b.append(resistor(a, ROW["c"], a - 15, BP))
    b.append(t(a - 26, 516, "4.7 kΩ", 11, "#16201C", "end", 600, True))
    # ---- wires to the ESP32
    # J1: STEP -> D13, DIR -> D27 ; J2: STEP -> D26, DIR -> D25 (top row)
    b.append(w(f"M{a+90} {ROW['a']} V638 H{EX('D13','top')} V{ETOP}", STEP))
    b.append(w(f"M{a+105} {ROW['a']} V616 H{EX('D27','top')} V{ETOP}", DIR))
    b.append(w(f"M{b_+90} {ROW['a']} V616 H{EX('D26','top')} V{ETOP}", STEP))
    b.append(w(f"M{b_+105} {ROW['a']} V638 H{EX('D25','top')} V{ETOP}", DIR))
    # J3 goes round the right end to the bottom row
    b.append(w(f"M{c_+90} {ROW['a']} V872 H{EX('D23','bot')} V{EBOT}", STEP))
    b.append(w(f"M{c_+105} {ROW['a']} V888 H{EX('D22','bot')} V{EBOT}", DIR))
    # from the left, under the board: 3V3, GND, EN
    b.append(w(f"M{X(8)} {BP} V872 H{EX('3V3','bot')} V{EBOT}", PUR))
    b.append(w(f"M{X(7)} {BM} V888 H{EX('GND','bot')} V{EBOT}", BLK))
    b.append(w(f"M{a} {ROW['a']} V904 H{EX('D21','bot')} V{EBOT}", EN))
    b.append(esp32())
    # components on top of wires
    for i, (x0, name) in enumerate(drivers):
        b.append(driver(x0, name))
        b.append(cap(x0, label=(i == 0)))
    b.append(inset())
    # legend
    lx, ly = 470, 950
    items = [(RED, "24 V"), (BLK, "GND"), (PUR, "3.3 V"), (STEP, "STEP"), (DIR, "DIR"), (EN, "EN")]
    for col, name in items:
        b.append(f'<path d="M{lx} {ly} H{lx+26}" stroke="{col}" stroke-width="4" stroke-linecap="round"/>')
        b.append(t(lx + 34, ly, name, 11, "#16201C", "start", 600))
        lx += 34 + len(name) * 7 + 26
    b.append(t(lx + 6, ly, "motor wires: red · black · blue · green, same order as at the motor's white plug", 11, "#56645E"))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 990" '
            f'font-family="Segoe UI, Arial, sans-serif">{"".join(b)}</svg>')


PAGE2 = """
<div class="p2">
  <div class="eyebrow">EasyCliq · core wiring</div>
  <h1>Wire list</h1>
  <p class="sub">Tick each wire as you place it. Plug out of the wall the whole time.</p>
  <div class="cols">
    <div>
      <h2>Power</h2>
      <table>
        <tr><td class="bx"><i></i></td><td>Side switch on the supply</td><td class="to">set to <b>220 V</b></td></tr>
        <tr><td class="bx"><i></i></td><td>Cord brown / blue / green</td><td class="to">L / N / ⏚</td></tr>
        <tr><td class="bx"><i></i></td><td>Supply <b>+V</b></td><td class="to">top <b>+</b> rail (red)</td></tr>
        <tr><td class="bx"><i></i></td><td>Supply <b>−V</b></td><td class="to">top <b>−</b> rail (black)</td></tr>
        <tr><td class="bx"><i></i></td><td>Top <b>−</b> rail</td><td class="to">bottom <b>−</b> rail (black)</td></tr>
        <tr><td class="bx"><i></i></td><td>Gap in a rail's red/blue line?</td><td class="to">jumper across each gap</td></tr>
      </table>

      <h2>Each driver <span>tick J1, J2, J3</span></h2>
      <table class="three">
        <tr><td class="bx3"><i></i><i></i><i></i></td><td>Driver across the gap, pot bottom-left</td><td class="to">VMOT row on top</td></tr>
        <tr><td class="bx3"><i></i><i></i><i></i></td><td><b>VMOT</b> column</td><td class="to">top <b>+</b> rail</td></tr>
        <tr><td class="bx3"><i></i><i></i><i></i></td><td><b>GND</b> column next to VMOT</td><td class="to">top <b>−</b> rail</td></tr>
        <tr><td class="bx3"><i></i><i></i><i></i></td><td><b>100 µF</b> across VMOT and that GND</td><td class="to">stripe on GND side</td></tr>
        <tr><td class="bx3"><i></i><i></i><i></i></td><td><b>GND</b> column next to FLT</td><td class="to">top <b>−</b> rail</td></tr>
        <tr><td class="bx3"><i></i><i></i><i></i></td><td><b>RST</b> column</td><td class="to"><b>SLP</b> column</td></tr>
        <tr><td class="bx3"><i></i><i></i><i></i></td><td><b>SLP</b> column</td><td class="to">bottom <b>+</b> rail (3.3 V)</td></tr>
        <tr><td class="bx3"><i></i><i></i><i></i></td><td><b>STEP</b></td><td class="to">J1 <b>D13</b> · J2 <b>D26</b> · J3 <b>D23</b></td></tr>
        <tr><td class="bx3"><i></i><i></i><i></i></td><td><b>DIR</b></td><td class="to">J1 <b>D27</b> · J2 <b>D25</b> · J3 <b>D22</b></td></tr>
      </table>
    </div>
    <div>
      <h2>Shared</h2>
      <table>
        <tr><td class="bx"><i></i></td><td>J1 <b>EN</b> column</td><td class="to">J2 <b>EN</b> column</td></tr>
        <tr><td class="bx"><i></i></td><td>J2 <b>EN</b> column</td><td class="to">J3 <b>EN</b> column</td></tr>
        <tr><td class="bx"><i></i></td><td>J1 <b>EN</b> column</td><td class="to">ESP32 <b>D21</b></td></tr>
        <tr><td class="bx"><i></i></td><td><b>4.7 kΩ</b> from J1 EN column</td><td class="to">bottom <b>+</b> rail (3.3 V)</td></tr>
        <tr><td class="bx"><i></i></td><td>ESP32 <b>3V3</b></td><td class="to">bottom <b>+</b> rail</td></tr>
        <tr><td class="bx"><i></i></td><td>ESP32 <b>GND</b></td><td class="to">bottom <b>−</b> rail</td></tr>
        <tr><td class="bx"><i></i></td><td>ESP32 USB</td><td class="to">laptop</td></tr>
      </table>

      <h2>First power-on</h2>
      <ol>
        <li><b>Motors not plugged in yet.</b> Plug the supply in and plug the ESP32 into the laptop. The multimeter should read about 24 V on the top rails and 3.3 V on the bottom rails.</li>
        <li><b>Set each driver to 0.55 V.</b> Black probe on a GND rail, red probe on the metal top of the driver's pot. 0 V means the driver is asleep: check RST and SLP reach the 3.3 V rail.</li>
        <li><b>Power off and unplug.</b> Stick a heatsink on each chip. Plug in the motors: red → 2B, black → 1B, blue → 1A, green → 2A.</li>
        <li><b>Power on.</b> Upload <span class="m">stepper_test.ino</span>, open the Serial Monitor at 115200 and type <span class="m">a</span>. All three motors turn once.</li>
      </ol>
      <p class="fix"><b>A motor buzzes but doesn't turn:</b> its two coils are mixed up. Power off, then check that red + black are one pair and blue + green the other.</p>
      <p class="fix"><b>Nothing moves at all:</b> check RST/SLP reach the 3.3 V rail, the GND rails are linked, and the 24 V rail really reads 24 V.</p>
    </div>
  </div>
</div>
"""

CSS = """
@page { size: A4 landscape; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body { font: 10.5pt/1.45 "Segoe UI", Arial, sans-serif; color: #16201C; }
.p1 { width: 297mm; height: 209.5mm; page-break-after: always; overflow: hidden; }
.p1 svg { width: 297mm; height: 210mm; display: block; }
.p2 { padding: 11mm 16mm 8mm; }
.eyebrow { font: 600 7.5pt/1 Consolas, monospace; letter-spacing: .14em; text-transform: uppercase; color: #0B7F6B; }
h1 { font: 700 22pt/1.1 "Segoe UI", Arial, sans-serif; margin: 5pt 0 2pt; }
.sub { color: #56645E; margin: 0 0 10pt; }
.cols { display: grid; grid-template-columns: 1fr 1fr; gap: 14mm; }
h2 { font: 600 8pt/1 Consolas, monospace; letter-spacing: .1em; text-transform: uppercase; color: #56645E;
     margin: 10pt 0 3pt; padding-bottom: 4pt; border-bottom: 1.2pt solid #16201C; }
h2 span { float: right; text-transform: none; letter-spacing: 0; font: 8.5pt "Segoe UI", Arial, sans-serif; }
table { width: 100%; border-collapse: collapse; }
td { padding: 4.4pt 0; border-bottom: .6pt solid #CBD5D0; vertical-align: middle; }
td.bx { width: 18pt; } td.bx3 { width: 42pt; white-space: nowrap; }
td i { display: inline-block; width: 9pt; height: 9pt; border: 1pt solid #16201C; border-radius: 1.5pt; margin-right: 3pt; vertical-align: middle; }
td.to { text-align: right; color: #2A3531; }
ol { margin: 6pt 0 0; padding-left: 16pt; }
li { margin-bottom: 3.5pt; }
.m { font-family: Consolas, monospace; font-size: .95em; }
.fix { margin: 5pt 0 0; font-size: 9.5pt; color: #3A4540; }
"""

html = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>EasyCliq Wiring Diagram</title>'
        f'<style>{CSS}</style></head><body><div class="p1">{page1()}</div>{PAGE2}</body></html>')
open(os.path.join(S, "wiring_pdf.html"), "w", encoding="utf-8").write(html)
print("ok", len(html))
