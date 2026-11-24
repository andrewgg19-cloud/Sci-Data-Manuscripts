"""Rosetta 10000: decodificacion asistida de todos los segmentos, con reanudacion.
No es decodificacion ciega: segmentos y diccionario conocidos.
La identidad verdadera se usa UNICAMENTE despues de escoger la prediccion.
"""
import argparse,csv,hashlib,json,math,pathlib,wave,time
import numpy as np
PHI=(1+5**.5)/2

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--wav',default='Rosetta_10000_base.wav');p.add_argument('--csv',default='Rosetta_10000_partitura.csv')
 p.add_argument('--from-note',type=int,default=1);p.add_argument('--to-note',type=int,default=10000)
 p.add_argument('--candidates',type=int,default=1000);p.add_argument('--stride',type=int,default=8)
 p.add_argument('--conditions',default='ruido_15dB,desfase_3ms_pilotos,ruido_15dB_desfase_pilotos',help='Separadas por comas: limpio,ruido_15dB,desfase_3ms_pilotos,ruido_15dB_desfase_pilotos')
 p.add_argument('--seed',type=int,default=20261022);p.add_argument('--out',default='Rosetta_exhaustiva')
 a=p.parse_args();conditions=[x.strip() for x in a.conditions.split(',') if x.strip()]
 if not set(conditions)<=set(['limpio','ruido_15dB','desfase_3ms_pilotos','ruido_15dB_desfase_pilotos']):p.error('Condiciones no reconocidas')
 if a.stride<1 or a.candidates<1:p.error('stride y candidates positivos')
 with open(a.csv,encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
 n=len(rows);freq=np.array([float(x['frecuencia_hz']) for x in rows]);phase=np.array([float(x['fase_rad']) for x in rows]);dur=np.array([float(x['duracion_s']) for x in rows]);
 with wave.open(a.wav,'rb') as w:
  if w.getnchannels()!=2 or w.getsampwidth()!=2: raise ValueError('WAV debe ser PCM16 estereo')
  sr=w.getframerate();audio=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2)
 sizes=np.maximum(8,np.rint(dur*sr).astype(int));pause=round(.018*sr);starts=np.cumsum(np.r_[0,sizes[:-1]+pause]);
 if starts[-1]+sizes[-1]>len(audio):raise ValueError('Audio mas corto que partitura')
 if a.from_note<1 or a.to_note>n or a.from_note>a.to_note:p.error('Rango invalido')
 wav_hash=hashlib.sha256(pathlib.Path(a.wav).read_bytes()).hexdigest();csv_hash=hashlib.sha256(pathlib.Path(a.csv).read_bytes()).hexdigest()
 config={'wav_sha256':wav_hash,'csv_sha256':csv_hash,'from_note':a.from_note,'to_note':a.to_note,'candidates':a.candidates,'stride':a.stride,'conditions':conditions,'seed':a.seed,'calibracion':'8 pilotos conocidos, excluidos del rango evaluado; retardo estimado por correlacion'}
 # Calibracion: 8 pilotos fuera del intervalo de evaluacion. Las identidades de
 # los pilotos son conocidas; las de las notas examinadas NO se consultan.
 shift=round(.003*sr) # Desfase de laboratorio INYECTADO; estimador no lo recibe.
 estimated_shift=None; pilots=[]
 if any('pilotos' in c for c in conditions):
  low,high=a.from_note-1,a.to_note-1
  eligible=[i for i in np.unique(np.linspace(4,n-5,min(n,60),dtype=int)) if not low<=i<=high]
  if len(eligible)<8:
   eligible=[i for i in range(n) if not low<=i<=high]
  if len(eligible)<8:
   raise SystemExit('No existen 8 pilotos fuera de la evaluacion. Para evaluar 1..10000, hacen falta pilotos externos independientes: ejecute solamente --conditions ruido_15dB y no reporte calibracion autonoma.')
  pilots=eligible[:8]
  maxlag=round(.005*sr)
  lag_scores=np.zeros(maxlag+1)
  for pi in pilots:
   sizep=int(sizes[pi]); tp=np.arange(sizep)/sr
   ep=np.sin(np.pi*np.arange(sizep)/(sizep-1))**2
   ang=2*np.pi*freq[pi]*tp; ph=phase[pi]
   model=np.stack((ep*(np.sin(ang+ph)+.18*np.sin(PHI*ang+ph)),ep*(np.sin(ang-ph)+.18*np.sin(PHI*ang-ph))),axis=1)
   clean=audio[starts[pi]:starts[pi]+sizep].astype(np.float64)/32768
   delayed=np.pad(clean,((shift,0),(0,0)))[:sizep]
   for lag in range(maxlag+1):
    x=delayed[lag:];ref=model[:sizep-lag]
    lag_scores[lag]+=np.sum(x*ref)/(np.linalg.norm(x)*np.linalg.norm(ref)+1e-15)
  estimated_shift=int(np.argmax(lag_scores))
  print('Pilotos externos:',[int(i+1) for i in pilots],'lag_estimado_muestras:',estimated_shift,'lag_inyectado_muestras:',shift,flush=True)
 # Referencias de frecuencia y fase compartidas; la verdad no interviene en ranking.
 order=np.argsort(freq);sorted_freq=freq[order];work=pathlib.Path(a.out+'.jsonl');cfgpath=pathlib.Path(a.out+'_config.json')
 if cfgpath.exists():
  if json.loads(cfgpath.read_text(encoding='utf-8'))!=config:raise SystemExit('Configuracion distinta de ejecucion anterior. Use otro --out.')
 else:cfgpath.write_text(json.dumps(config,indent=2),encoding='utf-8')
 completed=set();counts={c:{'aciertos':0,'cobertura':0,'evaluados':0} for c in conditions}
 if work.exists():
  for line in work.read_text(encoding='utf-8').splitlines():
   if not line.strip():continue
   r=json.loads(line);completed.add((r['indice'],r['condicion']));c=counts[r['condicion']];c['evaluados']+=1;c['aciertos']+=r['acierto'];c['cobertura']+=r['cobertura']
 print('Procesados previamente:',len(completed),'de',(a.to_note-a.from_note+1)*len(conditions),flush=True)
 rng=np.random.default_rng(a.seed)
 # La correccion usa exclusivamente estimated_shift obtenido de pilotos externos.
 # shift se usa SOLO para simular la perturbacion, nunca para corregir.
 tstart=time.time()
 with work.open('a',encoding='utf-8') as fp:
  for idx in range(a.from_note-1,a.to_note):
   size=int(sizes[idx]);original=audio[starts[idx]:starts[idx]+size].astype(np.float64)/32768
   tt=np.arange(0,size,a.stride)/sr;env=np.sin(np.pi*np.arange(0,size,a.stride)/(size-1))**2
   for cond in conditions:
    if (idx+1,cond) in completed:continue
    seg=original.copy()
    if cond in ('ruido_15dB','ruido_15dB_desfase_pilotos'):
     # Semilla por simbolo: comparable y reproducible al reanudar
     local=np.random.default_rng(a.seed+idx*17+3)
     rms=np.sqrt(np.mean(seg**2));seg+=local.normal(0,rms*10**(-15/20),seg.shape)
    if 'pilotos' in cond:
     seg=np.pad(seg,((shift,0),(0,0)))[:size]
     seg=np.pad(seg[estimated_shift:],((0,estimated_shift),(0,0)))[:size]
    mono=seg.mean(axis=1);nfft=2**math.ceil(math.log2(max(8192,size*4)))
    sp=np.abs(np.fft.rfft(mono*np.hanning(size),nfft));bins=np.fft.rfftfreq(nfft,1/sr);valid=np.flatnonzero((bins>=110)&(bins<440))
    fhat=bins[valid[np.argmax(sp[valid])]];center=np.searchsorted(sorted_freq,fhat);kk=min(a.candidates,n)
    lo=max(0,int(center)-kk//2);hi=min(n,lo+kk);lo=max(0,hi-kk);pool=order[lo:hi]
    obs=seg[::a.stride];norm=np.maximum(np.linalg.norm(obs,axis=0),1e-15)
    bestscore=-np.inf;prediction=-1
    for j in range(0,len(pool),64):
     ids=pool[j:j+64];ang=2*np.pi*freq[ids,None]*tt[None,:];theta=phase[ids,None]
     left=env[None,:]*(np.sin(ang+theta)+.18*np.sin(PHI*ang+theta))
     right=env[None,:]*(np.sin(ang-theta)+.18*np.sin(PHI*ang-theta))
     sl=(left@obs[:,0])/(np.maximum(np.linalg.norm(left,axis=1),1e-15)*norm[0]);srsc=(right@obs[:,1])/(np.maximum(np.linalg.norm(right,axis=1),1e-15)*norm[1]);scores=(sl+srsc)/2
     k=int(np.argmax(scores));v=float(scores[k])
     if v>bestscore:bestscore=v;prediction=int(ids[k])
    result={'indice':idx+1,'condicion':cond,'prediccion':prediction+1,'acierto':int(prediction==idx),'cobertura':int(idx in pool),'f_estimado':float(fhat),'score':bestscore}
    fp.write(json.dumps(result,ensure_ascii=False)+'\n');fp.flush()
    cc=counts[cond];cc['evaluados']+=1;cc['aciertos']+=result['acierto'];cc['cobertura']+=result['cobertura']
   if (idx+1)%100==0:
    print(f'{idx+1}/{a.to_note} notas | '+ ' | '.join(f'{c}: {counts[c]["aciertos"]}/{counts[c]["evaluados"]}' for c in conditions),flush=True)
 summary={'protocolo':'Segmentacion y diccionario conocidos; no ciego. Los pilotos deben quedar fuera de los simbolos evaluados.', 'calibracion': {'pilotos_1_based':[int(i+1) for i in pilots], 'retardo_estimado_muestras':estimated_shift, 'retardo_inyectado_muestras_solo_control':shift},'config':config,'duracion_ejecucion_s':time.time()-tstart,'resultados':{c:{**v,'exactitud_pct':100*v['aciertos']/v['evaluados'] if v['evaluados'] else None,'cobertura_pct':100*v['cobertura']/v['evaluados'] if v['evaluados'] else None} for c,v in counts.items()},'registro':str(work)}
 pathlib.Path(a.out+'_resumen.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
