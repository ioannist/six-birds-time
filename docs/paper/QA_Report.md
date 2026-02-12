# QA Report: Qeios Submission

**Date:** 12 February 2026
**Manuscript:** To Notch a Stone with Six Birds: Time as a Theory Artifact of Order, Measure, and Arrow

---

## A) Policy Compliance Checklist

| Requirement | Status | Location |
|---|---|---|
| "Potential competing interests" statement | PASS | Section "Statements and Declarations" |
| "Data availability" statement (what/where/how) | PASS | Section "Statements and Declarations" |
| "Author contributions" (CRediT-style) | PASS | Section "Statements and Declarations" |
| "Generative AI" disclosure (tool + purpose) | PASS | Section "Statements and Declarations" |
| Ethics statement ("Not applicable") | PASS | Section "Statements and Declarations" |
| Funding statement | PASS | Section "Statements and Declarations" |
| Code availability statement | PASS | Section "Statements and Declarations" |
| No patient/participant identifiers | PASS (N/A) | No human subjects |
| All content owned by author or cited | PASS | All tables auto-generated; all references cited |

---

## B) TeX Upload Robustness

### Deliverable 1: qeios_single.tex (self-contained)

**Build commands:**
```bash
pdflatex -interaction=nonstopmode -halt-on-error qeios_single.tex
pdflatex -interaction=nonstopmode -halt-on-error qeios_single.tex
pdflatex -interaction=nonstopmode -halt-on-error qeios_single.tex
```

| Check | Result |
|---|---|
| Compiles without .bib dependency | PASS |
| No undefined citations | PASS (grep -c "Citation.*undefined" = 0) |
| No undefined references | PASS (grep -c "Reference.*undefined" = 0) |
| Output PDF generated | PASS (22 pages, ~422 KB) |
| orcidlink fallback works | PASS (package found on this system; fallback defined for systems without it) |

### Deliverable 2: qeios_source_bundle.zip

**Build commands (after unzip):**
```bash
pdflatex to_notch_a_stone_with_six_birds.tex
bibtex to_notch_a_stone_with_six_birds
pdflatex to_notch_a_stone_with_six_birds.tex
pdflatex to_notch_a_stone_with_six_birds.tex
```

| Check | Result |
|---|---|
| Unzips and compiles in clean directory | PASS |
| No undefined citations | PASS (grep -c "Citation.*undefined" = 0) |
| No undefined references | PASS (grep -c "Reference.*undefined" = 0) |
| Output PDF generated | PASS (22 pages, ~422 KB) |
| All section files present | PASS (11 files in sections/) |
| All table files present | PASS (7 files in tables/) |
| README_BUILD.txt included | PASS |

---

## C) Citation Verification

All 20 citation keys referenced in the manuscript are present in the bibliography:

| Citation key | Present in .bbl | Has DOI/URL |
|---|---|---|
| Berry1984 | YES | YES (10.1098/rspa.1984.0023) |
| CoverThomas2006 | YES | YES (ISBN) |
| Crooks1999 | YES | YES (10.1103/PhysRevE.60.2721) |
| Esposito2010 | YES | YES (10.1103/PhysRevLett.104.090601) |
| Gaspard2004 | YES | YES (10.1007/s10955-004-3455-1) |
| Jarzynski1997 | YES | YES (10.1103/PhysRevLett.78.2690) |
| KullbackLeibler1951 | YES | YES (10.1214/aoms/1177729694) |
| Lebowitz1993 | YES | YES (10.1063/1.881363) |
| MurashitaFunoUeda2014 | YES | YES (10.1103/PhysRevE.90.042110) |
| Norris1997 | YES | YES (ISBN) |
| PopescuRohrlich1994 | YES | YES (10.1007/BF02058098) |
| Schnakenberg1976 | YES | YES (10.1103/RevModPhys.48.571) |
| Seifert2012 | YES | YES (10.1088/0034-4885/75/12/126001) |
| Shannon1949 | YES | YES (10.1002/j.1538-7305.1949.tb00928.x) |
| SinitsynNemenman2007 | YES | YES (10.1209/0295-5075/77/58001) |
| bell_1964 | YES | YES (10.1103/PhysicsPhysiqueFizika.1.195) |
| brunner_2014_bell_nonlocality | YES | YES (10.1103/RevModPhys.86.419) |
| einstein_1905 | YES | YES (10.1002/andp.19053221004) |
| nielsen_chuang | YES | YES (10.1017/CBO9780511976667) |
| sixbirds_foundations | YES | YES (10.5281/zenodo.18365949) |

---

## D) Content Integrity

| Check | Result |
|---|---|
| Title/author/affiliation present | PASS |
| Correspondence email present | PASS (ioannis@automorph.io) |
| ORCID present | PASS (0009-0009-7659-5964) |
| All 8 tables render correctly | PASS |
| No figures to verify | N/A (manuscript has no figures) |
| Keywords present | PASS (12 keywords) |
| Appendices (repro, Lean, code map) | PASS (3 appendix sections) |

---

## E) Filename Hygiene

| Check | Result |
|---|---|
| ASCII-only filenames | PASS |
| No spaces in filenames | PASS |
| Shallow directory structure | PASS (max depth: 1 subfolder) |
| Short paths | PASS |

---

## Deliverables Produced

1. `qeios_single.tex` - Self-contained single-file TeX (no .bib dependency)
2. `qeios_source_bundle.zip` - Full source bundle (69 KB)
3. `qeios_submission.pdf` - Built from qeios_single.tex (22 pages)
4. `Qeios_Submission_Notes.md` - Submission guide for human submitter
5. `QA_Report.md` - This file

**Overall verdict: ALL CHECKS PASS**
