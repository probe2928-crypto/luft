#!/usr/bin/env python3
"""Synthesised sound design for the LUFT Seoul ad (no outside audio at all).

  python3 src/sound.py  ->  assets/audio/luft-seoul-mix.wav (48 kHz stereo, 20 s)

Cue times come from the GSAP timeline in src/template.html; each hit lands one frame
(33 ms) after its picture. Edit CUES below when the timeline moves.
"""
import numpy as np, pathlib
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

import sys
TARGET_RMS = float(sys.argv[1]) if len(sys.argv) > 1 else -15.5
SR = 48000; DUR = 20.0; N = int(SR * DUR); F = 1 / 30
rng = np.random.default_rng(20261102)
out = np.zeros((N, 2))

def t_(d): return np.arange(int(d * SR)) / SR
def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], "band", fs=SR, output="sos"), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x)
def lp(x, f, o=2): return sosfilt(butter(o, f, "low", fs=SR, output="sos"), x)
def add(x, at, gain=1.0, pan=0.0):
    i = int((at) * SR); x = x[: max(0, N - i)]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    out[i : i + len(x), 0] += x * gain * l * 1.414; out[i : i + len(x), 1] += x * gain * r * 1.414
def env(n, a, d):  # attack / exponential decay
    t = np.arange(n) / SR; e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / d); return e

# ---- pad bed: A major add9 → D lydian from the hero/seal → back to A for the end card
def pad(freqs, start, end, gain, fade_in=1.2, fade_out=1.0):
    t = t_(end - start); x = np.zeros_like(t)
    for k, f in enumerate(freqs):
        for det in (-0.12, 0.12):
            ph = rng.uniform(0, 2 * np.pi)
            x += np.sin(2 * np.pi * (f + det) * t + ph) + 0.22 * np.sin(4 * np.pi * (f + det) * t + ph)
    x *= (0.78 + 0.22 * np.sin(2 * np.pi * 0.16 * t))
    x = lp(x, 2200); e = np.minimum(1, t / fade_in) * np.minimum(1, (t[-1] - t) / fade_out)
    return x * e * gain / len(freqs)
add(pad([110, 164.8, 220, 246.9, 329.6, 440], 0.0, 11.0, 0.17, 1.4, 0.4), 0.0)
add(pad([73.4, 146.8, 220, 293.7, 329.6, 415.3, 587.3], 10.7, 17.25, 0.17, 0.6, 0.5), 10.7)
add(pad([55, 110, 164.8, 220, 277.2, 329.6, 659.3], 17.1, 20.0, 0.18, 0.25, 0.9), 17.1)

# ---- soft pulse (100 BPM) under the store flow + cards, again under the map
def kick(g=1.0):
    t = t_(0.35); f = 46 + 54 * np.exp(-t * 32); ph = 2 * np.pi * np.cumsum(f) / SR
    x = (np.sin(ph) + 0.3 * np.sin(2 * ph)) * env(len(t), 0.004, 0.12)
    return lp(x, 900) * g
beat = 60 / 100
for k in range(int((9.75 - 2.52) / beat)):
    add(kick(0.36 if k % 2 == 0 else 0.26), 2.52 + F + k * beat)
for k in range(int((15.2 - 13.0) / beat)):
    add(kick(0.28), 13.0 + F + k * beat)
for k in range(int((6.9 - 2.82) / beat)):  # soft shaker off-beats while the phone is up
    n = rng.standard_normal(int(0.05 * SR)); add(bp(n, 5000, 11000) * env(len(n), 0.002, 0.016), 2.82 + beat / 2 + k * beat, 0.035, 0.3 * (-1) ** k)

