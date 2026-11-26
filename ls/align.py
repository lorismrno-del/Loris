import re, subprocess, json, sys
import numpy as np
from scipy.signal import find_peaks
PT = []

def nsyl(w):
    w = re.sub(r'[^a-zäöüß]', '', w.lower())
    return max(1, len(re.findall(r'[aeiouyäöü]+', w)))

def peaks(mp3):
    raw = subprocess.run(['ffmpeg','-v','error','-i',mp3,'-ac','1','-ar','16000','-f','s16le','-'],capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    hop = 160; n = len(x) // hop
    e = np.sqrt((x[:n*hop].reshape(n, hop)**2).mean(1) + 1e-9)
    k = np.hanning(9); k /= k.sum(); e = np.convolve(e, k, 'same')
    db = 20*np.log10(e + 1e-9)
    pk, _ = find_peaks(db, distance=int(0.085/0.01), prominence=3.0, height=db.max()-32)
    return list(pk * 0.01)


def silences(mp3, noise=-35, d=0.22):
    out = subprocess.run(['ffmpeg', '-hide_banner', '-i', mp3, '-af', f'silencedetect=noise={noise}dB:d={d}', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', out)]
    en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', out)]
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', mp3],
                               capture_output=True, text=True).stdout)
    sil = []
    for i, s in enumerate(st):
        e = en[i] if i < len(en) else dur
        sil.append((s, e))
    return sil, dur

def split_sentences(text):
    parts = re.split(r'(?<=[.!?])\s+', text.strip().replace('\n', ' '))
    return [p.strip() for p in parts if p.strip()]

def align(mp3, text, extra=()):
    sil, dur = silences(mp3)
    sil = sorted(list(sil) + list(extra))
    PT[:] = peaks(mp3)
    sents = split_sentences(text)
    # speech start / end
    t0 = 0.0
    if sil and sil[0][0] < 0.05:
        t0 = sil[0][1]
    t1 = dur
    if sil and sil[-1][1] >= dur - 0.05:
        t1 = sil[-1][0]
    inner = [s for s in sil if s[0] > t0 + 0.2 and s[1] < t1 - 0.1]
    n = len(sents)
    w = [len(s) + 8 for s in sents]
    tot = sum(w)
    est = []
    acc = 0
    for i in range(n - 1):
        acc += w[i]
        est.append(t0 + (t1 - t0) * acc / tot)
    # DP: choose n-1 silences (increasing) minimizing deviation, favour long silences
    m = len(inner)
    INF = 1e18
    if m < n - 1:
        bounds = [(e, e) for e in est]
    else:
        cost = [[INF] * (m + 1) for _ in range(n)]
        back = [[-1] * (m + 1) for _ in range(n)]
        for j in range(m):
            c = abs((inner[j][0] + inner[j][1]) / 2 - est[0]) - 0.6 * (inner[j][1] - inner[j][0])
            cost[1][j] = c
        for k in range(2, n):
            best = INF; bj = -1
            for j in range(m):
                if j > 0 and cost[k - 1][j - 1] < best:
                    best = cost[k - 1][j - 1]; bj = j - 1
                if best < INF:
                    c = abs((inner[j][0] + inner[j][1]) / 2 - est[k - 1]) - 0.6 * (inner[j][1] - inner[j][0])
                    cost[k][j] = best + c; back[k][j] = bj
        j = min(range(m), key=lambda j: cost[n - 1][j])
        chosen = []
        k = n - 1
        while k >= 1:
            chosen.append(j); j = back[k][j]; k -= 1
        chosen = chosen[::-1]
        bounds = [inner[j] for j in chosen]
    out = []
    starts = [t0] + [b[1] for b in bounds]
    ends = [b[0] for b in bounds] + [t1]
    for i, s in enumerate(sents):
        a, b = starts[i], ends[i]
        words = s.split()
        ns = [nsyl(x) for x in words]
        P = [p for p in PT if a - 0.03 <= p <= b + 0.03]
        S = sum(ns)
        wt = []
        if len(P) >= 2:
            def stime(k):
                f = k * (len(P) - 1) / max(1, S - 1)
                i = int(min(max(f // 1, 0), len(P) - 2)); fr = f - i
                return P[i] * (1 - fr) + P[i + 1] * fr
            acc = 0
            for k, x in enumerate(words):
                st_ = a if k == 0 else max(a, stime(acc) - 0.08)
                wt.append([round(st_, 3), 0, x]); acc += ns[k]
            for k in range(len(wt)):
                wt[k][1] = round(wt[k + 1][0] if k + 1 < len(wt) else b, 3)
        else:
            tt = a; tot = sum(ns)
            for k, x in enumerate(words):
                d = (b - a) * ns[k] / tot
                wt.append([round(tt, 3), round(tt + d, 3), x]); tt += d
        out.append({'text': s, 'start': round(a, 3), 'end': round(b, 3), 'words': wt})
    return {'duration': dur, 'sentences': out}

if __name__ == '__main__':
    mp3, txt, js = sys.argv[1:4]
    ex = [tuple(map(float, x.split('-'))) for x in sys.argv[4:]]
    r = align(mp3, open(txt).read(), ex)
    json.dump(r, open(js, 'w'), ensure_ascii=False, indent=1)
    for i, s in enumerate(r['sentences']):
        print(i, s['start'], s['end'], s['text'][:60])
