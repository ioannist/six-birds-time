# Research Square QA Report

## Compilation

**Command (main manuscript):**
```
cd docs/paper
latexmk -pdf -interaction=nonstopmode -halt-on-error to_notch_a_stone_with_six_birds.tex
```

**Result:** 20 pages, 433 KB. No errors, no undefined references, no missing citations.

**Command (supplementary):**
```
cd docs/paper
latexmk -pdf -interaction=nonstopmode -halt-on-error supplementary.tex
```

**Result:** 3 pages, 182 KB. No errors, no undefined references.

**Minor warnings (non-blocking):**
- 1 overfull hbox (0.87pt in clock budget table) — not visible to reader
- 1 underfull hbox in no-signalling Lean pointer paragraph — cosmetic only

---

## Pass/Fail Checks

| Check | Status | Notes |
|---|---|---|
| Compiles without errors | PASS | Both main and supplement |
| No undefined references ("??") | PASS | All \ref and \cref resolved |
| No missing citations | PASS | All \citep/\citet resolved; 4 new citations added |
| All 8 tables render and referenced | PASS | birds-to-time, artifact-manifest, dpi, clock-budget, enablement, constraints-cones, holonomy, no-signalling |
| Introduction present | PASS | Section 1 |
| Methods present and clearly labeled | PASS | Section 4, with new "Methods overview" subsection |
| Results present and clearly labeled | PASS | Sections 5–8 (Results I, Results II, No Global Time, Physics Dilemma) |
| Discussion/Conclusion present | PASS | Section 9 |
| Declarations section present in text | PASS | After Conclusion (competing interests, funding, ethics, data/code, author contributions, AI use) |
| Conflict-of-interest statement | PASS | "The author declares no competing interests." |
| "Theory" disambiguation | PASS | Final sentence of abstract: "'theory' is used in the SBT technical sense—a closure (layer with audits)—not as a speculative or opinion category." |
| Keywords present | PASS | 12 keywords in main tex |
| Author affiliation | PASS | Automorph Inc., Wilmington, DE |
| Corresponding author marked | PASS | Via \thanks footnote with email |
| ORCID | PASS | 0009-0009-7659-5964 |
| No draft artifacts / TODOs | PASS | None found |
| Hyperlinks public and stable | PASS | GitHub repo, Zenodo DOIs, standard journal DOIs |
| Supplementary split | PASS | Appendices S1–S3 in separate supplementary.pdf |

---

## List of Edits Made

### A) Build and Completeness
- Verified clean compilation; fixed 1 undefined reference (sec:appendix-mechanized → Supplementary Appendix S2)
- All 8 tables verified rendered and referenced

### B) Research Article Disambiguation
- **Abstract:** Added "theory is used in the SBT technical sense" disambiguation sentence
- **Abstract:** Strengthened audit suite language ("calibrated null regimes, matched controls")
- **Introduction:** Added "validated by reproducible artifacts and auto-generated evidence tables" to contributions bullet
- **Introduction:** Added Lebowitz (1993) citation anchoring arrow-of-time discussion in mainstream literature
- **Methods:** Added numbered "Methods overview" subsection (5 steps: state space, regimes, metrics, calibration, evidence tables)
- **Results I:** Added Evidence pointers for Separations (i), (ii), (iii) with table/artifact references
- **Results II:** Added Evidence pointers for Separation (iv) — enablement and holonomy

### C) Authorship and Metadata
- Updated author block: corresponding author marker (*), email via \thanks
- Added ORCID via \thanks
- Updated date to 10 February 2026
- Expanded keywords from 5 to 12

### D) Declarations Section
- Added full Declarations section after Conclusion with 8 subsections:
  competing interests, funding, ethics, consent, data availability, code availability, author contributions, AI/LLM use

### E) Data/Code Accessibility
- Updated footer DOI to repository DOI (10.5281/zenodo.18595959)
- Code availability statement includes both GitHub URL and Zenodo DOI
- Supplementary S1 includes full environment setup (Python ≥ 3.9, pyproject.toml deps, venv commands)

### F) Tone and Claim-Scope Safety
- Rewrote "Limits and scope" paragraph as explicit bulleted list with 5 clear disclaimers
- Added explicit "What is demonstrated vs. hypothesized" disclaimer
- No-signalling toy already had strong disclaimers; verified and preserved
- All "this is a toy" / "does not derive spacetime" language preserved and slightly strengthened

### G) Citation Hygiene
- Added 4 mainstream anchoring references:
  - Crooks (1999) — entropy production fluctuation theorem
  - Jarzynski (1997) — nonequilibrium equality
  - Lebowitz (1993) — Boltzmann's entropy and time's arrow
  - Esposito & Van den Broeck (2010) — detailed fluctuation theorems
- Integrated into Methods (entropy production subsection) and Introduction

### H) Supplement Split
- Original appendices (reproducibility, Lean anchors, code map) moved to standalone supplementary.pdf
- Main manuscript section 10 replaced with pointer to Supplementary Appendices S1–S3
- All internal cross-references updated

---

## Remaining Human-Fill Items Before Upload

| Item | Action Required |
|---|---|
| **Verify email address** | Confirm ioannis@automorph.org is the correct submission email |
| **Verify Zenodo DOI** | Confirm 10.5281/zenodo.18595959 is the correct repository DOI (vs. previous preprint DOI 10.5281/zenodo.18495363) |
| **RS subject area** | Select closest match from RS dropdown (Physics, CS theory, Information theory) |
| **AI/LLM disclosure** | Verify the AI use statement accurately reflects actual usage |
| **Review Declarations** | Confirm all statements (especially funding, competing interests) are accurate |
