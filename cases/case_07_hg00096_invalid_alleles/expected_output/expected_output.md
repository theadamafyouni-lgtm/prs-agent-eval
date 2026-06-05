# Case 7 expected: invalid alleles

## Input
- `input/HG00096_PGS000577_GRCh38_invalid.vcf.gz` — HG00096, GRCh38, with 20 variants whose REF allele was changed to an invalid letter (A->B, C->S, T->L, G->J). The 20 are listed in `changed_variants.txt`.
- Scoring model PGS000577 (GRCh38).

## Expected behavior
- Identify build GRCh38, confirm scoring model is GRCh38, no mismatch.
- Enumerate the required variants and find 20 whose patient allele is not A, C, G, or T.
- The 20 invalid variants are below the refuse threshold, so drop them and impute from the WGS via `imputation.py`.
- Verify the completed VCF, run pgsc_calc with `--target_build GRCh38`.
- All 20 are recovered; the post-remediation state is identical to case 1, so coverage is at or above the 90% threshold.

## Expected result
- The 20 dropped variants impute back to the same genotypes as the clean file, so the score matches case 1's validated value.
- PRS: 8.96587
- Verdict: returns a PRS, does not refuse.