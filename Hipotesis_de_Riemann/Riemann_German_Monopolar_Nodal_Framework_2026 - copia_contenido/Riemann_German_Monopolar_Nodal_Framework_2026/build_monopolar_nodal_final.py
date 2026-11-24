#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import textwrap
import zipfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source_polar_integration_33p.pdf"
FIG1 = ROOT / "figures" / "fig01_aplanamiento_geometrico.png"
FIG2 = ROOT / "figures" / "fig02_interferencia_nodal.png"
TITLE_PDF = ROOT / "_title_page.pdf"
APPENDIX_PDF = ROOT / "_appendix_f_nodal_operator.pdf"
OUTPUT_PDF = ROOT / "Riemann_German_Monopolar_Nodal_Framework_2026.pdf"
MANIFEST = ROOT / "MANIFEST_MONOPOLAR_NODAL_FINAL.json"
ZIP_OUT = ROOT.parent / "Riemann_German_Monopolar_Nodal_Framework_2026.zip"
EQ_DIR = ROOT / "_equations"

TITLE = (
    "Monopolar Nodal Operator Framework for the Riemann Hypothesis: "
    "Symmetry, Flattening, and Prime-Channel Criteria"
)
AUTHOR = "Germán García Andrés"
EDITION = "Revised nodal-operator edition - September 2026"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def register_fonts() -> dict[str, str]:
    fonts = {
        "regular": r"C:\Windows\Fonts\times.ttf",
        "bold": r"C:\Windows\Fonts\timesbd.ttf",
        "italic": r"C:\Windows\Fonts\timesi.ttf",
        "bolditalic": r"C:\Windows\Fonts\timesbi.ttf",
    }
    names = {
        "regular": "TimesNewRoman",
        "bold": "TimesNewRoman-Bold",
        "italic": "TimesNewRoman-Italic",
        "bolditalic": "TimesNewRoman-BoldItalic",
    }
    for key, font_path in fonts.items():
        pdfmetrics.registerFont(TTFont(names[key], font_path))
    return names


FONTS = register_fonts()


def wrapped_lines(text: str, width: int) -> list[str]:
    lines: list[str] = []
    for para in text.split("\n"):
        para = para.strip()
        if not para:
            lines.append("")
        else:
            lines.extend(textwrap.wrap(para, width=width, break_long_words=False, break_on_hyphens=False))
    return lines


def draw_wrapped(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    width_chars: int,
    size: float = 11,
    leading: float | None = None,
    font: str | None = None,
    fill=colors.black,
) -> float:
    font = font or FONTS["regular"]
    leading = leading or size * 1.28
    c.setFillColor(fill)
    c.setFont(font, size)
    for line in wrapped_lines(text, width_chars):
        if line:
            c.drawString(x, y, line)
        y -= leading
    return y


def draw_centered_wrapped(
    c: canvas.Canvas,
    text: str,
    x_mid: float,
    y: float,
    width_chars: int,
    size: float,
    leading: float | None = None,
    font: str | None = None,
    fill=colors.black,
) -> float:
    font = font or FONTS["regular"]
    leading = leading or size * 1.20
    c.setFillColor(fill)
    c.setFont(font, size)
    for line in wrapped_lines(text, width_chars):
        if line:
            c.drawCentredString(x_mid, y, line)
        y -= leading
    return y


def draw_equation(c: canvas.Canvas, text: str, x_mid: float, y: float, size: float = 14) -> float:
    c.setFillColor(colors.HexColor("#111111"))
    c.setFont(FONTS["italic"], size)
    c.drawCentredString(x_mid, y, text)
    return y - size * 1.55


