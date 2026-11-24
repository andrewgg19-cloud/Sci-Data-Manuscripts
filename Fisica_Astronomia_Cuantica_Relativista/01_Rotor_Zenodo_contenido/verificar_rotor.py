from pathlib import Path
import csv, json
import numpy as np
def spectrum(N,q,eta):
    n=np.arange(-N,N+1,dtype=float)
    kinetic=n*n if eta==0 else 2*n*n/(np.sqrt(1+eta*eta*n*n)+1)
    H=np.diag(kinetic+q/2)
    for j in range(len(n)-4): H[j,j+4]=H[j+4,j]=-q/4
    ground=np.linalg.eigvalsh(H)[0]
    sel=np.flatnonzero((n.astype(int)-2)%4==0)
    pair=np.linalg.eigvalsh(H[np.ix_(sel,sel)])[:2]
    return np.array([ground,pair[0],pair[1],pair[1]-pair[0]])
rows=[]
for eta in [0,.1,.3]:
    for q in [.1,1.,4.]:
        a=spectrum(32,q,eta); b=spectrum(64,q,eta)
        delta=float(np.max(np.abs(a-b)))
        assert delta<1e-9
        rows.append([eta,q,*b,delta])
out=Path(__file__).resolve().parent
with (out/'rotor_resultados.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['eta','V0_over_ER','Eground_over_ER','Eminus_over_ER','Eplus_over_ER','gap_over_ER','basis_difference']);w.writerows(rows)
# Verify the exact scale exponent by centered log differences.
errs=[]
for z in np.logspace(-3,3,61):
    h=1e-5
    def kinetic(s):
        u=z*np.exp(-s)
        return u*u/(np.sqrt(1+u*u)+1)
    numerical=(np.log(kinetic(h))-np.log(kinetic(-h)))/(2*h)
    exact=-1-1/np.sqrt(1+z*z)
    errs.append(abs(numerical-exact))
assert max(errs)<1e-7
(out/'verificacion_rotor.json').write_text(json.dumps({'max_exponent_error':max(errs),'max_basis_difference':max(r[-1] for r in rows),'scope':'Internal numerical checks; not experimental validation'},indent=2))
print('Rotor: checks passed')
