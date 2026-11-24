#!/usr/bin/env python3
"""Auditoría exhaustiva del diccionario de Rosetta (no decodificador ciego)."""
import argparse,csv,hashlib,json,math,pathlib,wave
from collections import defaultdict
import numpy as np

def main():
 p=argparse.ArgumentParser();p.add_argument('--csv',default='Rosetta_10000_partitura.csv');p.add_argument('--wav',default='Rosetta_10000_base.wav');p.add_argument('--out',default='Rosetta_auditoria_exhaustiva.json');a=p.parse_args()
 with open(a.csv,encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
 n=len(rows); assert n==10000,f'Se esperaban 10000, hay {n}'
 f=np.array([float(r['frecuencia_hz']) for r in rows]); th=np.array([float(r['fase_rad']) for r in rows]);g=np.array([float(r['gamma_odlyzko']) for r in rows]);d=np.array([float(r['duracion_s']) for r in rows]); primes=np.array([int(r['primo']) for r in rows])
 assert np.all(np.isfinite(f)) and np.all(np.isfinite(th)) and np.all(np.isfinite(d))
 # El diccionario contiene las frecuencias y fases a diez decimales.
 pairs=defaultdict(list)
 for i,(fi,ti) in enumerate(zip(f,th),1):pairs[(round(float(fi),10),round(float(ti)%(2*math.pi),10))].append(i)
 collisions=[v for v in pairs.values() if len(v)>1]
 freq_groups=defaultdict(list)
 for i,fi in enumerate(f,1):freq_groups[round(float(fi),10)].append(i)
 # Separaciones en parámetros escalados: descriptor diagnóstico, no norma de señales acústicas.
 from scipy.spatial import cKDTree
 xyz=np.column_stack([f/110,np.cos(th),np.sin(th)])
 dist,neighbors=cKDTree(xyz).query(xyz,k=2)
 ind=int(np.argmin(dist[:,1])); j=int(neighbors[ind,1]); gap=float(dist[ind,1]);
 # Verifica estructura esperada y procedencia en CSV (no autenticidad externa de Odlyzko).
 with wave.open(a.wav,'rb') as w:
  sample_rate=w.getframerate(); frames=w.getnframes(); channels=w.getnchannels(); width=w.getsampwidth()
 expected=int(np.maximum(8,np.rint(d*sample_rate).astype(int)).sum()+(n-1)*round(.018*sample_rate))
 wavhash=hashlib.sha256(pathlib.Path(a.wav).read_bytes()).hexdigest()
 out={
  'alcance':'Auditoria exhaustiva de 10000 entradas del diccionario y coherencia temporal del WAV; NO demuestra decodificacion inversa del audio ni recuperacion unica de gamma.',
  'entradas':n,'indices_consecutivos':all(int(r['n'])==i for i,r in enumerate(rows,1)),
  'primos_estrictamente_crecientes':bool(np.all(np.diff(primes)>0)),'gamma_estrictamente_crecientes':bool(np.all(np.diff(g)>0)),
  'frecuencia_min_hz':float(f.min()),'frecuencia_max_hz':float(f.max()),
  'pares_fase_frecuencia_exactamente_repetidos_al_redondeo_10_decimales':len(collisions),
  'ejemplos_colisiones':collisions[:10],
  'frecuencias_repetidas_al_redondeo_10_decimales':sum(len(v)-1 for v in freq_groups.values()),
  'distancia_min_descriptor_normalizado':gap,'par_mas_proximo_indices_1_based':[ind+1,j+1],
  'descriptor':'(frecuencia/110,cos(fase),sin(fase)); distancia NO equivale a distancia entre señales PCM.',
  'wav':a.wav,'wav_sha256':wavhash,'wav_frecuencia_muestreo':sample_rate,'wav_canales':channels,'wav_bytes_por_muestra':width,
  'wav_muestras_por_canal':frames,'muestras_esperadas':expected,'duracion_s':frames/sample_rate,
  'longitud_coincide_con_csv_y_pausas':frames==expected,
  'pendiente':'Decodificar todas las notas sin usar el índice verdadero, con controles negativos y desplazamientos desconocidos; validar independencia de los datos de entrada.'}
 pathlib.Path(a.out).write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