def draw_math(c: canvas.Canvas, latex: str, x_mid: float, y: float, max_w: float, fontsize: float = 16) -> float:
    EQ_DIR.mkdir(parents=True, exist_ok=True)
    name = hashlib.sha256((latex + str(fontsize)).encode("utf-8")).hexdigest()[:16] + ".png"
    path = EQ_DIR / name
    if not path.exists():
        fig = plt.figure(figsize=(8.8, 0.62), dpi=220)
        fig.patch.set_alpha(0)
        fig.text(0.5, 0.5, latex, ha="center", va="center", fontsize=fontsize, color="#111111")
        fig.savefig(path, transparent=True, bbox_inches="tight", pad_inches=0.045)
        plt.close(fig)
    with Image.open(path) as image:
        img_w, img_h = image.size
    scale = min(max_w / img_w, 0.46 * inch / img_h)
    draw_w = img_w * scale
    draw_h = img_h * scale
    c.drawImage(
        str(path),
        x_mid - draw_w / 2,
        y - draw_h,
        width=draw_w,
        height=draw_h,
        preserveAspectRatio=True,
        mask="auto",
    )
    return y - draw_h - 0.10 * inch


def header(c: canvas.Canvas, label: str, page: str) -> None:
    width, height = letter
    c.setFont("Helvetica", 8.5)
    c.setFillColor(colors.HexColor("#555555"))
    c.drawString(0.72 * inch, height - 0.48 * inch, label)
    c.drawRightString(width - 0.72 * inch, height - 0.48 * inch, page)
    c.setStrokeColor(colors.HexColor("#d0d0d0"))
    c.line(0.72 * inch, height - 0.58 * inch, width - 0.72 * inch, height - 0.58 * inch)


def make_title_page() -> None:
    width, height = letter
    c = canvas.Canvas(str(TITLE_PDF), pagesize=letter)
    c.setTitle(TITLE)
    c.setAuthor(AUTHOR)
    c.setSubject("Revised nodal-operator edition")

    y = height - 1.50 * inch
    y = draw_centered_wrapped(c, TITLE, width / 2, y, 58, 20, 24, FONTS["regular"])
    y -= 0.18 * inch
    c.setFont(FONTS["regular"], 13)
    c.drawCentredString(width / 2, y, AUTHOR)
    y -= 0.24 * inch
    c.drawCentredString(width / 2, y, "Independent Researcher")
    y -= 0.34 * inch
    c.setFont(FONTS["regular"], 12)
    c.drawCentredString(width / 2, y, EDITION)

    y -= 0.60 * inch
    c.setFont(FONTS["bold"], 12.5)
    c.drawCentredString(width / 2, y, "Abstract")
    y -= 0.28 * inch
    abstract = (
        "This revised edition preserves the mathematical body of the Polar Integration manuscript and "
        "adds a final nodal-operator block. The monopolar operator is not introduced here as a new object: "
        "it is the radial L=0 operator architecture already formulated in the original operator appendix. "
        "The new contribution isolates the local nodal mechanism generated by an amplitude-phase wave, an "
        "involutive angular interpretation, phase opposition, and vanishing transverse quadratic residue. "
        "Under these stated hypotheses the superposition cancels exactly, y+(-y)=0. This is an exact local "
        "cancellation theorem, not by itself an unconditional proof of the Riemann hypothesis."
    )
    y = draw_wrapped(c, abstract, 1.22 * inch, y, 92, 11.2, 14, FONTS["regular"])
    y -= 0.12 * inch
    y = draw_math(c, r"$\psi(\theta)=F(\theta)e^{iG_A(\theta)}$", width / 2, y, width - 2.3 * inch, 17)
    y = draw_math(
        c,
        r"$D(z)=E(z)\,\xi\!\left(\frac{1}{2}+z\right),\qquad E(z)\ne 0$",
        width / 2,
        y,
        width - 2.3 * inch,
        17,
    )

    y -= 0.18 * inch
    c.setFont(FONTS["bold"], 12.5)
    c.drawString(1.22 * inch, y, "Revision map")
    y -= 0.24 * inch
    revision = (
        "The title has been changed to emphasize the actual architecture of the manuscript: monopolar "
        "operator, nodal flattening, symmetry, and prime-channel criteria. The preserved source body follows "
        "after this page, beginning with its original Section 1. The final pages add Appendix F and a revised "
        "final conclusion. The logical standard remains unchanged: finite certificates, local cancellation "
        "identities, and operator analogies are not promoted to a global theorem unless the required "
        "arithmetic spectral realization is proved independently."
    )
    draw_wrapped(c, revision, 1.22 * inch, y, 92, 10.8, 13.5, FONTS["regular"])

    c.setFont(FONTS["regular"], 9.5)
    c.setFillColor(colors.HexColor("#555555"))
    c.drawCentredString(width / 2, 0.70 * inch, "Title page replaced; original pages 2-33 are preserved.")
    c.showPage()
    c.save()


