# AGI Research Review (2026)

An independent 50-page literature synthesis by **Rashmi Ranjan Behera**, prepared for academic discussion with **Dr. Vidya Mohanty**. The attribution identifies the intended reader; it does not claim co-authorship, supervision, or endorsement.

The review synthesizes the 20 supplied papers on AGI measurement, multimodal and visual intelligence, agent architectures, training and environment scaling, benchmark design, and process reliability. It includes a paper-by-paper critical review, a proposed evaluation protocol, technical appendices, and linked references.

## Downloads

- [50-page two-column PDF review](site/downloads/AGI_Research_Review_2026.pdf)
- [21-slide companion presentation](site/downloads/AGI_Research_Review_2026.pptx)
- [Annotated sources and publication status](site/sources.html)
- Hosted review: <https://rashmiranjanaiet.github.io/AGI/>

## Figures and source use

Figures 1 from ACL Anthology papers [R10]–[R20] are reproduced with their source captions and attribution under the applicable Creative Commons Attribution 4.0 policy. Other source diagrams are redrawn as reviewer schematics. Source prose is summarized in original wording, with citations and links to the official records; the source PDFs are not redistributed here. The ACL policy excludes third-party material from its blanket reuse permission, so such content is not included.

## Scope and provenance

This is a focused, non-systematic literature synthesis, not a peer-reviewed publication. It distinguishes conference papers, reports, position papers, surveys, and preprints. The review does not claim that any paper in the corpus demonstrates AGI. Publication details and versions should be checked against the official records before formal citation.

## Rebuilding the PDF

The report generator is `build_academic_review.py`. It requires Python, ReportLab, Poppler (`pdftotext`, `pdftoppm`), and the source PDFs in `papers/`. Run:

    python3 build_academic_review.py

Copy `output/AGI_Research_Review_2026.pdf` to `site/downloads/` to update the hosted PDF.
