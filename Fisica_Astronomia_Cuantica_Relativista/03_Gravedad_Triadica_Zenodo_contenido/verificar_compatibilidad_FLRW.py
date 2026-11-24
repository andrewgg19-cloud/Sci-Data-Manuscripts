from pathlib import Path
import json
import sympy as S
t,p,k,t0=S.symbols('t p k t0', positive=True)
a=S.log(3)
F=t/t0
H=p/t
s=S.log(t/t0)/a
sd=S.diff(s,t)
Z=3*p*a*a*F/k
U=(3*p*p+S.Rational(3,2)*p)*F/(k*t*t)
R=6*(2*H*H+S.diff(H,t))
eq1=3*F*H*H-k*Z*sd*sd/2-k*U+3*H*S.diff(F,t)
eq2=-2*F*S.diff(H,t)-k*Z*sd*sd-S.diff(F,t,2)+H*S.diff(F,t)
Zs=S.diff(Z,t)/sd
Us=S.diff(U,t)/sd
Fs=a*F
eq3=Z*(S.diff(s,t,2)+3*H*sd)+Zs*sd*sd/2+Us-Fs*R/(2*k)
res=[S.simplify(x) for x in [eq1,eq2,eq3]]
assert res==[0,0,0]
K=12*p*p*((p-1)**2+p*p)/t**4
K0=K.subs(t,t0)
assert S.simplify(S.diff(-S.log(K/K0)/(4*a)-s,t))==0
KE=S.simplify(Z/F+3*a*a/(2*k))
assert S.simplify(KE-3*(p+S.Rational(1,2))*a*a/k)==0
result={'FLRW_residuals':[str(x) for x in res],'K':str(K),'Einstein_kinetic':str(KE),'assumptions':'flat FLRW, vacuum, t>0, p>0, UA=0, reconstructed Z and U; no baryogenesis prediction'}
Path(__file__).with_name('compatibilidad_FLRW.json').write_text(json.dumps(result,indent=2))
print('FLRW: three field equations checked symbolically')
