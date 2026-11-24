"""Rosetta 10000 - auditoria de decodificacion con 4 modalidades y varios K.
Usa WAV y partitura conocidos para segmentacion y codebook; NUNCA usa el indice
verdadero en seleccion/ranking. Recuperacion asistida, no ciega.
"""
import argparse,csv,json,math,pathlib,wave,hashlib
import numpy as np
PHI=(1+5**.5)/2

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--wav',default='Rosetta_10000_base.wav')
 ap.add_argument('--csv',default='Rosetta_10000_partitura.csv')
 ap.add_argument('--max-notes',type=int,default=100)
 ap.add_argument('--candidates',default='60,200,500,1000')
 ap.add_argument('--downsample',type=int,default=6)
 ap.add_argument('--batch',type=int,default=100)
 ap.add_argument('--out',default='Rosetta_comparacion_4_metodos')
 args=ap.parse_args()
 if args.downsample<1 or args.batch<1 or args.max_notes<1: ap.error('Parametros invalidos')
 ks=sorted(set(int(x) for x in args.candidates.split(',')))
 if not ks or min(ks)<1: ap.error('candidates deben ser enteros positivos')
 with open(args.csv,encoding='utf-8-sig',newline='') as h: rows=list(csv.DictReader(h))
 f=np.array([float(r['frecuencia_hz']) for r in rows]); theta=np.array([float(r['fase_rad']) for r in rows]); dur=np.array([float(r['duracion_s']) for r in rows]); n=min(args.max_notes,len(rows)); sr=None
 with wave.open(args.wav,'rb') as w:
  sr=w.getframerate()
  if w.getnchannels()!=2 or w.getsampwidth()!=2: raise SystemExit('Se requiere WAV PCM16 estereo')
  audio=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2).astype(np.float64)/32768
 ns=np.maximum(8,np.rint(dur*sr).astype(int)); silence=round(.018*sr)
 starts=np.cumsum(np.r_[0,ns[:-1]+silence]);
 if starts[n-1]+ns[n-1]>len(audio):raise SystemExit('WAV y CSV incompatibles')
 order=np.argsort(f); sortedf=f[order]; kmax=min(max(ks),len(rows)); methods=['solo_izquierdo','solo_derecho','ambos_canales','diferencia_fase']
 accum={k:{'in_candidates':0,**{m:0 for m in methods},**{m+'_top5':0 for m in methods}} for k in ks}; output=[]
 for i in range(n):
  size=int(ns[i]); seg=audio[starts[i]:starts[i]+size]; mono=seg.mean(axis=1); window=np.hanning(size)
  nfft=2**math.ceil(math.log2(max(8192,size*4))); spectrum=np.abs(np.fft.rfft(mono*window,n=nfft)); bins=np.fft.rfftfreq(nfft,1/sr)
  allowed=np.flatnonzero((bins>=110)&(bins<440)); fhat=float(bins[allowed[np.argmax(spectrum[allowed])]])
  center=int(np.searchsorted(sortedf,fhat)); lo=max(0,center-kmax//2); hi=min(len(rows),lo+kmax);lo=max(0,hi-kmax); pool=order[lo:hi]
  # Each K gets its own centered candidate set; no true-index lookup in selection.
  t=np.arange(0,size,args.downsample,dtype=np.float64)/sr; env=np.sin(np.pi*np.arange(0,size,args.downsample)/(size-1))**2
  obs=seg[::args.downsample]; norms=np.sqrt(np.sum(obs*obs,axis=0))+1e-15
  scores=np.empty((len(pool),4),dtype=np.float64)
  for a in range(0,len(pool),args.batch):
   ids=pool[a:a+args.batch]; omega=2*np.pi*f[ids,None]*t[None,:]; angL=omega+theta[ids,None];angR=omega-theta[ids,None]
   layerL=np.sin(angL)+.18*np.sin(PHI*omega+theta[ids,None]);layerR=np.sin(angR)+.18*np.sin(PHI*omega-theta[ids,None])
   L=env[None,:]*layerL;R=env[None,:]*layerR
   nl=np.linalg.norm(L,axis=1)+1e-15; nr=np.linalg.norm(R,axis=1)+1e-15
   pl=(L@obs[:,0])/(nl*norms[0]);pr=(R@obs[:,1])/(nr*norms[1])
   # Phase-difference statistic: compare normalized relative waveforms with
   # cross-channel interference; independent of absolute per-channel scale.
   diff=L/(nl[:,None])-R/(nr[:,None]); dobs=obs[:,0]/norms[0]-obs[:,1]/norms[1]
   pd=(diff@dobs)/(np.linalg.norm(diff,axis=1)*np.linalg.norm(dobs)+1e-15)
   scores[a:a+len(ids),0]=pl;scores[a:a+len(ids),1]=pr
   scores[a:a+len(ids),2]=(pl+pr)/2;scores[a:a+len(ids),3]=pd
  row={'indice_real_solo_para_evaluacion':i+1,'fhat_hz':fhat}
  for k in ks:
   kk=min(k,len(rows));left=max(0,center-kk//2);right=min(len(rows),left+kk);left=max(0,right-kk)
   # Restrict to same K-neighbor set for all four methods
   eligible=(sortedf[left:right]); ids=order[left:right]
   pos={int(j):p for p,j in enumerate(pool)};pool_pos=np.array([pos[int(j)] for j in ids]);sc=scores[pool_pos,:]
   truth_in=bool(np.any(ids==i));accum[k]['in_candidates']+=truth_in
   row[f'candidato_K{k}']=int(truth_in)
   for m_idx,m in enumerate(methods):
    ranking=np.argsort(-sc[:,m_idx]);pred=int(ids[ranking[0]])+1
    accum[k][m]+=int(pred==i+1);accum[k][m+'_top5']+=int(truth_in and np.any(ids[ranking[:5]]==i))
    row[f'{m}_K{k}']=pred
  output.append(row)
  if (i+1)%10==0: print(f'Analizadas {i+1}/{n}',flush=True)
 report={'wav':args.wav,'csv':args.csv,'notas_evaluadas':n,'codebook_size':len(rows),'downsample':args.downsample,'metodo':'Segmentacion asistida y codebook; correlacion con sintesis base, sin elegir candidatos a partir del simbolo verdadero.','resultados':{str(k):{'cobertura_candidatos_pct':100*accum[k]['in_candidates']/n,**{m+'_exactitud_pct':100*accum[k][m]/n for m in methods},**{m+'_top5_pct':100*accum[k][m+'_top5']/n for m in methods}} for k in ks},'advertencia':'NO es decodificacion ciega; la tabla contiene las fases y frecuencias esperadas. Esta prueba no recupera gamma original sin informacion auxiliar. Resultados solo verificables al ejecutarse sobre el WAV real.'}
 base=pathlib.Path(args.out)
 with base.with_suffix('.csv').open('w',encoding='utf-8',newline='') as h:
  writer=csv.DictWriter(h,fieldnames=output[0].keys());writer.writeheader();writer.writerows(output)
 base.with_suffix('.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