def draw_title(c: canvas.Canvas, title: str, y: float, page: str) -> float:
    header(c, "Appendix F - Monopolar Nodal Channel", page)
    c.setFillColor(colors.HexColor("#111111"))
    c.setFont(FONTS["bold"], 16)
    c.drawString(0.78 * inch, y, title)
    return y - 0.35 * inch


def make_appendix() -> None:
    width, height = letter
    c = canvas.Canvas(str(APPENDIX_PDF), pagesize=letter)
    c.setTitle("Appendix F - General Nodal Theorem")
    c.setAuthor(AUTHOR)

    # Page F1
    y = draw_title(c, "Appendix F. General Nodal Theorem", height - 0.95 * inch, "F1")
    text = (
        "The preceding manuscript already contains the monopolar operator architecture: the radial L=0 mode, "
        "its collective Hamiltonian, the involution J:x -> -x, and the comparison with the graph symmetry "
        "operator P_R. The present appendix does not introduce a second operator. It adds the local nodal "
        "theorem that explains how an exact cancellation channel is formed once the angular wave is interpreted "
        "through an involutive operator O_theta."
    )
    y = draw_wrapped(c, text, 0.78 * inch, y, 95, 10.8, 13.4, FONTS["regular"])
    y -= 0.10 * inch
    c.setFont(FONTS["bold"], 12.5)
    c.drawString(0.78 * inch, y, "Definition F.1. Flattened angular channel.")
    y -= 0.24 * inch
    definition = (
        "Let Theta be a local parameter space and let psi(theta)=F(theta)e^{iG_A(theta)} be an amplitude-phase "
        "state with real amplitude F(theta). Let O_theta:Theta -> Theta be an involution, O_theta^2=I. Let "
        "y:Theta -> R denote the local transverse coordinate associated with a chosen flattening plane L. The "
        "channel is flattened and nodal when y(O_theta theta)=-y(theta)."
    )
    y = draw_wrapped(c, definition, 0.78 * inch, y, 95, 10.7, 13.4, FONTS["regular"])
    y -= 0.05 * inch
    y = draw_math(
        c,
        r"$\psi(\theta)=F(\theta)e^{iG_A(\theta)},\qquad O_\theta^2=I,\qquad y(O_\theta\theta)=-y(\theta)$",
        width / 2,
        y,
        width - 1.5 * inch,
        14.5,
    )
    y -= 0.08 * inch
    c.setFont(FONTS["bold"], 12.5)
    c.drawString(0.78 * inch, y, "Definition F.2. Meaning of Tr_q[X^2]=0.")
    y -= 0.24 * inch
    definition2 = (
        "In this appendix Tr_q[X^2]=0 is used as a stated flattening hypothesis: the transverse quadratic "
        "residue of the selected channel vanishes. If Tr_q is later specified as a positive Hilbert-space "
        "trace and X is self-adjoint, this condition is stronger and forces the corresponding quadratic "
        "component to vanish. If Tr_q is indefinite, renormalized, or projected, its domain and positivity "
        "properties must be stated before it can be used as a global spectral criterion."
    )
    draw_wrapped(c, definition2, 0.78 * inch, y, 95, 10.7, 13.4, FONTS["regular"])
    c.showPage()

    # Page F2
    y = draw_title(c, "Theorem F.3. General nodal cancellation", height - 0.95 * inch, "F2")
    theorem = (
        "Let psi(theta)=F(theta)e^{iG_A(theta)} be an amplitude-phase state on Theta. Assume O_theta^2=I, "
        "y(O_theta theta)=-y(theta), F(O_theta theta)=F(theta), and "
        "G_A(O_theta theta)=G_A(theta)+pi mod 2pi. If the selected channel also satisfies the flattening "
        "condition Tr_q[X^2]=0, interpreted as vanishing transverse quadratic residue, then the symmetric "
        "superposition along the O_theta-pair satisfies psi(theta)+psi(O_theta theta)=0. Equivalently, at the "
        "level of the real transverse coordinate, y(theta)+y(O_theta theta)=y+(-y)=0."
    )
    y = draw_wrapped(c, theorem, 0.78 * inch, y, 95, 10.7, 13.4, FONTS["regular"])
    y -= 0.06 * inch
    y = draw_math(
        c,
        r"$O_\theta^2=I,\quad O_\theta y=-y,\quad \Delta G_A=\pi,\quad \operatorname{Tr}_q[X^2]=0\Rightarrow y+(-y)=0$",
        width / 2,
        y,
        width - 1.4 * inch,
        14.5,
    )
    c.setFont(FONTS["bold"], 12.5)
    c.drawString(0.78 * inch, y, "Proof.")
    y -= 0.24 * inch
    proof = (
        "By amplitude invariance and phase opposition, psi(O_theta theta)=F(theta)e^{i(G_A(theta)+pi)}="
        "-F(theta)e^{iG_A(theta)}=-psi(theta). Therefore psi(theta)+psi(O_theta theta)=0. The coordinate "
        "identity follows directly from the imposed involution on the transverse coordinate: "
        "y(theta)+y(O_theta theta)=y(theta)-y(theta)=0. The condition Tr_q[X^2]=0 records that no quadratic "
        "transverse residue is retained in the flattened channel. Thus the cancellation is exact within the "
        "stated local model."
    )
    y = draw_wrapped(c, proof, 0.78 * inch, y, 95, 10.7, 13.4, FONTS["regular"])
    y -= 0.06 * inch
    c.setFont(FONTS["bold"], 12.5)
    c.drawString(0.78 * inch, y, "Remark F.4. Local theorem, not automatic global closure.")
    y -= 0.24 * inch
    remark = (
        "The theorem proves an exact nodal cancellation once the channel, involution, amplitude invariance, "
        "phase opposition, and residue condition have been fixed. It does not prove that every nontrivial zero "
        "of zeta activates this channel. It also does not prove that the operator determinant is xi. Those are "
        "the global arithmetic and spectral tasks."
    )
    draw_wrapped(c, remark, 0.78 * inch, y, 95, 10.7, 13.4, FONTS["regular"])
    c.showPage()

    # Page F3
    y = draw_title(c, "Figure F1. Aplanamiento local", height - 0.95 * inch, "F3")
    fig_caption = (
        "A parabolic or flattened channel is represented by a signed height h_L relative to L. The identity "
        "h_L(R_L q)=-h_L(q) gives exact local antisymmetry."
    )
    y = draw_wrapped(c, fig_caption, 0.78 * inch, y, 95, 10.6, 13.2, FONTS["regular"])
    draw_image(c, FIG1, 0.60 * inch, y - 0.10 * inch, width - 1.20 * inch, 5.75 * inch)
    c.showPage()

    # Page F4
    y = draw_title(c, "Figure F2. Interferencia destructiva", height - 0.95 * inch, "F4")
    fig_caption2 = (
        "Equal amplitudes with phase difference pi cancel exactly: h+e^{i pi}h=0. This visualizes the nodal "
        "channel of the theorem."
    )
    y = draw_wrapped(c, fig_caption2, 0.78 * inch, y, 95, 10.6, 13.2, FONTS["regular"])
    draw_image(c, FIG2, 0.60 * inch, y - 0.10 * inch, width - 1.20 * inch, 5.75 * inch)
    c.showPage()

    # Page F5
    y = draw_title(c, "Final Revised Conclusion", height - 0.95 * inch, "F5")
    conclusion1 = (
        "The manuscript now contains three logically linked layers. First, the analytic and graph symmetries "
        "isolate the critical fixed set through the involution R(s)=1-conjugate(s) and the induced graph "
        "operator P_R. Second, the monopolar operator architecture supplies an operator-spectral language based "
        "on a radial L=0 mode, an involution, a fixed sector, and commutation with the corresponding spectral "
        "generator. Third, the nodal theorem supplies the local cancellation mechanism:"
    )
    y = draw_wrapped(c, conclusion1, 0.78 * inch, y, 95, 10.7, 13.4, FONTS["regular"])
    y -= 0.08 * inch
    y = draw_math(
        c,
        r"$\psi=F(\theta)e^{iG_A(\theta)},\quad O_\theta^2=I,\quad O_\theta y=-y,\quad \Delta G_A=\pi$",
        width / 2,
        y,
        width - 1.4 * inch,
        13.8,
    )
    y = draw_math(
        c,
        r"$\operatorname{Tr}_q[X^2]=0\Rightarrow y+(-y)=0$",
        width / 2,
        y,
        width - 1.4 * inch,
        14.0,
    )
    conclusion2 = (
        "Thus the operator is not missing. The new theorem is attached to the existing monopolar architecture "
        "and explains how the flattened channel becomes nodal. What remains as the decisive closure condition "
        "is the arithmetic spectral realization D(z)=E(z)xi(1/2+z), E(z) not zero, derived from the prime "
        "channel and compatible with the passive-adjoint identity JAJ^{-1}=-A*. If that bridge is proved without "
        "assuming RH or inserting the zeros by definition, the passive-adjoint theorem confines the realized "
        "spectral parameters to the imaginary axis and therefore yields Re(rho)=1/2 for the realized nontrivial "
        "zeros. Until that bridge is proved, the present edition is a coherent nodal-operator framework with "
        "exact local cancellations and explicit global proof obligations."
    )
    y = draw_wrapped(c, conclusion2, 0.78 * inch, y, 95, 10.7, 13.4, FONTS["regular"])
    y -= 0.18 * inch
    c.setStrokeColor(colors.HexColor("#777777"))
    c.setFillColor(colors.HexColor("#f7f7f7"))
    c.roundRect(0.95 * inch, y - 0.68 * inch, width - 1.90 * inch, 0.58 * inch, 4, fill=1, stroke=1)
    c.setFillColor(colors.HexColor("#111111"))
    c.setFont(FONTS["bold"], 10.8)
    c.drawCentredString(width / 2, y - 0.32 * inch, "Monopolar operator + nodal flattening + prime-derived determinant")
    c.drawCentredString(width / 2, y - 0.50 * inch, "=> conditional route to RH.")
    c.showPage()
    c.save()


