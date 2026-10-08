#!/usr/bin/env python3
"""產生示範資料：兩個音源 (A、B) 加上雜訊混合成一條訊號，並計算頻譜。

只用 Python 標準函式庫 (math / cmath / csv / random)，不需要 numpy。
執行:  python3 generate_data.py
輸出:  public/data/waveform.csv  時域波形 (t, source_a, source_b, noise, mixture)
       public/data/spectrum.csv  單邊振幅頻譜 (freq_hz, source_a, source_b, mixture)
       public/data/peaks.csv     各音源的頻率成分 (source, freq_hz, amplitude)
"""
import cmath
import csv
import math
import os
import random

FS = 4096           # 取樣率 (Hz)
N = 2048            # 樣本數 → 0.5 秒；頻率解析度 FS / N = 2 Hz
SEED = 42           # 固定亂數種子，資料可重現
NOISE_STD = 0.12    # 高斯白雜訊標準差
OUT_DIR = "public/data"   # Vite 會把 public/ 底下的檔案原樣提供在網站根目錄

# 每個音源 = 基頻 + 一個泛音：(頻率 Hz, 振幅)。頻率都是 2 Hz 的倍數，剛好落在 FFT 的 bin 上。
SOURCES = {
    "source_a": [(110, 1.0), (220, 0.45)],   # 低音
    "source_b": [(350, 0.8), (700, 0.30)],   # 高音
}


def synth(components, t):
    """把多個正弦波疊加成一個樣本值。"""
    return sum(a * math.sin(2 * math.pi * f * t) for f, a in components)


def fft(x):
    """遞迴 radix-2 FFT (長度必須是 2 的次方)。"""
    n = len(x)
    if n == 1:
        return [complex(x[0])]
    even = fft(x[0::2])
    odd = fft(x[1::2])
    out = [0j] * n
    for k in range(n // 2):
        tw = cmath.exp(-2j * math.pi * k / n) * odd[k]
        out[k] = even[k] + tw
        out[k + n // 2] = even[k] - tw
    return out


def amplitude_spectrum(signal, window):
    """Hann 視窗 + FFT → 單邊振幅頻譜，正弦波的峰值 ≈ 它的振幅。"""
    spec = fft([s * w for s, w in zip(signal, window)])
    scale = 2.0 / sum(window)
    return [abs(spec[k]) * scale for k in range(N // 2 + 1)]


def main():
    random.seed(SEED)
    os.makedirs(OUT_DIR, exist_ok=True)

    t = [i / FS for i in range(N)]
    a = [synth(SOURCES["source_a"], ti) for ti in t]
    b = [synth(SOURCES["source_b"], ti) for ti in t]
    noise = [random.gauss(0.0, NOISE_STD) for _ in range(N)]
    mix = [a[i] + b[i] + noise[i] for i in range(N)]

    with open(f"{OUT_DIR}/waveform.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "source_a", "source_b", "noise", "mixture"])
        for i in range(N):
            w.writerow([f"{t[i]:.6f}", f"{a[i]:.5f}", f"{b[i]:.5f}", f"{noise[i]:.5f}", f"{mix[i]:.5f}"])

    window = [0.5 - 0.5 * math.cos(2 * math.pi * i / N) for i in range(N)]
    sa = amplitude_spectrum(a, window)
    sb = amplitude_spectrum(b, window)
    sm = amplitude_spectrum(mix, window)
    with open(f"{OUT_DIR}/spectrum.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["freq_hz", "source_a", "source_b", "mixture"])
        for k in range(N // 2 + 1):
            w.writerow([f"{k * FS / N:g}", f"{sa[k]:.5f}", f"{sb[k]:.5f}", f"{sm[k]:.5f}"])

    with open(f"{OUT_DIR}/peaks.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["source", "freq_hz", "amplitude"])
        for name, comps in SOURCES.items():
            for freq, amp in comps:
                w.writerow([name, freq, amp])

    print(f"waveform.csv: {N} rows ({N / FS:.2f} s @ {FS} Hz)")
    print(f"spectrum.csv: {N // 2 + 1} bins (resolution {FS / N:g} Hz)")
    for name, comps in SOURCES.items():
        for freq, amp in comps:
            k = int(freq * N / FS)
            print(f"  {name} {freq:>4} Hz  expected {amp:.2f}  measured in mixture {sm[k]:.3f}")


if __name__ == "__main__":
    main()
