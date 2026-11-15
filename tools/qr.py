"""Minimal QR Code encoder (byte mode, error-correction level M, versions 1-5). Returns an SVG string."""
# (total codewords, ec codewords per block, blocks, data codewords per block, alignment centre)
VERS = {1: (26, 10, 1, 16, None), 2: (44, 16, 1, 28, 18), 3: (70, 26, 1, 44, 22),
        4: (100, 18, 2, 32, 26), 5: (134, 24, 2, 43, 30)}

EXP, LOG = [0] * 512, [0] * 256
_x = 1
for _i in range(255):
    EXP[_i] = _x; LOG[_x] = _i
    _x <<= 1
    if _x & 0x100: _x ^= 0x11D
for _i in range(255, 512): EXP[_i] = EXP[_i - 255]

def gmul(a, b): return 0 if a == 0 or b == 0 else EXP[LOG[a] + LOG[b]]

def rs_generator(n):
    g = [1]
    for i in range(n):
        ng = [0] * (len(g) + 1)
        for j, c in enumerate(g):
            ng[j] ^= c
            ng[j + 1] ^= gmul(c, EXP[i])
        g = ng
    return g

def rs_remainder(data, n):
    g = rs_generator(n)
    rem = [0] * n
    for b in data:
        f = b ^ rem[0]
        rem = rem[1:] + [0]
        for i in range(n): rem[i] ^= gmul(g[i + 1], f)
    return rem

def encode(text):
    raw = text.encode('utf-8')
    for v, (total, ecn, nb, dpb, _) in VERS.items():
        if len(raw) <= nb * dpb - 2: break
    else:
        raise ValueError('text too long for built-in QR encoder')
    total, ecn, nb, dpb, align = VERS[v]
    bits = '0100' + format(len(raw), '08b') + ''.join(format(b, '08b') for b in raw)
    cap = nb * dpb * 8
    bits += '0' * min(4, cap - len(bits))
    bits += '0' * (-len(bits) % 8)
    data = [int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)]
    pad = [0xEC, 0x11]
    while len(data) < nb * dpb: data.append(pad[(len(data) - len(bits) // 8) % 2])
    blocks = [data[i * dpb:(i + 1) * dpb] for i in range(nb)]
    ecs = [rs_remainder(b, ecn) for b in blocks]
    out = [b[i] for i in range(dpb) for b in blocks] + [e[i] for i in range(ecn) for e in ecs]
    stream = ''.join(format(c, '08b') for c in out)

    size = 17 + 4 * v
    mod = [[False] * size for _ in range(size)]
    fn = [[False] * size for _ in range(size)]
    def setf(x, y, dark):
        mod[y][x] = dark; fn[y][x] = True
    for i in range(size):
        setf(6, i, i % 2 == 0); setf(i, 6, i % 2 == 0)
    for cx, cy in ((3, 3), (size - 4, 3), (3, size - 4)):
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                x, y = cx + dx, cy + dy
                if 0 <= x < size and 0 <= y < size:
                    d = max(abs(dx), abs(dy)); setf(x, y, d not in (2, 4))
    if align:
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                setf(align + dx, align + dy, max(abs(dx), abs(dy)) != 1)
    for i in range(9):
        fn[8][i] = fn[i][8] = True
    for i in range(8):
        fn[8][size - 1 - i] = fn[size - 1 - i][8] = True
    setf(8, size - 8, True)

    i = 0
    for right in range(size - 1, 0, -2):
        if right == 6: right = 5
        for vert in range(size):
            for j in range(2):
                x = right - j
                y = size - 1 - vert if ((right + 1) & 2) == 0 else vert
                if not fn[y][x] and i < len(stream):
                    mod[y][x] = stream[i] == '1'; i += 1

    masks = [lambda x, y: (x + y) % 2 == 0, lambda x, y: y % 2 == 0, lambda x, y: x % 3 == 0,
             lambda x, y: (x + y) % 3 == 0, lambda x, y: (x // 3 + y // 2) % 2 == 0,
             lambda x, y: x * y % 2 + x * y % 3 == 0, lambda x, y: (x * y % 2 + x * y % 3) % 2 == 0,
             lambda x, y: ((x + y) % 2 + x * y % 3) % 2 == 0]

    def build(m):
        g = [row[:] for row in mod]
        for y in range(size):
            for x in range(size):
                if not fn[y][x] and masks[m](x, y): g[y][x] = not g[y][x]
        d = m  # EC level M = 00
        rem = d
        for _ in range(10): rem = (rem << 1) ^ ((rem >> 9) * 0x537)
        fb = ((d << 10) | rem) ^ 0x5412
        bit = lambda k: (fb >> k) & 1 == 1
        for k in range(6): g[k][8] = bit(k)
        g[7][8] = bit(6); g[8][8] = bit(7); g[8][7] = bit(8)
        for k in range(9, 15): g[8][14 - k] = bit(k)
        for k in range(8): g[8][size - 1 - k] = bit(k)
        for k in range(8, 15): g[size - 15 + k][8] = bit(k)
        g[size - 8][8] = True
        return g

    def penalty(g):
        p = 0
        for rows in (g, [list(c) for c in zip(*g)]):
            for r in rows:
                run = 1
                for k in range(1, size):
                    if r[k] == r[k - 1]: run += 1
                    else:
                        if run >= 5: p += 3 + run - 5
                        run = 1
                if run >= 5: p += 3 + run - 5
                s = ''.join('1' if c else '0' for c in r)
                p += 40 * (s.count('10111010000') + s.count('00001011101'))
        for y in range(size - 1):
            for x in range(size - 1):
                if g[y][x] == g[y][x + 1] == g[y + 1][x] == g[y + 1][x + 1]: p += 3
        dark = sum(c for r in g for c in r)
        p += 10 * (abs(dark * 20 - size * size * 10) // (size * size))
        return p

    best = min((build(m) for m in range(8)), key=penalty)
    return best

def to_svg(text, fg='#08080C', bg='none', quiet=4):
    g = encode(text); n = len(g); dim = n + 2 * quiet
    path = ''.join(f'M{x + quiet} {y + quiet}h1v1h-1z' for y in range(n) for x in range(n) if g[y][x])
    bgrect = '' if bg == 'none' else f'<rect width="{dim}" height="{dim}" fill="{bg}"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {dim} {dim}" shape-rendering="crispEdges" '
            f'role="img" aria-label="QR code">{bgrect}<path fill="{fg}" d="{path}"/></svg>')

if __name__ == '__main__':
    import sys
    print(to_svg(sys.argv[1], bg='#fff'))
