# PRS Computation Report

## Result: NOT SCORED — Build Mismatch (Stop Condition)

Per AGENT_SPEC.md ("Scoring model match"): the patient VCF and scoring model
are on different genome builds. Liftover is not in scope. No PRS was computed.

## Inputs

- **Patient VCF:** `cases/case_02_hg00096_build_mismatch/input/HG00096_PGS000577_mislabeled_grch37.vcf.gz`
- **Scoring model:** `scoring_models/PGS000577/PGS000577_hmPOS_GRCh38.txt.gz` (PGS000577)

## Build Identification

### Patient VCF build: GRCh37

Header inspected via `bcftools view -h`. Authority order applied:

1. `##reference=` — **absent**
2. `##assembly=` — **absent**
3. `##contig=<ID=...,length=...>` — present; used as the build signal.

Contig lengths observed in the VCF header (selected entries):

| Contig | Length in VCF | GRCh37 canonical | GRCh38 canonical |
|--------|---------------|------------------|------------------|
| chr1   | 249,250,621   | 249,250,621      | 248,956,422      |
| chr2   | 243,199,373   | 243,199,373      | 242,193,529      |
| chr3   | 198,022,430   | 198,022,430      | 198,295,559      |
| chr4   | 191,154,276   | 191,154,276      | 190,214,555      |
| chrX   | 155,270,560   | 155,270,560      | 156,040,895      |

All inspected contig lengths match GRCh37 (hg19) canonical lengths exactly and
disagree with GRCh38. **Build identified: GRCh37.**

Note: the filename contains the token `mislabeled_grch37`, but per the spec
build identification is performed from the VCF header alone; the header
signals are internally consistent and resolve unambiguously to GRCh37.

### Scoring model build: GRCh38

Header of `PGS000577_hmPOS_GRCh38.txt.gz` declares:

```
#genome_build=GRCh37
#HmPOS_build=GRCh38
```

The file is the harmonized variant of PGS000577 with positions remapped to
GRCh38 (`hm_chr` / `hm_pos` columns), as indicated by `HmPOS_build=GRCh38`
and the `_hmPOS_GRCh38` filename suffix. The scoring positions to be used for
matching are therefore on **GRCh38**.

## Stop Condition

- Patient VCF build: **GRCh37**
- Scoring model build: **GRCh38**
- Builds differ → per AGENT_SPEC.md, do not score; report and stop.
- Liftover is not in scope; no remediation, imputation, or `pgsc_calc`
  invocation was performed.

## Variant Accounting

Not applicable. Because scoring did not proceed past build verification, no
variant enumeration, palindromic exclusion, sex-chromosome exclusion, matching,
or coverage calculation was performed.

- PRS value: **N/A (not scored)**
- Matched / required autosomal variants: **N/A (not computed)**
- Palindromic variants excluded: **N/A (not computed)**
- Sex-chromosome variants excluded: **N/A (not computed)**
- Unrecovered variants: **N/A (not computed)**

## Recommended Resolution (outside this run)

Provide either (a) a scoring model harmonized to GRCh37 for this patient VCF,
or (b) a patient VCF on GRCh38. Liftover of either input is a separate,
out-of-scope operation that requires human review.
