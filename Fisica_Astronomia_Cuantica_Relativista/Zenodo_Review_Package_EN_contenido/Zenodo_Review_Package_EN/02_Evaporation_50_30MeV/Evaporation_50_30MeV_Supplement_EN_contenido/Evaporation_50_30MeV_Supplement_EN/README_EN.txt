REVIEW SUPPLEMENT — Symmetric Evaporation and Entropy Dilution of the Baryon Excess between 50 and 30 MeV
Author: Andrés Germán García
Manuscript revision: 18 October 2026
Packaging date: 19 October 2026

CONTENTS AND COMPILATION
evaporation/ contains the English LaTeX source, figures, numerical programs,
fixed catalogs, archived CSV/JSON results, and third-party license notices.
audit/ contains paper-specific audit extracts and execution logs.
Run python build_english.py from this supplement's root with pdfLaTeX installed.
For Overleaf, upload the contents of evaporation/ and select paper_en.tex.
The English PDF is supplied separately alongside this supplement.

NUMERICAL REPRODUCTION
Use a working copy: numerical programs overwrite their own outputs.
Recorded environment: Linux; Python 3.12.14; NumPy 2.3.5;
SciPy 1.17.0; Matplotlib 3.10.8. Original requirements are retained.
From evaporation, run in this order:
  python simular.py
  python ajustar_exceso_final.py
  python robustez_hrg/ejecutar_robustez.py
  python robustez_hrg/verificar_fuentes.py
  python robustez_hrg/verificar_multicruce.py
  python make_figures_en.py

AUDIT SCOPE
All 36 compared CSV files (38,496 rows) were reproduced. Repeated execution establishes numerical reproducibility, not an independent reimplementation of the dynamics or observational validation. Neutrality constraints were tested in separate equilibrium calculations.
Local catalog hashes were checked; remote commit authenticity was not established.
The archive retains original computational filenames and some Spanish notes.
The original numerical programs, data, and manuscript sources are unchanged.
Paper-specific audit extracts omit the unrelated residual-manuscript diagnostic.
The HRG-only quadrature script, when present, is an explicitly labeled adaptation.
Archived manifest checks refer to the earlier source package, not this archive;
SHA256SUMS.txt identifies the present supplement.

PUBLICATION STATUS
Prepared for author review. This package does not assert a Zenodo upload,
DOI registration, peer review, or editorial acceptance.
See RIGHTS_REVIEW.txt before public deposit.
