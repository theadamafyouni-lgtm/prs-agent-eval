# PRS Report — HG00096 / PGS000577

## Result: NOT SCORED — malformed patient VCF (invalid REF alleles)

The patient VCF contains records with invalid (non-`ACGTN`) REF alleles. Per
AGENT_SPEC §Scope & inputs ("If any required file … is … malformed, report it
and stop. Do not proceed on partial inputs."), scoring was **not** performed and
no PRS value is returned.

- **PRS value:** not computed (stopped before scoring)
- **Matched vs required variants:** not evaluated — input rejected at the
  data-integrity gate, before variant matching / imputation / pgsc_calc.

## Inputs

- Patient VCF: `cases/case_07_hg00096_invalid_alleles/input/HG00096_PGS000577_GRCh38_invalid.vcf.gz`
- Scoring model: `scoring_models/PGS000577/PGS000577_hmPOS_GRCh38.txt.gz` (PGS000577)

## Build identification

- **Identified build: GRCh38.**
- Evidence: header contains no `##reference=` and no `##assembly=` field, so the
  highest-authority signal available is `##contig` lengths. `chr1` length =
  248,956,422, which is the canonical GRCh38 chr1 length (GRCh37 chr1 =
  249,250,621). Other contigs are consistent (e.g. `chr2=242,193,529`).
- Scoring model harmonized build (`#HmPOS_build`) = GRCh38. **Builds match**, so
  no build-mismatch stop applies; the stop is due to malformed allele data.

## Reason for stopping: invalid REF alleles

20 of 101 records carry REF alleles that are not valid VCF nucleotides. Valid
REF bases are `A/C/G/T/N`; the values found (`B`, `J`, `L`, `S`) are either IUPAC
ambiguity codes (`B`, `S`), which are not permitted in the REF field, or not
nucleotide codes at all (`J`, `L`). The variant ID field preserves the intended
allele (e.g. `2:10570604:C:T`), confirming the REF column has been corrupted.

These are **not** missing variants, so they are not eligible for the imputation
remediation workflow (AGENT_SPEC §Variant enumeration: variants whose alleles
cannot be reconciled are unrecoverable and "do not pass them to imputation").
They are corrupt records, which makes the patient VCF a malformed input.

All 20 corrupted records are on autosomes. Affected records (REF found → REF
intended, from ID):

| CHROM | POS | REF found | REF intended |
|-------|-----|-----------|--------------|
| chr2  | 10570604  | S | C |
| chr2  | 43326810  | L | T |
| chr2  | 62904596  | J | G |
| chr2  | 66425753  | S | C |
| chr2  | 85567174  | L | T |
| chr2  | 172446825 | B | A |
| chr2  | 173369819 | L | T |
| chr3  | 170412314 | S | C |
| chr5  | 169745129 | B | A |
| chr6  | 11218797  | S | C |
| chr7  | 40835593  | B | A |
| chr8  | 127091872 | B | A |
| chr8  | 127401060 | J | G |
| chr9  | 129813781 | S | C |
| chr10 | 88435392  | S | C |
| chr11 | 113936459 | J | G |
| chr12 | 14263984  | B | A |
| chr12 | 49282227  | L | T |
| chr12 | 132491403 | J | G |
| chr17 | 37738049  | B | A |

## Supporting variant-set context (not used for scoring)

These counts are provided for transparency; matching/coverage were not run
because the input was rejected.

- Scoring model total required variants: 117
- Sex-chromosome (X/Y/MT) required variants excluded from scoring: 6 (all chrX)
- Autosomal required variants (would-be coverage denominator): 111
- Palindromic autosomal variants (A/T, T/A, G/C, C/G; excluded from numerator): 9
- Invalid-allele records in patient VCF: 20 (all autosomal)

## Required action

The patient VCF must be regenerated with valid REF alleles before a PRS can be
computed. No score should be reported from this input.