# ---- particles: airy shimmer converging into the mark, warm bloom when it resolves
n = rng.standard_normal(int(1.3 * SR)); t = t_(1.3)
sh = bp(n, 3000, 9000) * np.minimum(1, t / 0.9) * np.exp(-np.maximum(0, t - 1.0) / 0.22)
add(sh, 0.0, 0.09)
for k in range(30):
    at = 0.35 + k * 0.024 + rng.uniform(0, 0.02); f0 = rng.uniform(2600, 5200); tt = t_(0.06)
    add(np.sin(2 * np.pi * f0 * tt) * env(len(tt), 0.001, 0.014), at, 0.028, rng.uniform(-0.6, 0.6))
tt = t_(1.6); add(lp(np.sin(2 * np.pi * 82.4 * tt) + 0.5 * np.sin(2 * np.pi * 164.8 * tt) + 0.2 * np.sin(2 * np.pi * 329.6 * tt), 1000) * env(len(tt), 0.03, 0.5), 1.04 + F, 0.34)
tt = t_(1.2); add(np.sin(2 * np.pi * 1318.5 * tt) * env(len(tt), 0.004, 0.35) * 0.5 + np.sin(2 * np.pi * 1975.5 * tt) * env(len(tt), 0.004, 0.25) * 0.25, 1.06 + F, 0.07)

# ---- whooshes (varied)
def whoosh(d, lo, hi, up=True, g=1.0):
    t = t_(d); n = rng.standard_normal(len(t)); fc = np.geomspace(lo, hi, len(t)) if up else np.geomspace(hi, lo, len(t))
    y = np.zeros_like(t); bands = np.geomspace(min(lo, hi), max(lo, hi), 7)
    for b0, b1 in zip(bands[:-1], bands[1:]):
        w = np.exp(-((np.log(fc) - np.log((b0 * b1) ** 0.5)) ** 2) / 0.18); y += bp(n, b0, b1) * w
    e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.6
    return y * e * g
for at, d, lo, hi, up, g, pan in [
    (2.2, 0.5, 300, 4000, True, 0.26, 0.0),      # logo push-through
    (2.5, 0.6, 2200, 300, False, 0.14, 0.2),     # phone rises in
    (6.9, 0.6, 2500, 250, False, 0.22, -0.2),    # phone drops away
    (7.12, 0.8, 200, 2400, True, 0.15, 0.3),     # cards fan out
    (9.3, 0.5, 600, 4500, True, 0.18, 0.0),      # cards gather
    (9.8, 1.1, 180, 1400, True, 0.12, -0.3),     # hero swing
    (10.95, 0.6, 250, 2000, True, 0.12, 0.0),    # macro push
    (12.38, 0.5, 2000, 300, False, 0.13, 0.0),   # pull back
    (12.75, 0.5, 3500, 250, False, 0.2, 0.0),    # dive into the map
    (15.98, 0.3, 500, 3500, True, 0.1, 0.0),     # copy swap
    (16.95, 0.55, 250, 3500, True, 0.2, 0.0),    # iris flood
]:
    add(whoosh(d, lo, hi, up, 1.0), at, g, pan)

# ---- UI: taps, chip, keys, button, toast
def tick(f=2200, d=0.03, g=1.0):
    t = t_(d); n = rng.standard_normal(len(t)); return (bp(n, f * 0.6, f * 1.6) + 0.6 * np.sin(2 * np.pi * f * t)) * env(len(t), 0.0008, d / 5) * g
add(tick(1800, 0.05), 3.62 + F, 0.22); add(tick(2400, 0.03), 4.5 + F, 0.17); add(tick(2000, 0.04), 5.18 + F, 0.15)
add(tick(3000, 0.025), 5.34 + F, 0.14, 0.1); add(tick(2800, 0.025), 5.52 + F, 0.14, -0.1)
add(tick(1500, 0.06), 6.36 + F, 0.24)
tt = t_(0.35); add((np.sin(2 * np.pi * 880 * tt) * 0.6 + np.sin(2 * np.pi * 1318.5 * tt) * 0.3) * env(len(tt), 0.004, 0.09), 6.48 + F, 0.13)

