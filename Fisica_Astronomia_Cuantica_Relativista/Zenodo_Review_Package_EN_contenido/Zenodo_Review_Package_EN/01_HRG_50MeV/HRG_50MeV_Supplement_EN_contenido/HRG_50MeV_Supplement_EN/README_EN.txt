REVIEW SUPPLEMENT — Baryon-Antibaryon Reconstruction at 50 MeV: Rest Masses and Cosmological Abundances
Author: Andrés Germán García
Manuscript revision: 18 October 2026
Packaging date: 19 October 2026

CONTENTS AND COMPILATION
hrg/ contains the English LaTeX source, figures, numerical programs,
fixed catalogs, archived CSV/JSON results, and third-party license notices.
audit/ contains paper-specific audit extracts and execution logs.
Run python build_english.py from this supplement's root with pdfLaTeX installed.
For Overleaf, upload the contents of hrg/ and select paper_en.tex.
The English PDF is supplied separately alongside this supplement.

NUMERICAL REPRODUCTION
Use a working copy: numerical programs overwrite their own outputs.
Recorded environment: Linux; Python 3.12.14; NumPy 2.3.5;
SciPy 1.17.0; Matplotlib 3.10.8. Original requirements are retained.
From hrg/calculos_50MeV_cruce, run:
  python comparar_50MeV.py
From the supplement root, run the additional quadrature check:
  python audit/momentum_integral_check.py --hrg-root hrg/calculos_50MeV_cruce --output new_check.json
From hrg, make_final_assets.py regenerates the figures and tables.

AUDIT SCOPE
Five compared CSV files (1,419 rows) and 24 internal checks were reproduced. The additional quadrature uses the same catalog, temperatures and solved chemical potentials at two states; it is not an independent cosmological inference.
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
