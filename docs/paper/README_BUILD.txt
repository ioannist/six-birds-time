README_BUILD.txt
================
To Notch a Stone with Six Birds: Time as a Theory Artifact of Order, Measure, and Arrow
Ioannis Tsiokos <ioannis@automorph.io>

Build instructions for the Qeios source bundle
-----------------------------------------------

OPTION A: Single-file build (recommended, no BibTeX needed)

    pdflatex qeios_single.tex
    pdflatex qeios_single.tex

  Two passes are needed for cross-references. No .bib file is required;
  the bibliography is embedded in the .tex file.

OPTION B: Full BibTeX build (modular source)

    pdflatex to_notch_a_stone_with_six_birds.tex
    bibtex to_notch_a_stone_with_six_birds
    pdflatex to_notch_a_stone_with_six_birds.tex
    pdflatex to_notch_a_stone_with_six_birds.tex

  Or equivalently:

    latexmk -pdf -interaction=nonstopmode -halt-on-error to_notch_a_stone_with_six_birds.tex

  This requires: references.bib, all files under sections/ and tables/.

Files in this bundle
--------------------
  qeios_single.tex                         Self-contained single-file TeX
  to_notch_a_stone_with_six_birds.tex      Modular main TeX (uses \input)
  references.bib                           BibTeX database
  to_notch_a_stone_with_six_birds.bbl      Pre-built BibTeX output
  sections/*.tex                           Section files (11 files)
  tables/*.tex                             Auto-generated table files (7 files)
  README_BUILD.txt                         This file

Requirements
------------
  - pdflatex (TeX Live 2022 or later recommended)
  - Standard packages: amsmath, amssymb, amsthm, mathtools, microtype,
    graphicx, booktabs, array, tabularx, multirow, enumitem, xcolor,
    fancyhdr, geometry, float, placeins, caption, xurl, hyperref,
    cleveref, natbib
  - Optional: orcidlink (fallback provided if missing)
