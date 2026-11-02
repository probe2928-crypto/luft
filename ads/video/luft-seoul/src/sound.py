#!/usr/bin/env python3
"""Synthesised sound design for the LUFT Seoul ad (no outside audio at all).

  python3 src/sound.py  ->  assets/audio/luft-seoul-mix.wav (48 kHz stereo, 19 s)

Cue times come from the GSAP timeline in src/template.html; each hit lands one frame
(33 ms) after its picture. Edit CUES below when the timeline moves.
"""
import numpy as np, pathlib
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

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

# ---- pad bed: A major add9 → D lydian after the stamp → back to A for the end card
def pad(freqs, start, end, gain, fade_in=1.2, fade_out=1.0):
    t = t_(end - start); x = np.zeros_like(t)
    for k, f in enumerate(freqs):
        for det in (-0.12, 0.12):
            ph = rng.uniform(0, 2 * np.pi)
            x += np.sin(2 * np.pi * (f + det) * t + ph) + 0.25 * np.sin(4 * np.pi * (f + det) * t + ph)
    x *= (0.75 + 0.25 * np.sin(2 * np.pi * 0.18 * t))
    x = lp(x, 2400); e = np.minimum(1, t / fade_in) * np.minimum(1, (t[-1] - t) / fade_out)
    return x * e * gain / len(freqs)
add(pad([110, 164.8, 220, 246.9, 329.6, 440], 0.0, 10.75, 0.16, 1.6, 0.25), 0.0)
add(pad([146.8, 220, 293.7, 329.6, 415.3, 587.3], 10.6, 17.3, 0.15, 0.25, 0.5), 10.6)
add(pad([110, 164.8, 220, 277.2, 329.6, 659.3], 17.1, 20.0, 0.17, 0.3, 0.9), 17.1)

# ---- soft pulse (100 BPM) under the store flow and the map
def kick(g=1.0):
    t = t_(0.35); f = 48 + 60 * np.exp(-t * 30); ph = 2 * np.pi * np.cumsum(f) / SR
    x = (np.sin(ph) + 0.35 * np.sin(2 * ph)) * env(len(t), 0.003, 0.11)
    return x * g
beat = 60 / 100
for k in range(int((10.25 - 2.45) / beat)):
    add(kick(0.42 if k % 2 == 0 else 0.3), 2.45 + F + k * beat)
for k in range(int((14.8 - 12.35) / beat)):
    add(kick(0.3), 12.35 + F + k * beat)
# shaker on the off-beats while the phone is on screen
for k in range(int((7.0 - 2.75) / beat)):
    n = rng.standard_normal(int(0.06 * SR)); add(hp(n, 6000) * env(len(n), 0.002, 0.018), 2.75 + beat / 2 + k * beat, 0.05, 0.3 * (-1) ** k)

# ---- particles: airy shimmer rising into the mark
n = rng.standard_normal(int(1.5 * SR)); t = t_(1.5)
sh = bp(n, 3000, 9000) * np.minimum(1, t / 1.0) * np.exp(-np.maximum(0, t - 1.15) / 0.25)
add(sh, 0.0, 0.11)
for k in range(26):  # grains as streaks land
    at = 0.25 + k * 0.035 + rng.uniform(0, 0.02); f0 = rng.uniform(2500, 5200); tt = t_(0.05)
    add(np.sin(2 * np.pi * f0 * tt) * env(len(tt), 0.001, 0.012), at, 0.035, rng.uniform(-0.6, 0.6))
# the mark lands: warm body hit
tt = t_(1.2); add(lp(np.sin(2 * np.pi * 82 * tt) + 0.5 * np.sin(2 * np.pi * 164 * tt), 900) * env(len(tt), 0.01, 0.35), 1.18 + F, 0.35)

# ---- whooshes (three takes, varied)
def whoosh(d, lo, hi, up=True, g=1.0):
    t = t_(d); n = rng.standard_normal(len(t)); fc = np.geomspace(lo, hi, len(t)) if up else np.geomspace(hi, lo, len(t))
    # moving band: crossfade 6 static bands along the sweep
    y = np.zeros_like(t); bands = np.geomspace(min(lo, hi), max(lo, hi), 7)
    for b0, b1 in zip(bands[:-1], bands[1:]):
        w = np.exp(-((np.log(fc) - np.log((b0 * b1) ** 0.5)) ** 2) / 0.18); y += bp(n, b0, b1) * w
    e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.6
    return y * e * g
