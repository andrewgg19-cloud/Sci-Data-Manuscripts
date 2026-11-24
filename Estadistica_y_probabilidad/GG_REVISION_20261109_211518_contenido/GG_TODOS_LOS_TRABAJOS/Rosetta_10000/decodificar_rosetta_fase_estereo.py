"""Rosetta 10 000: prueba de decodificación por frecuencia y fase estéreo.
Protocolo asistido: WAV PCM16, partitura completa compartida como codebook,
ventanas conocidas. NO es decodificación ciega ni recuperación de gamma completa.
No modifica archivos de entrada.
"""
import argparse, csv, json, math, pathlib, wave
import numpy as np
PHI = (1 + np.sqrt(5)) / 2

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--wav',default='Rosetta_10000_base.wav')
    p.add_argument('--csv',default='Rosetta_10000_partitura.csv')
    p.add_argument('--out',default='Rosetta_10000_fase_estereo')
    p.add_argument('--max-notes',type=int,default=10000)
    p.add_argument('--candidates',type=int,default=60,help='Número de candidatos por frecuencia en la primera fase')
    p.add_argument('--downsample',type=int,default=3,help='Muestrear cada N muestras para comparar modelos')
    args=p.parse_args()
    if args.candidates < 1 or args.downsample < 1: p.error('Los parámetros candidates/downsample deben ser >=1')
    with open(args.csv,encoding='utf-8-sig',newline='') as h: rows=list(csv.DictReader(h))
    f=np.array([float(r['frecuencia_hz']) for r in rows]); th=np.array([float(r['fase_rad']) for r in rows]); dur=np.array([float(r['duracion_s']) for r in rows]);
    count=min(args.max_notes,len(rows)); K=min(args.candidates,len(rows));
    with wave.open(args.wav,'rb') as w:
        sr=w.getframerate(); assert w.getnchannels()==2 and w.getsampwidth()==2, 'Se necesita WAV PCM16 estéreo'; total=w.getnframes(); sound=np.frombuffer(w.readframes(total),dtype='<i2').reshape(-1,2).astype(np.float64)/32768
    ns=np.maximum(8,np.rint(dur*sr).astype(int)); pause=round(.018*sr); start=np.cumsum(np.r_[0,ns[:-1]+pause]);
    if start[count-1]+ns[count-1]>len(sound): raise SystemExit('Duración WAV/CSV incompatible')
    # Espectro de referencia: elegir candidatos por diferencia de frecuencia
    order=np.argsort(f); sorted_f=f[order]
    results=[]; hitf=hitp=present=0; top5f=top5p=0
    for i in range(count):
        k=int(ns[i]); seg=sound[start[i]:start[i]+k]; mono=seg.mean(axis=1)
        nnfft=2**math.ceil(math.log2(max(8192,k*4)))
        window=np.hanning(k); spectrum=np.abs(np.fft.rfft(mono*window,n=nnfft)); bins=np.fft.rfftfreq(nnfft,1/sr)
        ix=np.flatnonzero((bins>=110)&(bins<440)); peakbin=ix[np.argmax(spectrum[ix])]; fhat=bins[peakbin]
        # Comparación igualitaria: ambos métodos reciben exactamente los mismos candidatos.
        center=int(np.searchsorted(sorted_f,fhat)); left=max(0,center-K//2); right=min(len(rows),left+K); left=max(0,right-K)
        inds=order[left:right]
        # Correlación normalizada del audio stereo con las ondas ideales; se ajusta
        # únicamente ganancia global positiva, sin corrección libre de fase.
        skip=args.downsample; t=np.arange(0,k,skip)/sr
        env=np.sin(np.pi*(t*sr)/(k-1))**2
        obs=seg[::skip]; obsnorm=np.linalg.norm(obs)+1e-15
        score=[]
        for j in inds:
            ang=2*np.pi*f[j]*t
            tl=env*(np.sin(ang+th[j])+.18*np.sin(PHI*ang+th[j]))
            tr=env*(np.sin(ang-th[j])+.18*np.sin(PHI*ang-th[j]))
            norm=np.sqrt(np.dot(tl,tl)+np.dot(tr,tr)) + 1e-15
            corr=(np.dot(tl,obs[:,0])+np.dot(tr,obs[:,1]))/(norm*obsnorm)
            score.append(corr)
        score=np.asarray(score)
        phase_ranking=np.argsort(-score)
        # La línea base es el índice con frecuencia más próxima al máximo FFT.
        freq_ranking=np.argsort(abs(f[inds]-fhat))
        predicted_phase=int(inds[phase_ranking[0]])+1
        predicted_frequency=int(inds[freq_ranking[0]])+1
        in_candidates=bool(np.any(inds==i)); present+=in_candidates
        hitp+=predicted_phase==i+1; hitf+=predicted_frequency==i+1
        top5p+=in_candidates and bool(np.any(inds[phase_ranking[:5]]==i))
        top5f+=in_candidates and bool(np.any(inds[freq_ranking[:5]]==i))
        results.append([i+1,predicted_frequency,predicted_phase,int(in_candidates),round(float(fhat),6),round(float(score[phase_ranking[0]]),6)])
        if (i+1)%250==0: print(f'Analizadas {i+1}/{count} notas',flush=True)
    report={'archivo':str(pathlib.Path(args.wav).name),'notas_evaluadas':count,'candidatos_por_nota':K,
        'porcentaje_simbolo_verdadero_en_candidatos':100*present/count,
        'exactitud_frecuencia_pct':100*hitf/count,'exactitud_fase_estereo_pct':100*hitp/count,
        'top5_frecuencia_pct':100*top5f/count,'top5_fase_estereo_pct':100*top5p/count,
        'diferencia_puntos_porcentuales':100*(hitp-hitf)/count,
        'protocolo':'Segmentación asistida por duraciones del CSV, codebook compartido de 10000 frecuencias y fases; ranking local de K candidatos según máximo FFT.',
        'limitaciones':'Las fases de referencia provienen de la partitura: no se recuperan las gamma originales en forma unívoca; el candidate recall limita exactitud máxima. El decodificador no es ciego. Evaluar robustez con ruido y desfase es trabajo posterior.'}
    out=pathlib.Path(args.out)
    with out.with_suffix('.csv').open('w',encoding='utf-8',newline='') as h:
        w=csv.writer(h);w.writerow(['indice_real_solo_para_evaluacion','predicho_solo_frecuencia','predicho_frecuencia_y_fase','real_en_candidatos','frecuencia_estimacion_hz','correlacion_mejor']); w.writerows(results)
    out.with_suffix('.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
