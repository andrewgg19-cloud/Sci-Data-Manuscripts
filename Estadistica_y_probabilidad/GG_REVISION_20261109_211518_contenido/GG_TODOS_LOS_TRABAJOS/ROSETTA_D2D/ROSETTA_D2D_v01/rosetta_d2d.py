#!/usr/bin/env python3
"""Educational offline acoustic protocol prototype, not the Odlyzko Rosetta codec.
Only generates or decodes files explicitly supplied by the operator.
"""
import argparse, math, wave, struct, zlib, json, hashlib, pathlib
FS=22050; BIT_S=0.08; N=round(FS*BIT_S); F0=1100; F1=1900
PREAMBLE=b'ROSETTA-D2D-01'
MAX_LEN=80

def pack_message(txt):
    payload=txt.encode('utf-8'); assert len(payload)<=MAX_LEN, 'Message too long (80 bytes max)'
    return PREAMBLE+len(payload).to_bytes(2,'big')+payload+zlib.crc32(payload).to_bytes(4,'big')
def bits(data):
    for b in data:
        for shift in range(7,-1,-1):yield (b>>shift)&1

def encode(txt, path):
    payload=pack_message(txt)
    samples=[]
    for bit in bits(payload):
        f=F1 if bit else F0
        for k in range(N):
            ramp=min(1.,k/160,(N-1-k)/160)
            samples.append(int(0.12*32767*ramp*math.sin(2*math.pi*f*k/FS)))
    with wave.open(str(path),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(FS);w.writeframes(struct.pack('<%dh'%len(samples),*samples))
    return {'file':str(path),'bytes':len(payload),'duration_s':round(len(samples)/FS,3),'wav_sha256':hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()}
def tonepower(samples, freq):
    # Correlation at known symbol timing
    c=s=0.
    for i,v in enumerate(samples):
        a=2*math.pi*freq*i/FS;c+=v*math.cos(a);s+=v*math.sin(a)
    return c*c+s*s

def decode(path):
    with wave.open(str(path),'rb') as w:
        if (w.getnchannels(),w.getsampwidth(),w.getframerate())!=(1,2,FS):raise ValueError('Requires mono 16-bit 22050 Hz WAV')
        raw=w.readframes(w.getnframes())
    arr=struct.unpack('<%dh'%(len(raw)//2),raw)
    nbits=len(arr)//N
    recovered=[]
    for n in range(nbits):
        v=arr[n*N:(n+1)*N]
        recovered.append(int(tonepower(v,F1)>tonepower(v,F0)))
    data=bytes(sum(recovered[i+j]<<(7-j) for j in range(8)) for i in range(0,(len(recovered)//8)*8,8))
    if not data.startswith(PREAMBLE):raise ValueError('Preamble missing: unsupported timing/noise or unrelated WAV')
    p=len(PREAMBLE);L=int.from_bytes(data[p:p+2],'big');p+=2
    if L>MAX_LEN:raise ValueError('Invalid length')
    if len(data)<p+L+4:raise ValueError('Incomplete recording')
    payload=data[p:p+L];crc=int.from_bytes(data[p+L:p+L+4],'big')
    if zlib.crc32(payload)!=crc:raise ValueError('CRC32 check FAILED; do not trust payload')
    return {'message':payload.decode('utf-8'),'integrity':'CRC32 passed (not authentication)','wav_sha256':hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()}
if __name__=='__main__':
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='command',required=True)
    en=sub.add_parser('encode');en.add_argument('--message',required=True);en.add_argument('--out',default='mensaje_prueba.wav')
    de=sub.add_parser('decode');de.add_argument('--wav',required=True)
    a=ap.parse_args()
    try:
        print(json.dumps(encode(a.message,a.out) if a.command=='encode' else decode(a.wav),indent=2,ensure_ascii=False))
    except Exception as e:ap.exit(2,f'ERROR: {e}\n')