def draw_image(c: canvas.Canvas, image_path: Path, x: float, top: float, max_w: float, max_h: float) -> None:
    with Image.open(image_path) as image:
        img_w, img_h = image.size
    scale = min(max_w / img_w, max_h / img_h)
    draw_w = img_w * scale
    draw_h = img_h * scale
    draw_x = x + (max_w - draw_w) / 2
    draw_y = top - draw_h
    c.drawImage(str(image_path), draw_x, draw_y, width=draw_w, height=draw_h, preserveAspectRatio=True, mask="auto")


def merge_final() -> None:
    title = PdfReader(str(TITLE_PDF))
    source = PdfReader(str(SOURCE))
    appendix = PdfReader(str(APPENDIX_PDF))
    writer = PdfWriter()

    writer.add_page(title.pages[0])
    for page in source.pages[1:]:
        writer.add_page(page)
    for page in appendix.pages:
        writer.add_page(page)

    writer.add_metadata(
        {
            "/Title": TITLE,
            "/Author": AUTHOR,
            "/Subject": "Revised nodal-operator edition with monopolar operator and final nodal theorem",
            "/Creator": "build_monopolar_nodal_final.py",
            "/Producer": "pypdf + reportlab",
            "/CreationDate": "D:20260907000000-06'00'",
            "/ModDate": "D:20260907000000-06'00'",
        }
    )
    with OUTPUT_PDF.open("wb") as handle:
        writer.write(handle)


