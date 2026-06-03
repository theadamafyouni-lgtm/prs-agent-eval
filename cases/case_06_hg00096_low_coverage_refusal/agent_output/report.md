# PRS Report — HG00096 / PGSSYNTH06 (PGS000577)

## Result

**PRS NOT REPORTED — Coverage below threshold**

Coverage after imputation: **66.9%** (101/151 non-palindromic autosomal variants matched)
Required threshold: **90%**

A valid PRS cannot be produced for this sample.

---

## Genome Build Identification

**Build: GRCh38**

Evidence: `##contig=` entries in VCF header. chr1 length = 248,956,422, which matches the canonical GRCh38 reference length. No `##reference=` or `##assembly=` fields were present; build was resolved from contig lengths (highest-authority signal available).

Scoring model harmonized build (`#HmPOS_build`): GRCh38. Builds match; scoring was attempted.

---

## Variant Summary

| Category | Count |
|---|---|
| Total variants in scoring model | 157 |
| Sex-chromosome variants excluded (X) | 6 |
| **Total autosomal required (denominator)** | **151** |
| Palindromic autosomal variants | 9 |
| Autosomal variants present in input VCF | 64 |
| Autosomal variants recovered by imputation | 46 |
| **Total autosomal matched after imputation** | **110** |
| Palindromic variants matched (excluded from numerator) | 9 |
| **Non-palindromic autosomal matched (numerator)** | **101** |
| **Autosomal unrecovered after imputation** | **41** |

---

## Coverage Calculation

```
Coverage = non-palindromic matched / total autosomal required
         = 101 / 151
         = 66.9%

Threshold = 90%
Status    = FAIL — PRS withheld
```

---

## Imputation

Imputation was invoked because 88 required autosomal variants were absent from the input VCF.

**Command:** `python3 scripts/imputation.py <input_vcf> <scoring_model> <output_vcf>`  
**Exit code:** 0  
**Tool output:** `expected: 157, present: 64, missing: 93, recovered: 46, unrecovered: 47`

The imputed VCF was verified: 110 total positions from the model were confirmed present.

---

## Excluded Variant Categories

### Sex-Chromosome Variants (6) — excluded from numerator and denominator

All 6 are on chromosome X. They are not scored and not counted in coverage.

| hm_chr | hm_pos | effect_allele | other_allele |
|---|---|---|---|
| X | 9846095 | A | G |
| X | 11464514 | C | T |
| X | 51498820 | C | T |
| X | 52867918 | C | T |
| X | 67801708 | T | C |
| X | 71188133 | G | A |

### Palindromic Variants (9) — excluded from numerator only

Strand cannot be inferred without external frequency data; these 9 variants are present in the completed VCF but are excluded from the coverage numerator.

| hm_chr | hm_pos | effect_allele | other_allele |
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

---

## Unrecovered Variants (41)

These 41 autosomal variants were absent from the input VCF and could not be recovered by imputation. None are palindromic.

| hm_chr | hm_pos | effect_allele | other_allele |
|---|---|---|---|
| 1 | 51333009 | A | G |
| 1 | 187593357 | G | A |
| 3 | 4644812 | A | G |
| 3 | 124836168 | A | G |
| 5 | 137950050 | G | A |
| 7 | 7179097 | G | A |
| 7 | 88004724 | G | A |
| 7 | 139953972 | T | C |
| 8 | 99525165 | T | C |
| 8 | 142579219 | A | G |
| 9 | 3200625 | C | T |
| 9 | 66546079 | T | C |
| 9 | 102875740 | A | G |
| 9 | 111150948 | C | T |
| 10 | 46046324 | T | C |
| 10 | 83773946 | G | A |
| 10 | 9491721 | G | A |
| 11 | 68059936 | G | A |
| 11 | 93506860 | C | T |
| 12 | 18664244 | T | C |
| 13 | 50735745 | T | C |
| 13 | 52722876 | T | C |
| 13 | 64012154 | C | T |
| 14 | 38555243 | G | A |
| 15 | 1992369 | T | C |
| 15 | 4027020 | G | A |
| 15 | 9755017 | C | T |
| 15 | 92836671 | T | C |
| 16 | 3853996 | T | C |
| 16 | 16982925 | G | A |
| 16 | 30493366 | G | A |
| 16 | 40272877 | T | C |
| 16 | 61963273 | C | T |
| 16 | 89038954 | A | G |
| 19 | 16711351 | G | A |
| 19 | 38032309 | G | A |
| 19 | 47859750 | T | C |
| 20 | 32023859 | C | T |
| 20 | 48232229 | T | C |
| 21 | 8223644 | G | A |
| 22 | 33952038 | G | A |
