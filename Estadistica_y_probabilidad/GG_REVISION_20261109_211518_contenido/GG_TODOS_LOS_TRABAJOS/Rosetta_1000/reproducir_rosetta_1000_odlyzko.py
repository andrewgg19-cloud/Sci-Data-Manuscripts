import math,csv,json,wave,hashlib,zipfile, pathlib,sys
import numpy as np
from mpmath import mp
P=pathlib.Path(__file__).resolve().parent; N=1000; SR=22050; PHI=(1+5**.5)/2
mp.dps=40
# Odlyzko's zeros1 official source may be placed in the same directory.
# When absent, numerically evaluate zeta zeros via mpmath and identify result honestly.
source=P/'Odlyzko_zeros1_fuente.txt'
if not source.exists():
    import urllib.request
    url='https://www-users.cse.umn.edu/~odlyzko/zeta_tables/zeros1'
    print('Descargando tabla Odlyzko zeros1...',flush=True)
    try:
        urllib.request.urlretrieve(url,source)
    except Exception as exc:
        raise SystemExit('No se pudo descargar la tabla oficial: '+str(exc)+'\nDescargue zeros1 manualmente desde '+url+' y guárdelo junto a este programa como Odlyzko_zeros1_fuente.txt')
raw=source.read_text(encoding='ascii').split()[:N]
provenance='Andrew Odlyzko, zeros1 official first 1000 ordinates'
assert len(raw)==N
# Generate primes using elementary sieve.
lim=10000
sieve=np.ones(lim+1,dtype=bool); sieve[:2]=False
for p in range(2,int(lim**.5)+1):
    if sieve[p]:sieve[p*p::p]=False
primes=np.flatnonzero(sieve)[:N].tolist()
assert len(primes)==N and primes[-1]==7919
fibs=[1,1]
for i in range(2,N):fibs.append(fibs[-1]+fibs[-2])
# Proposed extension: use monotone log Fibonacci coordinate [0,1] to avoid astronomical durations.
fib_log=np.array([math.log(x) for x in fibs]); u=(fib_log-fib_log[0])/(fib_log[-1]-fib_log[0]);
# 80-160 ms duration, 20ms pause; approx 140 s. Dynamic curve grows 0.16 ->0.85.
durations=0.085+0.065*u
amps=0.16+0.69*u**1.7
pause=.018
phases=np.array([float((mp.mpf(x)/mp.mpf(str(PHI)))%1) for x in raw])*2*math.pi
fqs=np.array([110*2**((math.log(p)%math.log(4))/math.log(2)) for p in primes])
score=[]
for i in range(N):score.append({'n':i+1,'prime':primes[i],'gamma':raw[i],'fibonacci':str(fibs[i]),'normalized_log_fibonacci':round(float(u[i]),10),'frequency_hz':round(float(fqs[i]),9),'phase_radians':round(float(phases[i]),10),'duration_s':round(float(durations[i]),8),'amplitude':round(float(amps[i]),8)})
with open(P/'Rosetta_1000_partitura.csv','w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=score[0].keys());w.writeheader();w.writerows(score)
(P/'Rosetta_1000_gamma.txt').write_text('\n'.join(raw)+'\n')

def audio(mode):
    chunks=[]; rms=[]
    max_peak=0
    for i in range(N):
        k=max(8,round(SR*durations[i]));t=np.arange(k)/SR
        env=np.sin(np.pi*np.arange(k)/max(k-1,1))**2
        f=fqs[i]; theta=phases[i]; a=amps[i]
        left=np.sin(2*np.pi*f*t+theta)+.18*np.sin(2*np.pi*PHI*f*t+theta)
        right=np.sin(2*np.pi*f*t-theta)+.18*np.sin(2*np.pi*PHI*f*t-theta)
        stereo=np.stack((left,right),axis=1)*a*env[:,None]
        if mode=='crescendo':
            # Additional registered musical arrangement: density increases in 5 steps.
            density=1+(i*4//N)
            layers=((.5,.12),(1.5,.12),(2.,.10),(3.,.08))
            for ratio,weight in layers[:density-1]:
                stereo[:,0]+=env*a*weight*np.sin(2*np.pi*ratio*f*t+theta)
                stereo[:,1]+=env*a*weight*np.sin(2*np.pi*ratio*f*t-theta)
        rms.append(float(np.sqrt(np.mean(stereo**2))))
        chunks.append(stereo.astype(np.float32))
        if i<N-1:chunks.append(np.zeros((round(pause*SR),2),dtype=np.float32))
    out=np.concatenate(chunks)
    peak=float(np.max(np.abs(out)));out*=.90/max(peak,1e-10)
    pcm=np.round(out*32767).astype('<i2')
    fn='Rosetta_1000_crescendo.wav' if mode=='crescendo' else 'Rosetta_1000_base.wav'
    with wave.open(str(P/fn),'wb') as wav:
        wav.setnchannels(2);wav.setsampwidth(2);wav.setframerate(SR);wav.writeframes(pcm.tobytes())
    return {'file':fn,'duration_s':len(out)/SR,'samples_per_channel':len(out),'peak_pre_norm':peak,'rms_first':rms[0],'rms_last':rms[-1]}
results=[audio('base'),audio('crescendo')]
meta={'input_provenance':provenance,'official_odlyzko_url':'https://www-users.cse.umn.edu/~odlyzko/zeta_tables/zeros1','n':N,'sample_rate':SR,'input_gamma_sha256':hashlib.sha256((P/'Rosetta_1000_gamma.txt').read_bytes()).hexdigest(),'transforms':['prime frequency from manuscript','phase gamma/phi from manuscript','NEW extension: log(F_n) normalized over n=1..1000 for amplitude and duration','Hann-squared envelope; golden ratio second voice at 0.18','18ms breaks','global peak normalization'],'results':results}
(P/'Rosetta_1000_parametros.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False))
print(json.dumps(meta,ensure_ascii=False,indent=2))
