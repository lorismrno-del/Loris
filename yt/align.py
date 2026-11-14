import re, json, subprocess, numpy as np
GAP = 0.8
INTRO = 12.0
cues = []; offset = INTRO + 0.6
parts_info = []
for i in range(1, 5):
    txt = open(f'part{i}.txt').read().replace('\n\n', ' ').strip()
    dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f'p{i}.wav']))
    lines = open(f'sil{i}.txt').read().split('\n')
    sils = []; st = None
    for ln in lines:
        if ln.startswith('silence_start:'): st = float(ln.split()[1])
        elif ln.startswith('silence_end:') and st is not None: sils.append((st, float(ln.split()[1]))); st = None
    sents = [s.strip() for s in re.split(r'(?<=[.?!:])\s+', txt) if s.strip()]
    # speech start/end
    s0 = sils[0][1] if sils and sils[0][0] < 0.05 else 0.0
    s1 = sils[-1][0] if sils and sils[-1][1] > dur - 0.05 else dur
    inner = [(a, b) for a, b in sils if a > s0 + 0.2 and b < s1 - 0.2]
    L = np.array([len(s) for s in sents], float); cum = np.cumsum(L) / L.sum()
    exp = s0 + (s1 - s0) * cum[:-1]
    P = inner; n = len(sents) - 1; m = len(P)
    rate = L.sum() / (s1 - s0)
    INF = 1e9
    # node j: boundary at pause j (1..m); node 0 = start; final = end
    D = np.full((n + 1, m + 2), INF); D[0, 0] = 0; back = {}
    pos_end = lambda j: s0 if j == 0 else P[j - 1][0]
    pos_start = lambda j: s0 if j == 0 else P[j - 1][1]
    for k in range(1, n + 1):
        for j in range(1, m + 1):
            best = INF; arg = None
            for jj in range(0, j):
                if D[k - 1, jj] >= INF: continue
                d = P[j - 1][0] - pos_start(jj)
                c = D[k - 1, jj] + abs(d - L[k - 1] / rate) - 1.5 * min(0.6, P[j - 1][1] - P[j - 1][0])
                if c < best: best = c; arg = jj
            D[k, j] = best; back[(k, j)] = arg
    best = INF; arg = None
    for jj in range(0, m + 1):
        if D[n, jj] >= INF: continue
        c = D[n, jj] + abs((s1 - pos_start(jj)) - L[n] / rate)
        if c < best: best = c; arg = jj
    j = arg; bounds = []
    for k in range(n, 0, -1):
        bounds.append(P[j - 1]); j = back[(k, j)]
    bounds = bounds[::-1]
    starts = [s0] + [b for a, b in bounds]; ends = [a for a, b in bounds] + [s1]
    for s, a, b in zip(sents, starts, ends):
        words = s.split(); chunks = []; cur = ''
        for w in words:
            if len((cur + ' ' + w).strip()) > 46 and cur: chunks.append(cur); cur = w
            else: cur = (cur + ' ' + w).strip()
        if cur: chunks.append(cur)
        if len(chunks) > 1 and len(chunks[-1]) < 12:
            chunks[-2] = chunks[-2] + ' ' + chunks[-1]; chunks.pop()
        tot = sum(len(c) for c in chunks); t = a
        for c in chunks:
            d = (b - a) * len(c) / tot
            cues.append([round(offset + t, 2), round(offset + t + d, 2), c]); t += d
    parts_info.append(dict(i=i, start=offset, dur=dur))
    offset += dur + GAP
for k in range(len(cues) - 1):
    cues[k][1] = min(max(cues[k][1], cues[k][0] + 0.6), cues[k + 1][0] - 0.03)
json.dump(dict(cues=cues, parts=parts_info, total=offset - GAP + 2.0), open('timing.json', 'w'), ensure_ascii=False, indent=0)
print(len(cues), offset)
for c in cues: print(c)
