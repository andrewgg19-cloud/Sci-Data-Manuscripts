#!/usr/bin/env python3
"""Recupera los datos y audios grandes y verifica su integridad SHA-256."""
import argparse,gzip,hashlib,json,pathlib,shutil,tempfile
ROOT=pathlib.Path(__file__).resolve().parent
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--carpeta',help='Recuperar solo rutas que contengan este texto')
    args=parser.parse_args()
    records=json.loads((ROOT/'catalogo/manifest.json').read_text(encoding='utf-8'))
    count=0
    for record in records:
        if record['storage']!='gzip-parts' or (args.carpeta and args.carpeta not in record['path']):continue
        target=ROOT/record['path']; target.parent.mkdir(parents=True,exist_ok=True)
        if target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest()==record['sha256']:
            print('Verificado:',record['path']);continue
        with tempfile.TemporaryFile() as packed:
            for part in record['parts']:
                data=(ROOT/part['path']).read_bytes()
                if len(data)!=part['size'] or hashlib.sha256(data).hexdigest()!=part['sha256']:
                    raise RuntimeError('Fragmento dañado: '+part['path'])
                packed.write(data)
            packed.seek(0)
            with gzip.GzipFile(fileobj=packed) as src,target.with_suffix(target.suffix+'.tmp').open('wb') as dst:shutil.copyfileobj(src,dst)
        temp=target.with_suffix(target.suffix+'.tmp')
        if temp.stat().st_size!=record['size'] or hashlib.sha256(temp.read_bytes()).hexdigest()!=record['sha256']:
            temp.unlink();raise RuntimeError('Integridad incorrecta: '+record['path'])
        temp.replace(target);count+=1;print('Recuperado:',record['path'])
    print('Archivos recuperados:',count)
if __name__=='__main__':main()
