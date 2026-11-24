# Canonical reproduction

Install the pinned dependencies and execute:

```bash
python -m pip install -r requirements.txt
python reproduce.py
```

The command uses the included first 15 positive critical-line ordinates, runs
the canonical finite audit at `T=50` and `P=100`, and then checks the resulting
JSON with `verify_reproducibility.py`.

Expected final lines:

```text
TAMPER SELF-TEST PASSED: global_RH_proved=true was rejected
VERIFICATION PASSED
- finite count identity checked at T=50
- finite prime channel checked at P=100
- bridge remains NV_unproved_methodological_lemma
- every global_RH_proved field remains false
Canonical output: canonical_audit_reproduced.json
```

The total count `N_plus(50)=10` remains an externally supplied input. The
package checks its consistency with the ten included ordinates below `T=50`,
but does not independently authenticate that total count. The computation is
finite and does not prove RH.
