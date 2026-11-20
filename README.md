# AGI Research Review (2026)

An independent 100-page literature synthesis by **Rashmi Ranjan Behera**, prepared for **Dr. Vidya Mohanty** as the intended academic reader. The document does not claim co-authorship, supervision, endorsement, or a year of work.

The review synthesizes 20 recent papers on AGI measurement, multimodal and visual intelligence, agent architectures, training and environment scaling, benchmark design, and process reliability. It includes original conceptual diagrams, two-page profiles of each source, a proposed evaluation protocol, and an annotated source register.

## Downloads

- [100-page PDF report](site/downloads/AGI_Research_Review_2026.pdf)
- [Editable Word manuscript](site/downloads/AGI_Research_Review_2026.docx)
- [21-slide PowerPoint deck](site/downloads/AGI_Research_Review_2026.pptx)
- [Annotated sources and publication status](site/sources.html)
- Hosted review website: https://rashmiranjanaiet.github.io/AGI/

The twenty source PDFs remain in the author’s local workspace. This repository links to official source records and does not redistribute papers whose licenses may restrict copying.

## Provenance and scope

The review is a focused, non-systematic literature synthesis, not a peer-reviewed publication. It distinguishes conference publications, lab reports, surveys, position papers, and preprints. The source index records publisher and author links. The report does not claim that any paper in the corpus demonstrates AGI. Its diagrams are conceptual schematics created for this review, not copied figures or empirical results.

“Prepared for Dr. Vidya Mohanty” identifies the intended reader only. It does not imply that Dr. Mohanty co-authored, supervised, or endorsed the work.

## Rebuilding

The generation scripts create the PDF, DOCX, and PPTX from the review content. Use Python with ReportLab, python-docx, and python-pptx installed:

    python build_resource.py

Generated files in output/ can be copied into site/downloads/ for the static website.
