"""Reproduce the zero-width ideal-HRG entropy audit and publication figures.
Independent Python evaluation; Thermal-FIST C++ is not executed.
Units: GeV, GeV^3. Particle lists are frozen at the commit in provenance.json.
The legacy reduced benchmark is transcribed, not recalculated.
"""
from pathlib import Path
import csv, hashlib, json, math, platform
import numpy as np
import scipy
from scipy.special import kv, expit
from scipy.integrate import quad
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parent
TEMPERATURES = np.array([150,140,120,100,80,60,50,40], dtype=float)
LEGACY = np.array([.06208,.04328,.01686,.004305,.0005464,.00001782,.000001148,.00000001795])
PREVIOUS_FULL = np.array([.08455,.05693,.02032,.004750,.0005661,.00001795,.000001152,.00000001797])
MUON_MASS = .1056583755
COMMIT = "4086191e952285cd572ba2bbbefb2fdc55401c9b"
KMAX = 96

def parse_list(path):
    rows = []
    for line in path.read_text().splitlines():
        parts = line.split("#",1)[0].split()
        if not parts:
            continue
        if len(parts) < 14:
            raise ValueError("Malformed row: " + line)
        pdg = int(parts[0]); mass = float(parts[3]); g = float(parts[4])
        statistics = int(parts[5])
        B,Q,S,C = [int(parts[j]) for j in range(6,10)]
        # Thermal-FIST lists one member of each particle-antiparticle pair.
        anti_factor = 2 if any((B,Q,S,C)) else 1
        rows.append(dict(pdg=pdg,name=parts[1],m=mass,g=g,stat=statistics,
                         B=B,Q=Q,S=S,C=C,multiplicity=anti_factor,width=float(parts[12])))
    if len({r["pdg"] for r in rows}) != len(rows):
        raise ValueError("Duplicate PDG IDs")
    if any(r["pdg"] < 0 for r in rows):
        raise ValueError("Explicit antiparticles require different counting")
    return rows

def entropy_over_T3(mass, g, stat, T, kmax=KMAX):
    x = mass/T
    if x == 0:
        return 2*math.pi**2/45*g*(7/8 if stat == 1 else 1)
    k = np.arange(1,kmax+1, dtype=float)
    signs = (-1.)**(k+1) if stat == 1 else np.ones_like(k)
    return g*x*x/(2*math.pi**2)*np.sum(signs*(4*kv(2,k*x)/(k*k)+x*kv(1,k*x)/k))

def integral_entropy_over_T3(mass,g,stat,T):
    x = mass/T
    def integrand(q):
        E = math.hypot(q,x)
        if E == 0: return 0.
        occ = expit(-E) if stat == 1 else (0. if E > 700 else 1/math.expm1(E))
        return q*q*(E+q*q/(3*E))*occ
    value,error = quad(integrand,0,np.inf,epsabs=1e-15,epsrel=5e-12,limit=200)
    return g/(2*math.pi**2)*value

def light_over_T3(T):
    # gamma (g=2), e+- (g=4, massless), 3 neutrino flavors plus antiparticles (g=6).
    photon = 2*math.pi**2/45*2
    electron = 2*math.pi**2/45*4*7/8
    neutrino = 2*math.pi**2/45*6*7/8
    muon = entropy_over_T3(MUON_MASS,4,1,T)
    return photon+electron+neutrino+muon

def evaluate(rows,T,kmax=KMAX):
    contributions = [(r,entropy_over_T3(r["m"],r["g"]*r["multiplicity"],r["stat"],T,kmax)) for r in rows if r["g"]>0]
    B = sum(x for r,x in contributions if r["B"] != 0)
    M = sum(x for r,x in contributions if r["B"] == 0)
    light = light_over_T3(T)
    total = B+M+light
    return dict(s_B_GeV3=B*T**3,s_meson_GeV3=M*T**3,s_had_GeV3=(B+M)*T**3,
                s_light_GeV3=light*T**3,s_total_GeV3=total*T**3,
                f=B/total,f_had=B/(B+M),g_star_s=45*total/(2*math.pi**2))

