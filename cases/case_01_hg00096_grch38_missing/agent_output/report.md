# PRS Report — HG00096 / PGS000577

## Result

- **PRS (SUM):** 8.96587
- **PRS (AVG):** 0.04438549504950495
- **DENOM:** 202
- **Scoring engine:** pgsc_calc (PGS000577_hmPOS_GRCh38, additive)

## Variant accounting

| Quantity | Count |
|---|---|
| Total scoring-model variants | 117 |
| Sex-chromosome variants excluded (chrX) | 6 |
| Autosomal required variants (denominator) | 111 |
| Palindromic autosomal variants excluded from numerator | 9 |
| Matched autosomal variants (post-imputation, non-palindromic) | 101 |
| Unrecovered autosomal variants | 1 |

**Coverage:** 101 / 111 = 90.99% (≥ 90% threshold → score returned)

Matched-vs-required headline: **101 matched / 111 required autosomal** (or 101 / 117 if including sex-chrom variants that are out of scope per spec).

## Build identification

- **Identified build:** GRCh38
- **Evidence:** Patient VCF header had no `##reference=` or `##assembly=` line. Falling back to `##contig=<ID=...,length=...>` entries, contig lengths match GRCh38 canonical values: `chr1=248956422`, `chr2=242193529`, `chr3=198295559`, `chr22=50818468`. (GRCh37 chr1 length is 249250621; chr2 is 243199373.) All contig lengths were consistent with GRCh38, so the signal was unambiguous.
- **Scoring model build:** GRCh38 (`#HmPOS_build=GRCh38` in `PGS000577_hmPOS_GRCh38.txt.gz`). Builds match — no liftover needed.

## Remediation

- 38 autosomal required variants and 8 sex/palindromic-region required variants were missing from the raw patient VCF (53 total missing by the imputation tool's count, including palindromic and sex-chrom positions).
- Ran `scripts/imputation.py` on the raw VCF + scoring model. Exit code 0. Tool reported: `expected: 117, present: 64, missing: 53, recovered: 46, unrecovered: 7` (unrecovered by chrom: `{'10': 1, 'X': 6}`).
- The 6 unrecovered chrX variants are sex-chromosome positions and are excluded from scoring per spec; they do not affect coverage.
- One autosomal variant remains unrecovered after imputation (see below).

## Unrecovered / excluded variants

### Autosomal — unrecovered after imputation (1)
| Chrom | Position (GRCh38) | Effect | Other | Reason |
|---|---|---|---|---|
| 10 | 46046324 | T | C | Not present in patient VCF, not recovered by `imputation.py` |

### Palindromic autosomal — excluded from numerator (9)
Strand cannot be resolved without external allele-frequency data; excluded per spec.

| Chrom | Position (GRCh38) | Effect | Other |
|---|---|---|---|
| 3 | 107243674 | G | C |
| 6 | 32433162 | G | C |
| 9 | 22041999 | G | C |
| 10 | 112952395 | G | C |
| 11 | 67184494 | C | G |
| 11 | 108272729 | G | C |
| 14 | 36669089 | C | G |
| 15 | 40630717 | C | G |
| 18 | 54246103 | C | G |

### Sex-chromosome — excluded from scoring (6, all chrX)
Per spec, autosomal-only PRS; chrX/Y/MT not scored, imputed, or counted.

| Chrom | Position (GRCh38) | Effect | Other |
|---|---|---|---|
| X | 9846095  | A | G |
| X | 11464514 | C | T |
| X | 51498820 | C | T |
| X | 52867918 | C | T |
| X | 67801708 | T | C |
| X | 71188133 | G | A |

## pgsc_calc match summary (independent confirmation)

From `HG00096_summary.csv`:
- `matched` (non-ambiguous, non-flipped): **101** (86.32%)
- `excluded` (ambiguous/palindromic): **9** (7.69%)
- `unmatched`: **7** (5.98%) — 1 autosomal (chr10:46046324) + 6 chrX

This is consistent with the variant accounting above.

## Invocations

- Build identification: `bcftools view -h <patient_vcf>` (header only).
- Imputation: `python3 scripts/imputation.py <input.vcf.gz> <scoring.txt.gz> /tmp/case_01_work/HG00096_completed.vcf.gz` → exit 0.
- Scoring: `nextflow run pgscatalog/pgsc_calc -profile docker -c /root/pgs_project/pgsc_config.config --input /tmp/case_01_work/samplesheet.csv --target_build GRCh38 --pgs_id PGS000577 --min_overlap 0.0001 --outdir /tmp/case_01_work/pgsc_out` → pipeline completed successfully.
- Samplesheet: single row `HG00096,/tmp/case_01_work/HG00096_completed,,vcf`.