for at, d, lo, hi, up, g, pan in [
    (2.3, 0.55, 300, 4000, True, 0.30, 0.0),     # logo push-through
    (6.95, 0.65, 2500, 250, False, 0.26, -0.2),   # phone drops away
    (7.2, 0.8, 200, 2400, True, 0.18, 0.3),       # cards fan out
    (9.6, 0.5, 600, 5000, True, 0.22, 0.0),       # cards gather
    (11.85, 0.55, 3500, 300, False, 0.24, 0.0),   # seal shrinks into the map
    (14.5, 0.45, 400, 3000, True, 0.18, 0.2),     # map out
    (17, 0.6, 250, 3500, True, 0.24, 0.0),      # iris flood
]:
    add(whoosh(d, lo, hi, up, 1.0), at, g, pan)

# ---- UI: taps, chip, keys, button, toast
def tick(f=2200, d=0.03, g=1.0):
    t = t_(d); n = rng.standard_normal(len(t)); return (bp(n, f * 0.6, f * 1.6) + 0.6 * np.sin(2 * np.pi * f * t)) * env(len(t), 0.0008, d / 5) * g
add(tick(1800, 0.05), 3.72 + F, 0.28); add(tick(2400, 0.03), 4.66 + F, 0.2)
add(tick(3000, 0.025), 5.28 + F, 0.18, 0.1); add(tick(2800, 0.025), 5.5 + F, 0.18, -0.1)
add(tick(1500, 0.06), 6.32 + F, 0.32)
tt = t_(0.25); add((np.sin(2 * np.pi * 660 * tt) * 0.6 + np.sin(2 * np.pi * 990 * tt) * 0.3) * env(len(tt), 0.004, 0.06), 6.45 + F, 0.16)

# ---- stamp: riser → impact
t = t_(0.6); n = rng.standard_normal(len(t))
riser = (hp(n, 1200) * (t / 0.6) ** 2.2) + 0.4 * np.sin(2 * np.pi * np.cumsum(np.geomspace(180, 900, len(t))) / SR) * (t / 0.6) ** 2
add(riser, 10.02, 0.22)
t = t_(1.6); f = 38 + 90 * np.exp(-t * 18); ph = 2 * np.pi * np.cumsum(f) / SR
boom = (np.sin(ph) + 0.4 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph)) * env(len(t), 0.002, 0.38)
crack = bp(rng.standard_normal(len(t)), 900, 7000) * env(len(t), 0.0005, 0.05)
wood = bp(rng.standard_normal(len(t)), 180, 700) * env(len(t), 0.001, 0.09)
add(boom * 0.9 + crack * 0.55 + wood * 0.7, 10.62 + F, 0.85)

# ---- map: pin lands, end card: wordmark hit
add(tick(1200, 0.08), 14.18 + F, 0.3)
tt = t_(1.5); add(lp(np.sin(2 * np.pi * 55 * tt) + 0.6 * np.sin(2 * np.pi * 110 * tt) + 0.3 * np.sin(2 * np.pi * 220 * tt), 1200) * env(len(tt), 0.006, 0.5), 17.36 + F, 0.45)

# ---- room: short plate on everything
ir_t = t_(0.9); ir = rng.standard_normal((len(ir_t), 2)) * np.exp(-ir_t / 0.22)[:, None]
ir[:, 0] = hp(ir[:, 0], 250); ir[:, 1] = hp(ir[:, 1], 250)
wet = np.stack([fftconvolve(out[:, c], ir[:, c])[:N] for c in range(2)], 1)
mix = out + wet * (0.18 / np.abs(ir).sum(0).max() * 40)

# master: fade tail, gentle limit, normalise towards ~ -15 LUFS-ish RMS, peak ≤ -1 dBFS
tail = np.ones(N); i0 = int((DUR - 0.7) * SR); tail[i0:] = np.linspace(1, 0, N - i0) ** 1.5
mix *= tail[:, None]
rms = np.sqrt(np.mean(mix ** 2)); mix *= 10 ** (-17 / 20) / max(rms, 1e-9)
mix = np.tanh(mix * 1.2) / 1.2
mix *= 10 ** (-1.2 / 20) / max(np.abs(mix).max(), 1e-9) if np.abs(mix).max() > 10 ** (-1.2 / 20) else 1
dst = pathlib.Path(__file__).resolve().parent.parent / "assets/audio/luft-seoul-mix.wav"
wavfile.write(dst, SR, (mix * 32767).astype(np.int16))
print("wrote", dst, "peak", round(20 * np.log10(np.abs(mix).max()), 2), "dBFS rms", round(20 * np.log10(np.sqrt(np.mean(mix ** 2))), 2))
