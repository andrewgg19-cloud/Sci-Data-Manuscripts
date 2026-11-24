"""Rosetta 10000: validacion asistida, estratificada y con controles negativos.
No es una decodificacion ciega: conoce tabla de frecuencias/fases y duraciones.
No consulta el indice correcto durante la prediccion.
"""
import argparse, csv, hashlib, json, math, pathlib, wave
import numpy as np
P=pathlib.Path(__file__).resolve().parent
PHI=(1+5**.5)/2

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--wav',default='Rosetta_10000_base.wav')
 ap.add_argument('--csv',default='Rosetta_10000_partitura.csv')
 ap.add_argument('--notes',type=int,default=100)
 ap.add_argument('--candidates',type=int,default=1000)
 ap.add_argument('--seed',type=int,default=20261022)
 ap.add_argument('--stride',type=int,default=5,help='Submuestreo temporal para correlacion')
 ap.add_argument('--out',default='Rosetta_validacion_robustez')
 args=ap.parse_args()
 if args.notes<4 or args.candidates<1 or args.stride<1: ap.error('Argumentos invalidos')
 with open(args.csv,encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
 nrows=len(rows); freq=np.array([float(x['frecuencia_hz']) for x in rows]); th=np.array([float(x['fase_rad']) for x in rows]); dur=np.array([float(x['duracion_s']) for x in rows]); ns=None
 with wave.open(args.wav,'rb') as w:
  sr=w.getframerate()
  if w.getnchannels()!=2 or w.getsampwidth()!=2: raise SystemExit('Se necesita WAV PCM16 estereo')
  audio=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2).astype(np.float64)/32768
 ns=np.maximum(8,np.rint(dur*sr).astype(int)); pause=round(.018*sr)
 starts=np.cumsum(np.r_[0,ns[:-1]+pause]); valid=np.flatnonzero(starts+ns<=len(audio))
 if len(valid)<nrows: raise SystemExit('WAV mas corto que partitura; no continuar')
 # indices estratificados sobre toda la secuencia; sin seleccionar por el resultado
 ids=np.unique(np.linspace(0,nrows-1,min(args.notes,nrows),dtype=int))
 order=np.argsort(freq); fs=freq[order]
 rng=np.random.default_rng(args.seed)
 conditions=['limpio','ruido_30dB','ruido_15dB','desfase_3ms']
 methods=['izquierdo','derecho','estereo','diferencia_fase','fase_permutada_control']
 tally={c:{m:0 for m in methods}|{'cobertura':0} for c in conditions}; records=[]
 permuted=th[rng.permutation(nrows)]
 for j,i in enumerate(ids):
  size=int(ns[i]); original=audio[starts[i]:starts[i]+size,:].copy()
  for cond in conditions:
   seg=original.copy()
   if cond.startswith('ruido_'):
    snr=30 if cond=='ruido_30dB' else 15
    rms=np.sqrt(np.mean(seg*seg)); noise=rng.normal(0,rms*10**(-snr/20),size=seg.shape);seg+=noise
   if cond=='desfase_3ms':
    shift=round(.003*sr)
    # desplazamiento de muestras conservando tamaño con relleno silencioso
    seg=np.pad(seg,((shift,0),(0,0)))[:size]
   # ranking basado solo en espectro del audio. Sin uso del simbolo verdadero.
   mono=seg.mean(axis=1); nfft=2**math.ceil(math.log2(max(8192,size*4)))
   spec=np.abs(np.fft.rfft(mono*np.hanning(size),n=nfft)); bins=np.fft.rfftfreq(nfft,1/sr)
   ok=np.flatnonzero((bins>=110)&(bins<440))
   fhat=bins[ok[np.argmax(spec[ok])]]; center=int(np.searchsorted(fs,fhat)); kk=min(args.candidates,nrows)
   left=max(0,center-kk//2);right=min(nrows,left+kk);left=max(0,right-kk); pool=order[left:right]
   tally[cond]['cobertura']+=int(i in pool)
   t=np.arange(0,size,args.stride)/sr; env=np.sin(np.pi*np.arange(0,size,args.stride)/(size-1))**2
   obs=seg[::args.stride]; norms=np.maximum(np.linalg.norm(obs,axis=0),1e-15)
   difobs=obs[:,0]/norms[0]-obs[:,1]/norms[1]; nd=np.linalg.norm(difobs)+1e-15
   best={m:(-1e99,-1) for m in methods}
   for begin in range(0,len(pool),60):
    batch=pool[begin:begin+60]
    ang=2*np.pi*freq[batch,None]*t[None,:]
    L=env[None,:]*(np.sin(ang+th[batch,None])+.18*np.sin(PHI*ang+th[batch,None]))
    R=env[None,:]*(np.sin(ang-th[batch,None])+.18*np.sin(PHI*ang-th[batch,None]))
    nl=np.maximum(np.linalg.norm(L,axis=1),1e-15);nr=np.maximum(np.linalg.norm(R,axis=1),1e-15)
    sL=(L@obs[:,0])/(nl*norms[0]);sR=(R@obs[:,1])/(nr*norms[1]);diff=L/nl[:,None]-R/nr[:,None]
    sDiff=(diff@difobs)/(np.maximum(np.linalg.norm(diff,axis=1),1e-15)*nd)
    # negativo: rompiendo aleatoriamente el emparejamiento gamma-frecuencia
    LP=env[None,:]*(np.sin(ang+permuted[batch,None])+.18*np.sin(PHI*ang+permuted[batch,None]))
    RP=env[None,:]*(np.sin(ang-permuted[batch,None])+.18*np.sin(PHI*ang-permuted[batch,None]))
    npL=np.maximum(np.linalg.norm(LP,axis=1),1e-15);npR=np.maximum(np.linalg.norm(RP,axis=1),1e-15)
    sPerm=((LP@obs[:,0])/(npL*norms[0])+(RP@obs[:,1])/(npR*norms[1]))/2
    for name, scores in zip(methods,[sL,sR,(sL+sR)/2,sDiff,sPerm]):
     idx=int(np.argmax(scores));v=float(scores[idx]);pred=int(batch[idx]);
     if v>best[name][0]:best[name]=(v,pred)
   line={'indice_verdadero_solo_evaluacion':int(i+1),'condicion':cond,'frecuencia_fft_hz':float(fhat),'verdadero_en_candidatos':int(i in pool)}
   for m in methods:
    pred=best[m][1];line[m+'_prediccion']=pred+1; tally[cond][m]+=int(pred==i)
   records.append(line)
  if (j+1)%10==0: print(f'{j+1}/{len(ids)} simbolos evaluados',flush=True)
 out={'aviso':'Segmentacion y diccionario conocidos; NO es decodificacion ciega ni recuperacion unica de gamma. La seleccion de candidatos depende solo del audio.','wav':args.wav,'wav_sha256':hashlib.sha256(pathlib.Path(args.wav).read_bytes()).hexdigest(),'csv':args.csv,'semilla':args.seed,'simbolos_evaluados':len(ids),'indices_estratificados_min_max':[int(ids[0]+1),int(ids[-1]+1)],'numero_candidatos':kk,'resultados':{c:{'cobertura_pct':100*v['cobertura']/len(ids),**{m+'_exactitud_pct':100*v[m]/len(ids) for m in methods}} for c,v in tally.items()}}
 prefix=pathlib.Path(args.out)
 with prefix.with_suffix('.csv').open('w',newline='',encoding='utf-8') as f:
  writer=csv.DictWriter(f,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)
 prefix.with_suffix('.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