# ---- seal: soft air before, then a crafted press — wood thock + paper + low warmth (no boom)
t = t_(0.3); n = rng.standard_normal(len(t)); add(bp(n, 1500, 6000) * (t / 0.3) ** 2, 11.55, 0.06)
t = t_(0.9)
thock = bp(rng.standard_normal(len(t)), 250, 1100) * env(len(t), 0.0008, 0.035)
body = lp(np.sin(2 * np.pi * 120 * t) + 0.4 * np.sin(2 * np.pi * 240 * t), 600) * env(len(t), 0.002, 0.09)
paper = bp(rng.standard_normal(len(t)), 2500, 8000) * env(len(t), 0.001, 0.05)
sub = np.sin(2 * np.pi * 55 * t) * env(len(t), 0.01, 0.35)
add(thock * 0.9 + body * 0.6 + paper * 0.25 + sub * 0.45, 11.85 + F, 0.62)
tt = t_(1.6); add(np.sin(2 * np.pi * 1760 * tt) * env(len(tt), 0.005, 0.5) * 0.35 + np.sin(2 * np.pi * 2637 * tt) * env(len(tt), 0.005, 0.35) * 0.2, 11.9 + F, 0.06)

# ---- map: travelling light, pin lands
t = t_(1.3); ph = 2 * np.pi * np.cumsum(np.geomspace(440, 880, len(t))) / SR
add(np.sin(ph) * np.sin(np.pi * t / 1.3) ** 2 * 0.3 + bp(rng.standard_normal(len(t)), 2000, 6000) * np.sin(np.pi * t / 1.3) ** 2 * 0.15, 13.15, 0.12)
add(tick(1200, 0.08), 14.5 + F, 0.24)
tt = t_(0.8); add(np.sin(2 * np.pi * 1318.5 * tt) * env(len(tt), 0.004, 0.25), 14.5 + F, 0.08)

# ---- copy: underline shimmer; end card: warm wordmark hit + CTA tick
n = rng.standard_normal(int(0.5 * SR)); t = t_(0.5); add(bp(n, 4000, 10000) * np.sin(np.pi * t / 0.5) ** 2, 16.55, 0.07)
tt = t_(1.6); add(lp(np.sin(2 * np.pi * 55 * tt) + 0.6 * np.sin(2 * np.pi * 110 * tt) + 0.3 * np.sin(2 * np.pi * 220 * tt), 1200) * env(len(tt), 0.006, 0.55), 17.28 + F, 0.42)
add(tick(1600, 0.05), 17.8 + F, 0.16)

# ---- room: short plate on everything
ir_t = t_(0.9); ir = rng.standard_normal((len(ir_t), 2)) * np.exp(-ir_t / 0.22)[:, None]
ir[:, 0] = hp(ir[:, 0], 250); ir[:, 1] = hp(ir[:, 1], 250)
wet = np.stack([fftconvolve(out[:, c], ir[:, c])[:N] for c in range(2)], 1)
mix = out + wet * (0.18 / np.abs(ir).sum(0).max() * 40)

# master: fade tail, gentle limit, normalise towards ~ -15 LUFS-ish RMS, peak ≤ -1 dBFS
tail = np.ones(N); i0 = int((DUR - 0.7) * SR); tail[i0:] = np.linspace(1, 0, N - i0) ** 1.5
mix *= tail[:, None]
rms = np.sqrt(np.mean(mix ** 2)); mix *= 10 ** (TARGET_RMS / 20) / max(rms, 1e-9)
mix = np.tanh(mix * 1.2) / 1.2
mix *= 10 ** (-1.2 / 20) / max(np.abs(mix).max(), 1e-9) if np.abs(mix).max() > 10 ** (-1.2 / 20) else 1
dst = pathlib.Path(__file__).resolve().parent.parent / "assets/audio/luft-seoul-mix.wav"
wavfile.write(dst, SR, (mix * 32767).astype(np.int16))
print("wrote", dst, "peak", round(20 * np.log10(np.abs(mix).max()), 2), "dBFS rms", round(20 * np.log10(np.sqrt(np.mean(mix ** 2))), 2))
