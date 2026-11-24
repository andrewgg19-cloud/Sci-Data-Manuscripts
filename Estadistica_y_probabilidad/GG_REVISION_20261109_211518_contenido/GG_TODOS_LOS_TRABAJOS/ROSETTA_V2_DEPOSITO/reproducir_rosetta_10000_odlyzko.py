"""Rosetta 10,000: extensión experimental, dos audios WAV estéreo PCM16.
Fuente: tabla oficial zeros1 de Odlyzko; audio generado en streaming, dos pasadas.
"""
import csv, hashlib, json, math, pathlib, urllib.request, wave
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent
N, SR = 10000, 22050
PHI = (1 + 5**0.5) / 2
URL = 'https://www-users.cse.umn.edu/~odlyzko/zeta_tables/zeros1'
DATA = ROOT / 'Odlyzko_zeros1_fuente.txt'

if not DATA.exists():
    print('Descargando tabla oficial zeros1 de Odlyzko...', flush=True)
    try:
        urllib.request.urlretrieve(URL, DATA)
    except Exception as e:
        raise SystemExit(f'No se descargó la tabla: {e}\nDescarga manualmente {URL}\ny guárdala como {DATA.name} en la carpeta de este script.')
raw = DATA.read_text(encoding='ascii').split()
if len(raw) < N:
    raise SystemExit(f'Se requieren {N} ordenadas, pero el archivo contiene {len(raw)}.')
raw = raw[:N]
if raw[0] != '14.134725142' or raw[1] != '21.022039639':
    raise SystemExit('El encabezado de zeros1 no coincide con las dos ordenadas esperadas; comprueba la fuente.')
gamma = np.array([float(x) for x in raw])
if not np.all(np.diff(gamma) > 0):
    raise SystemExit('Los valores gamma no están ordenados estrictamente.')

# Criba para los primeros 10,000 primos: p_10000=104729.
limit = 110000
sieve = np.ones(limit + 1, dtype=bool)
sieve[:2] = False
for p in range(2, math.isqrt(limit) + 1):
    if sieve[p]: sieve[p*p::p] = False
primes = np.flatnonzero(sieve)[:N]
assert len(primes) == N and primes[-1] == 104729

# Fibonacci exacto en enteros; comprimido al logaritmo para normalización estable.
fibs = [1, 1]
for _ in range(2, N): fibs.append(fibs[-1] + fibs[-2])
logf = np.array([math.log(f) for f in fibs], dtype=np.float64)
u = (logf - logf[0]) / (logf[-1] - logf[0])
durations = .085 + .065*u
amps = .16 + .69*u**1.7
pause_samples = round(.018*SR)
freqs = np.array([110 * 2**((math.log(int(p)) % math.log(4))/math.log(2)) for p in primes])
# Parámetro extraído según el manuscrito: theta_n=2pi frac(gamma_n/phi).
phases = 2*math.pi*np.mod(gamma/PHI, 1.0)
nsamp = np.maximum(8, np.rint(durations*SR).astype(int))

# CSV sin enteros Fibonacci de miles de cifras: F_n exacto puede regenerarse del índice.
score_path = ROOT / 'Rosetta_10000_partitura.csv'
with score_path.open('w', encoding='utf-8', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['n','primo','gamma_odlyzko','frecuencia_hz','fase_rad','log_fibonacci_normalizado','duracion_s','amplitud'])
    for i in range(N):
        w.writerow([i+1, int(primes[i]), raw[i], f'{freqs[i]:.10f}', f'{phases[i]:.10f}', f'{u[i]:.10f}', f'{durations[i]:.8f}', f'{amps[i]:.8f}'])
(ROOT/'Rosetta_10000_gamma.txt').write_text('\n'.join(raw)+'\n',encoding='ascii')

def note(i, crescendo):
    k = int(nsamp[i]); t = np.arange(k, dtype=np.float64)/SR
    env = np.sin(np.pi*np.arange(k)/(k-1))**2
    f, th, a = freqs[i], phases[i], amps[i]
    l = np.sin(2*np.pi*f*t+th) + .18*np.sin(2*np.pi*PHI*f*t+th)
    r = np.sin(2*np.pi*f*t-th) + .18*np.sin(2*np.pi*PHI*f*t-th)
    sig = np.column_stack((l,r))* (a*env)[:,None]
    if crescendo:
        # Cuatro capas adicionales, progresivas en cinco etapas (misma regla de Rosetta 1000).
        density = 1+(i*4//N)
        for ratio,weight in ((.5,.12),(1.5,.12),(2.,.10),(3.,.08))[:density-1]:
            sig[:,0] += env*a*weight*np.sin(2*np.pi*ratio*f*t+th)
            sig[:,1] += env*a*weight*np.sin(2*np.pi*ratio*f*t-th)
    return sig

def render(crescendo):
    name = 'Rosetta_10000_crescendo.wav' if crescendo else 'Rosetta_10000_base.wav'
    print(f'Analizando pico {name}...', flush=True)
    peak = 0.; rms_first = rms_last = 0.
    for i in range(N):
        a = note(i,crescendo)
        peak = max(peak,float(np.max(np.abs(a))))
        if i==0: rms_first=float(np.sqrt(np.mean(a*a)))
        if i==N-1: rms_last=float(np.sqrt(np.mean(a*a)))
    gain = .90 / max(peak, 1e-12)
    total=0
    silence = np.zeros((pause_samples, 2),dtype='<i2').tobytes()
    with wave.open(str(ROOT/name),'wb') as wav:
        wav.setnchannels(2);wav.setsampwidth(2);wav.setframerate(SR)
        for i in range(N):
            a = np.clip(note(i,crescendo)*gain,-1,1)
            wav.writeframes(np.rint(a*32767).astype('<i2').tobytes())
            total += len(a)
            if i < N-1:
                wav.writeframes(silence)
                total += pause_samples
            if (i+1)%2000==0: print(f'  {i+1}/{N} notas escritas',flush=True)
    return dict(file=name,duration_s=total/SR,samples_per_channel=total,peak_pre_norm=peak,gain=gain,rms_first=rms_first,rms_last=rms_last,bytes=(ROOT/name).stat().st_size)

results = [render(False),render(True)]
meta = dict(version='Rosetta 10000 extensión experimental, no equivalente al prototipo original de 13 pasos',
    fuente=URL,primeros_ceros=N,primo_final=int(primes[-1]),sample_rate=SR,
    gamma_sha256=hashlib.sha256((ROOT/'Rosetta_10000_gamma.txt').read_bytes()).hexdigest(),
    definiciones='Frecuencia y fase del manuscrito; amplitud y duración normalizadas usando log(F_n), NO las fórmulas sin normalizar del prototipo de 13 pasos',
    pausa_s_aproximada=pause_samples/SR,normalizacion='Ganancia global por modalidad a pico .90, PCM16',resultados=results)
(ROOT/'Rosetta_10000_parametros.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(meta,ensure_ascii=False,indent=2))
