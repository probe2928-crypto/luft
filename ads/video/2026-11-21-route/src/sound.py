"""ROUTE 광고 사운드 — 전부 numpy 합성(외부 음원 0). python3 src/sound.py [목표 RMS dB]"""
import sys, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
DUR = 15.5
N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(11)
F = 1 / 30  # 화면 동작 +1프레임


def put(sig, t, pan=0.0, g=1.0):
    if t >= 3.3: t -= 0.8  # r2: 히어로 홀드 0.8초 단축
    i = int((t + F) * SR)
    if i >= N: return
    s = sig[: N - i] * g
    L[i:i + len(s)] += s * np.sqrt(0.5 * (1 - pan)) * 1.414
    R[i:i + len(s)] += s * np.sqrt(0.5 * (1 + pan)) * 1.414


def bp(x, lo, hi, o=2):
    return sosfilt(butter(o, [lo, hi], btype='band', fs=SR, output='sos'), x)


def lp(x, f, o=2):
    return sosfilt(butter(o, f, btype='low', fs=SR, output='sos'), x)


def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)


def flap(g=1.0, bright=1.0):
    n = int(.03 * SR)
    x = rng.standard_normal(n) * env(n, .0005, .004)
    x = bp(x, 1800 * bright, 7000)
    body = np.sin(2 * np.pi * (900 + rng.uniform(-80, 80)) * np.arange(n) / SR) * env(n, .0003, .006) * .35
    return (x + body) * g


def tick(g=1.0, f=2600):
    n = int(.04 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) * env(n, .0003, .006) + bp(rng.standard_normal(n), 3000, 9000) * env(n, .0002, .002) * .5) * g


def bell(f, d=1.4, g=1.0):
    n = int(d * 2.5 * SR); t = np.arange(n) / SR
    s = sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t / (d / (1 + m * .6))) for m, a in [(1, 1), (2.0, .35), (3.01, .12), (4.2, .05)])
    return s * np.minimum(1, t / .004) * g


def whoosh(d, g=1.0, up=True):
    n = int(d * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n)
    shape = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2 if not up else (t / d) ** 2.2 * (1 - np.exp(-(d - t) / .03))
    x = bp(x, 400, 5000) * shape
    return lp(x, 6000) * g


def thump(g=1.0, f0=70):
    n = int(.5 * SR); t = np.arange(n) / SR
    f = f0 + 60 * np.exp(-t / .03)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .002, .14) * g


def paper(g=1.0):
    n = int(.12 * SR)
    return bp(rng.standard_normal(n), 1500, 6000) * env(n, .002, .03) * g


def pad(t0, t1, freqs, g=1.0, fade_in=.8, fade_out=.8):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR
    s = np.zeros(n)
    for f in freqs:
        for det in (-.12, .12):
            s += np.sin(2 * np.pi * f * (1 + det / 100) * t + rng.uniform(0, 6))
            s += .25 * np.sin(2 * np.pi * 2 * f * (1 + det / 100) * t)
    s = lp(s, 1800) / len(freqs)
    e = np.minimum(1, t / fade_in) * np.minimum(1, (t1 - t0 - t) / fade_out)
    put(s * e * g, t0 - F)


# 0.0–0.75 출발 안내판 플랩 (0프레임부터)
t = 0.0
while t < .72:
    dens = 1 - t / .9
    put(flap(.5 + .5 * rng.random()), t, rng.uniform(-.6, .6), .55)
    t += rng.uniform(.006, .02) / max(dens, .2)
for k in range(3): put(flap(1.0, 1.1), .57 + k * .05, -.1 + k * .1, .8)  # LIS 착지
# BOARDING 차임 2음
put(bell(659.3, 1.0, .5), .56, -.15); put(bell(523.3, 1.2, .5), .80, .15)
# 푸시 휘시 → 매치 컷 툭 + 종이
put(whoosh(.36, .6), .54)
put(thump(.9, 62), .9); put(paper(.35), .9)
# 패드 (케이스 장면)
pad(.95, 10.7, [174.6, 220.0, 261.6, 329.6], .16, 1.2, .3)
# 소프트 펄스 100BPM 3.6–11.3
beat = 60 / 100
b = 3.6
while b < 11.0:
    put(thump(.28, 55), b)
    n = int(.05 * SR); put(bp(rng.standard_normal(n), 6000, 12000) * env(n, .001, .012) * .12, b + beat / 2, .3)
    b += beat
# 카메라 휘시
for tt, d in [(1.0, .5), (3.4, .7), (5.0, .7), (6.7, .6), (8.15, .7), (8.85, 1.2)]:
    put(whoosh(d, .22, up=False), tt, rng.uniform(-.3, .3))
# 공항 코드 플랩 3단어 x 3글자
for t0 in (3.75, 4.2, 4.65):
    for k in range(3): put(flap(.9, 1.2), t0 + k * .03 + .05, -.2 + k * .2, .75)
# 이름 지우기·타이핑
for i in range(9): put(tick(.35, 2200), 5.55 + i * .04, .1)
for i in range(8): put(tick(.5, 2600 + (i % 3) * 180), 5.95 + i * .07, -.05 + (i % 2) * .1)
# 날짜 숫자 플랩
for k in (3, 5, 6, 8, 9): put(flap(.8, 1.3), 7.12 + (k - 3) * .012 + .08, (k - 6) * .08, .7)
# 글로스 스윕 종
put(bell(1046.5, .9, .25), 9.45, .2); put(bell(1568, .7, .12), 9.52, -.2)
# 엔드: 피치 컷 히트 + 새 화성
put(thump(.7, 58), 11.4); put(bell(523.3, 1.6, .22), 11.4, -.1); put(bell(659.3, 1.6, .18), 11.42, .1); put(bell(784, 1.8, .16), 11.45)
pad(11.4, 16.25, [196.0, 246.9, 293.7, 392.0], .13, .4, 1.6)
put(tick(.4, 1800), 12.35); put(tick(.4, 2000), 12.42); put(tick(.55, 2400), 12.52)

# 짧은 플레이트 리버브
def verb(x):
    ir_n = int(1.2 * SR); t = np.arange(ir_n) / SR
    ir = rng.standard_normal(ir_n) * np.exp(-t / .35); ir = lp(ir, 5000); ir /= np.abs(ir).sum() / 8
    from scipy.signal import fftconvolve
    return fftconvolve(x, ir)[:len(x)]
L2 = L + .18 * verb(L); R2 = R + .18 * verb(R)
target = float(sys.argv[1]) if len(sys.argv) > 1 else -17.0
mix = np.stack([L2, R2], 1)
rms = 20 * np.log10(np.sqrt(np.mean(mix ** 2)) + 1e-9)
mix *= 10 ** ((target - rms) / 20)
pk = np.abs(mix).max()
lim = 10 ** (-1.2 / 20)
if pk > lim: mix = np.tanh(mix / lim) * lim
wavfile.write('assets/audio/route-mix.wav', SR, (np.clip(mix, -1, 1) * 32767).astype(np.int16))
print('rms', round(rms, 1), '-> target', target, 'peak', round(20 * np.log10(np.abs(mix).max()), 2))
