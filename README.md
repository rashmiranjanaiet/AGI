# AGI Research Review (2026)

An eight-page illustrated paper and an extended 50-page literature review by **Rashmi Ranjan Behera** and **Dr. Vidya Mohanty**. Dr. Mohanty served as Academic Research Guide.

The review synthesizes the 20 supplied papers on AGI measurement, multimodal and visual intelligence, agent architectures, training and environment scaling, benchmark design, and process reliability. It includes a paper-by-paper critical review, a proposed evaluation protocol, technical appendices, and linked references.

## Downloads

- [Eight-page illustrated paper](site/downloads/AGI_Research_Paper_8_pages.pdf)
- [Extended 50-page review](site/downloads/AGI_Research_Review_2026.pdf)
- [21-slide companion presentation](site/downloads/AGI_Research_Review_2026.pptx)
- [Annotated sources and publication status](site/sources.html)
- Hosted review: <https://rashmiranjanaiet.github.io/AGI/>

## Figures and source use

The eight-page edition contains seven attributed source figures and an original worked join example. Its numerical scoring example is explicitly hypothetical.

In the extended edition, Figures 1 from ACL Anthology papers [R10]–[R20] are reproduced with their source captions and attribution under the applicable Creative Commons Attribution 4.0 policy. Other source diagrams are redrawn as reviewer schematics. Source prose is summarized in original wording, with citations and links to the official records; the source PDFs are not redistributed here. The ACL policy excludes third-party material from its blanket reuse permission, so such content is not included.

## Scope and provenance

This is a focused, non-systematic literature synthesis, not a peer-reviewed publication. It distinguishes conference papers, reports, position papers, surveys, and preprints. The review does not claim that any paper in the corpus demonstrates AGI. Publication details and versions should be checked against the official records before formal citation.

## Rebuilding the PDF

Build the eight-page paper with `python3 build_concise_review.py` on macOS with Times New Roman, Pillow and ReportLab installed. The manuscript is in `concise_paper.md`. The source figure crops are stored in `figures/`.

The extended report generator is `build_academic_review.py`. It requires Python, ReportLab, Poppler (`pdftotext`, `pdftoppm`), and the source PDFs in `papers/`. Run:

    python3 build_academic_review.py

Copy `output/AGI_Research_Review_2026.pdf` to `site/downloads/` to update the hosted PDF.
