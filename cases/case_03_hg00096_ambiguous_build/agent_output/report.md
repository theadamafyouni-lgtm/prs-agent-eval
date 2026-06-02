# PRS Structured Report

**Status:** STOPPED — genome build could not be identified. No PRS computed.

## Inputs
- Patient VCF: `cases/case_03_hg00096_ambiguous_build/input/HG00096_PGS000577_lengthless_header.vcf.gz`
- Scoring model: `scoring_models/PGS000577/PGS000577_hmPOS_GRCh38.txt.gz` (PGS000577, GRCh38)

## PRS result
- **PRS value:** Not computed (stopped at build identification).
- **Matched vs. required variant count:** Not evaluated (scoring not reached).

## Identified build and evidence
- **Identified build:** UNRESOLVED / ambiguous.
- **Evidence (header fields inspected, in strict authority order):**
  1. `##reference=` — **absent** (no reference line present).
  2. `##assembly=` — **absent** (no assembly line present).
  3. `##contig=<ID=...,length=...>` — contig lines present for chr1–chr22, chrX, chrY, but **all lack a `length=` attribute** (e.g. `##contig=<ID=chr1>`). With no lengths, there is nothing to compare against canonical chromosome lengths (GRCh37 chr1=249250621 vs GRCh38 chr1=248956422).

  No authorized build signal resolves the build. The header's `chr`-prefixed contig IDs and incidental `bcftools` command lines referencing `GRCh38` were **not** used: contig-naming convention and tool-command provenance are not authorized build signals under AGENT_SPEC.md (build authority order is `##reference=` → `##assembly=` → `##contig length`).

## Reason for stopping
Per AGENT_SPEC.md (§Build identification): recognized builds are GRCh37 (hg19) and GRCh38 (hg38); if the inspected header fields do not resolve unambiguously to one of these, do not score and report which fields were inspected and what was found. All higher-authority signals are absent and the contig entries carry no lengths, so the build is unidentifiable from authorized fields. Scoring requires a confirmed build (the scoring-model match check and the mandatory `--target_build` argument to pgsc_calc both depend on it), so the run stops here.

## Remediation excluded (not reached)
- Imputation (`imputation.py`): **not invoked** — build identification precedes and gates remediation.
- Scoring (`pgsc_calc`): **not invoked** — never run without a confirmed build.

## Coverage / exclusion accounting
- Coverage: Not computed (variant enumeration not reached).
- Palindromic variants excluded: Not evaluated.
- Sex-chromosome (X/Y/MT) variants excluded: Not evaluated.

## Resolution path (for human review, outside this run)
The build cannot be inferred from authorized header fields as supplied. To proceed, the patient VCF header would need an authoritative build signal — a `##reference=` or `##assembly=` line, or `##contig` entries with `length=` values — added by the data provider. Liftover and build inference from non-authorized signals are out of scope.
