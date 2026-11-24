#!/usr/bin/env python3
"""Construcción finita reproducible del tambor primo diagonal."""

from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile
from scipy.signal import spectrogram


PRIME_COUNT = 100
MAX_POWER = 4
SIGMA = 1.1
TIME_SCALE = 800.0
DURATION = 18.0
RATE = 48_000


def first_primes(count: int) -> list[int]:
    values = []
    n = 2
    while len(values) < count:
        if all(n % p for p in values if p <= math.isqrt(n)):
            values.append(n)
        n += 1
    return values


def build_modes():
    rows = []
    for p in first_primes(PRIME_COUNT):
        for m in range(1, MAX_POWER + 1):
            omega = m * math.log(p)
            weight = math.log(p) / p ** (m * SIGMA)
            rows.append((p, m, omega, weight, TIME_SCALE * omega / (2 * math.pi)))
    return rows


def synthesize(omega: np.ndarray, weight: np.ndarray) -> np.ndarray:
    samples = int(DURATION * RATE)
    output = np.empty(samples, dtype=np.float64)
    normalizer = weight.sum()
    block = 4096
    for start in range(0, samples, block):
        stop = min(samples, start + block)
        t = np.arange(start, stop, dtype=np.float64) / RATE
        output[start:stop] = (
            weight[:, None] * np.cos(TIME_SCALE * omega[:, None] * t)
        ).sum(axis=0) / normalizer
    # Se conserva el ataque x(0)=1; sólo se suaviza la terminación del archivo.
    release = int(0.08 * RATE)
    output[-release:] *= np.cos(np.linspace(0, math.pi / 2, release)) ** 2
    return output


def verification_rows(omega: np.ndarray, weight: np.ndarray):
    normalizer = weight.sum()
    vector = np.sqrt(weight / normalizer).astype(np.complex128)
    rows = []
    for t in [0.0, 0.001, 0.01, 0.125, 0.5, 1.0, 2.0, 5.0]:
        diagonal = np.exp(-1j * TIME_SCALE * omega * t)
        matrix_value = np.vdot(vector, diagonal * vector)
        sum_value = np.sum((weight / normalizer) * diagonal)
        rows.append({
            "time_seconds": t,
            "matrix_real": matrix_value.real,
            "matrix_imag": matrix_value.imag,
            "prime_sum_real": sum_value.real,
            "prime_sum_imag": sum_value.imag,
            "absolute_difference": abs(matrix_value - sum_value),
        })
    return rows


def main():
    root = Path(__file__).resolve().parent
    modes = build_modes()
    primes = np.array([r[0] for r in modes], dtype=np.int64)
    powers = np.array([r[1] for r in modes], dtype=np.int64)
    omega = np.array([r[2] for r in modes], dtype=np.float64)
    weight = np.array([r[3] for r in modes], dtype=np.float64)
    frequency = np.array([r[4] for r in modes], dtype=np.float64)
    vector = np.sqrt(weight).astype(np.complex128)

    # H queda representado sin ambigüedad por su diagonal real.
    np.savez_compressed(
        root / "tambor_aritmetico_operador.npz",
        primes=primes,
        powers=powers,
        H_diagonal=omega,
        excitation_vector=vector,
        sigma=np.array(SIGMA),
        time_scale=np.array(TIME_SCALE),
    )

    with (root / "modos_del_tambor.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["prime", "power", "eigenvalue_m_log_p",
                         "weight_logp_over_p_msigma", "audible_frequency_hz"])
        writer.writerows(modes)

    checks = verification_rows(omega, weight)
    with (root / "verificacion_autocorrelacion.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(checks[0]))
        writer.writeheader()
        writer.writerows(checks)

    audio = synthesize(omega, weight)
    wavfile.write(root / "tambor_aritmetico.wav", RATE,
                  np.int16(np.clip(audio, -1, 1) * 32767))

    f, t, s = spectrogram(audio, fs=RATE, nperseg=8192, noverlap=6144)
    mask = (f >= 60) & (f <= 3400)
    fig, ax = plt.subplots(figsize=(12, 5), constrained_layout=True)
    mesh = ax.pcolormesh(t, f[mask], 10*np.log10(s[mask] + 1e-14),
                         shading="auto", cmap="inferno")
    ax.set(title="Respuesta del tambor aritmético",
           xlabel="Tiempo (s)", ylabel="Frecuencia (Hz)")
    fig.colorbar(mesh, ax=ax, label="Potencia (dB)")
    fig.savefig(root / "espectrograma_tambor_aritmetico.png", dpi=180)
    plt.close(fig)

    print(f"modes={len(modes)}; primes={PRIME_COUNT}; max_p={primes.max()}; "
          f"max_identity_error={max(float(r['absolute_difference']) for r in checks):.3e}")


if __name__ == "__main__":
    main()