def make_contact_sheets(render_dir: Path) -> list[Path]:
    pngs = sorted(render_dir.glob("page-*.png"), key=lambda p: int(p.stem.split("-")[-1]))
    sheets: list[Path] = []
    thumb_w, thumb_h = 245, 318
    margin = 26
    label_h = 22
    cols, rows = 4, 3
    try:
        font = ImageFont.truetype("arial.ttf", 13)
    except OSError:
        font = ImageFont.load_default()

    for batch_idx in range(0, len(pngs), cols * rows):
        batch = pngs[batch_idx : batch_idx + cols * rows]
        sheet = Image.new(
            "RGB",
            (cols * thumb_w + (cols + 1) * margin, rows * (thumb_h + label_h) + (rows + 1) * margin),
            "white",
        )
        draw = ImageDraw.Draw(sheet)
        for idx, path in enumerate(batch):
            img = Image.open(path).convert("RGB")
            img.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
            col = idx % cols
            row = idx // cols
            x0 = margin + col * (thumb_w + margin)
            y0 = margin + row * (thumb_h + label_h + margin)
            sheet.paste(img, (x0 + (thumb_w - img.width) // 2, y0))
            page_no = int(path.stem.split("-")[-1])
            draw.text((x0, y0 + thumb_h + 5), f"page {page_no}", fill=(45, 45, 45), font=font)
        out = ROOT / f"contact_sheet_final_{len(sheets)+1:02d}.png"
        sheet.save(out)
        sheets.append(out)
    return sheets


def write_manifest(extra_paths: list[Path]) -> None:
    source_reader = PdfReader(str(SOURCE))
    output_reader = PdfReader(str(OUTPUT_PDF))
    appendix_reader = PdfReader(str(APPENDIX_PDF))
    files = [
        SOURCE,
        ROOT / "Riemann_German_Monopolar_Nodal_Framework_2026.tex",
        ROOT / "build_monopolar_nodal_final.py",
        OUTPUT_PDF,
        APPENDIX_PDF,
        TITLE_PDF,
        FIG1,
        FIG2,
    ] + extra_paths + sorted(EQ_DIR.glob("*.png"))
    data = {
        "title": TITLE,
        "author": AUTHOR,
        "edition": EDITION,
        "source_pdf": str(SOURCE),
        "source_pdf_pages": len(source_reader.pages),
        "source_pages_preserved": "2-33",
        "title_page_replaced": True,
        "appendix_pdf_pages": len(appendix_reader.pages),
        "output_pdf": str(OUTPUT_PDF),
        "output_pdf_pages": len(output_reader.pages),
        "expected_output_pages": 1 + (len(source_reader.pages) - 1) + len(appendix_reader.pages),
        "new_section": "Appendix F. General Nodal Theorem for the Monopolar Angular Channel",
        "final_page": "Final Revised Conclusion",
        "global_RH_proved": False,
        "operator_status": "monopolar operator architecture already present in source manuscript",
        "closure_condition": "derive D(z)=E(z)xi(1/2+z), E(z)!=0, from prime data and passive-adjoint compatibility without circular zero insertion",
        "sha256": {str(p): sha256(p) for p in files if p.exists()},
    }
    MANIFEST.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def make_zip(paths: list[Path]) -> None:
    with zipfile.ZipFile(ZIP_OUT, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in paths:
            if path.exists() and path.is_file():
                zf.write(path, arcname=f"Riemann_German_Monopolar_Nodal_Framework_2026/{path.name}")
        for path in [FIG1, FIG2]:
            zf.write(path, arcname=f"Riemann_German_Monopolar_Nodal_Framework_2026/figures/{path.name}")


def main() -> None:
    make_title_page()
    make_appendix()
    merge_final()
    write_manifest([])
    make_zip(
        [
            OUTPUT_PDF,
            ROOT / "Riemann_German_Monopolar_Nodal_Framework_2026.tex",
            ROOT / "build_monopolar_nodal_final.py",
            MANIFEST,
            SOURCE,
        ]
    )
    print(json.dumps({
        "output_pdf": str(OUTPUT_PDF),
        "output_pages": len(PdfReader(str(OUTPUT_PDF)).pages),
        "tex": str(ROOT / "Riemann_German_Monopolar_Nodal_Framework_2026.tex"),
        "zip": str(ZIP_OUT),
        "sha256_pdf": sha256(OUTPUT_PDF),
        "global_RH_proved": False,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