def write_csv(path,rows):
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

def zero_mu_baryon_number(rows,T):
    k=np.arange(1,KMAX+1,dtype=float)
    total=0.
    for r in rows:
        if r['g']<=0 or r['B']==0: continue
        x=r['m']/T
        signs=(-1.)**(k+1) if r['stat']==1 else np.ones_like(k)
        total += r['g']*r['multiplicity']*x*x/(2*math.pi**2)*np.sum(signs*kv(2,k*x)/k)*T**3
    return total

def main():
    (ROOT/"data").mkdir(exist_ok=True)
    catalogs = {}
    provenance = dict(commit=COMMIT,analysis_date="2026-10-07",
                      implementation="Independent zero-width ideal-HRG calculation in Python; not Thermal-FIST execution",
                      units="GeV; entropy density in GeV^3",
                      assumptions=dict(mu_B=0,mu_Q=0,mu_S=0,common_temperature=True,
                                       resonance_widths=False,interaction_corrections=False,
                                       electrons_massless=True,muon_mass_GeV=MUON_MASS,neutrino_helicities=6,
                                       charm=False,nuclei=False,bottom=False),
                      legacy_reference={'citation': 'Garcia (2026), unpublished working manuscript v0.9', 'original_filename': 'avance_paper_residuo_bario_antibario_v0_9.pdf', 'sha256': '58da2a0e29e455c454b4966582a6acc8db4494d89c4296a2bc1cc378373571dc', 'status': 'Transcribed values only; species inventory and original calculation code unavailable', 'significant_digits': 4},
                      kmax=KMAX,python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,catalogs={})
    for key in ["PDG2014","PDG2020","PDG2025"]:
        path=ROOT/"catalogs"/(key+"_list.dat")
        rows=parse_list(path); catalogs[key]=rows
        provenance["catalogs"][key]=dict(
            url=f"https://github.com/vlvovch/Thermal-FIST/blob/{COMMIT}/input/list/{key}/list.dat",
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            listed_rows=len(rows),expanded_including_zero_g=sum(r["multiplicity"] for r in rows),
            active_rows=sum(r["g"]>0 for r in rows),
            active_expanded=sum(r["multiplicity"] for r in rows if r["g"]>0),
            active_baryons_expanded=sum(r["multiplicity"] for r in rows if r["g"]>0 and r["B"]!=0))
    outputs=[]; details=[]
    for j,tm in enumerate(TEMPERATURES):
        result={key:evaluate(rows,tm/1000) for key,rows in catalogs.items()}
        f25=result["PDG2025"]["f"]
        outputs.append(dict(T_MeV=tm,legacy_reduced_fraction=LEGACY[j],
                            PDG2014_fraction=result["PDG2014"]["f"],PDG2020_fraction=result["PDG2020"]["f"],
                            PDG2025_fraction=f25,reconstruction_pct=100*LEGACY[j]/f25,
                            relative_deficit_pct=100*(1-LEGACY[j]/f25),
                            difference_percentage_points=100*(f25-LEGACY[j]),
                            catalog_spread_percentage_points=100*(max(r["f"] for r in result.values())-min(r["f"] for r in result.values())),
                            ))
        for key,d in result.items():
            details.append(dict(T_MeV=tm,catalog=key,**d))
    write_csv(ROOT/"data"/"comparison_hrg.csv",outputs)
    write_csv(ROOT/"data"/"entropy_densities.csv",details)
    write_csv(ROOT/"data"/"legacy_reduced_benchmark.csv",[dict(T_MeV=t,f_reduced=x,provenance="Transcribed from Garcia v0.9; original species list/code unavailable") for t,x in zip(TEMPERATURES,LEGACY)])
    f25=np.array([x["PDG2025_fraction"] for x in outputs])
    l0=np.log10(LEGACY); l1=np.log10(f25); diff=l0-l1
    summary=dict(
        pearson_log10=float(np.corrcoef(l0,l1)[0,1]),
        spearman_rank=float(spearmanr(LEGACY,f25).statistic),
        rmse_log10=float(np.sqrt(np.mean(diff*diff))),
        maximum_relative_deficit_pct=float(100*np.max(1-LEGACY/f25)),
        endpoint_ratio_reduced=float(LEGACY[-1]/LEGACY[0]),
        endpoint_ratio_PDG2025=float(f25[-1]/f25[0]),
        suppression_orders_reduced=float(np.log10(LEGACY[0]/LEGACY[-1])),
        suppression_orders_PDG2025=float(np.log10(f25[0]/f25[-1])),
        previous_full_series_max_relative_difference=float(np.max(abs(f25/PREVIOUS_FULL-1))),
        precision_warning="Legacy benchmark has four significant digits; ratios are descriptive, not statistical accuracy.",
    )
    diag=[]
    YB=6.12e-10/7.04
    for tm in [150.,40.]:
        d=evaluate(catalogs['PDG2025'],tm/1000)
        n0=zero_mu_baryon_number(catalogs['PDG2025'],tm/1000)
        alpha=math.asinh(YB*d['s_total_GeV3']/n0)
        correction=math.cosh(alpha)-n0/d['s_B_GeV3']*alpha*math.sinh(alpha)
        diag.append(dict(T_MeV=tm,n_B_plus_anti_zero_mu_GeV3=n0,
                         Y_sum_zero_mu=n0/d['s_total_GeV3'],muB_over_T_MB_diagnostic=alpha,
                         approximate_baryon_entropy_change_pct=100*(correction-1)))
    summary['asymmetry_diagnostic_MB']=diag
    validation={}
    for key,rows in catalogs.items():
        max_delta=0
        for tm in TEMPERATURES:
            a=evaluate(rows,tm/1000,96);b=evaluate(rows,tm/1000,192)
            max_delta=max(max_delta,abs(a["f"]/b["f"]-1))
        validation[key]={"maximum_relative_fraction_change_k96_to192":max_delta}
    test_rows=[r for r in catalogs["PDG2025"] if r["g"]>0 and r["pdg"] in [111,211,2212,2112]]
    validation["momentum_integrals"]=[]
    for tm in [150.,40.]:
        for r in test_rows+[dict(pdg=13,m=MUON_MASS,g=4,stat=1,multiplicity=1)]:
            a=entropy_over_T3(r["m"],r["g"]*r["multiplicity"],r["stat"],tm/1000)
            b=integral_entropy_over_T3(r["m"],r["g"]*r["multiplicity"],r["stat"],tm/1000)
            validation["momentum_integrals"].append(dict(T_MeV=tm,pdg=r["pdg"],relative_difference=abs(a/b-1)))
    validation["max_integral_relative_difference"]=max(x["relative_difference"] for x in validation["momentum_integrals"])
    # Entropy in the nonrelativistic limit: s/n = m/T + 5/2; s ~ T^3 x^(5/2) e^-x.
    validation["electron_massless_error"]=[]
    for tm in [150.,40.]:
        exact=integral_entropy_over_T3(.00051099895,4,1,tm/1000)
        approx=entropy_over_T3(0,4,1,tm/1000)
        validation["electron_massless_error"].append(dict(T_MeV=tm,relative_entropy_error=approx/exact-1))
    assert validation["max_integral_relative_difference"] < 1e-8
    assert all(d["maximum_relative_fraction_change_k96_to192"] < 1e-10 for k,d in validation.items() if k.startswith("PDG"))
    for key in catalogs:
        series=np.array([r["f"] for r in details if r["catalog"]==key])
        assert np.all(series>0) and np.all(series<1) and np.all(np.diff(series)<0)
    (ROOT/"provenance.json").write_text(json.dumps(provenance,indent=2,ensure_ascii=False)+"\n")
    (ROOT/"data"/"summary_metrics.json").write_text(json.dumps(summary,indent=2)+"\n")
    (ROOT/"data"/"numerical_validation.json").write_text(json.dumps(validation,indent=2)+"\n")
    print(json.dumps(dict(summary=summary,catalogs=provenance["catalogs"],validation=validation,rows=outputs,at150=[r for r in details if r["T_MeV"]==150]),indent=2))

if __name__=="__main__":
    main()

