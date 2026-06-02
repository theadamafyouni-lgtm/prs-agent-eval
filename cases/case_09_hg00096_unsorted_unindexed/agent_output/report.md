# PRS Structured Report — case_09_hg00096_unsorted_unindexed

## Result
- **PRS (PGS000577) SUM:** 8.96587
- **PRS AVG (per-allele):** 0.04438549504950495
- **Scoring DENOM (alleles):** 202  (= 101 matched variants × 2)
- **Result status:** VALID — coverage ≥ 90% threshold met.

## Matched vs. required variants
- **Matched (scored):** 101
- **Total required autosomal variants (denominator):** 111
- **Coverage:** 101 / 111 = **90.99%** (configured threshold: 90% → PASS)

Required-variant accounting (scoring model PGS000577 = 117 total variants):
| Category | Count |
|---|---|
| Total variants in scoring model | 117 |
| Sex-chromosome (chrX) — excluded from scoring entirely | 6 |
| Autosomal required (denominator) | 111 |
| Palindromic autosomal — excluded from numerator only | 9 |
| Non-palindromic autosomal | 102 |
| Non-palindromic autosomal matched (numerator) | 101 |
| Non-palindromic autosomal unrecovered | 1 |

## Genome build
- **Identified build: GRCh38**
- **Evidence:** No `##reference=` or `##assembly=` header lines were present, so the highest-authority signal available was `##contig` lengths. These match GRCh38 canonical lengths, e.g. **chr1=248956422, chr2=242193529, chr3=198295559**. Scoring model is harmonized to GRCh38 (`#HmPOS_build=GRCh38`). Builds match → scoring proceeded.

## Palindromic variants (excluded from numerator only)
Count: **9**. Strand cannot be inferred without external frequency data, so they are not matched and not imputed:
- 3:107243674 G/C, 6:32433162 G/C, 9:22041999 G/C, 10:112952395 G/C, 11:67184494 C/G, 11:108272729 G/C, 14:36669089 C/G, 15:40630717 C/G, 18:54246103 C/G

## Sex-chromosome variants excluded from scoring
Count: **6** (all chrX; not scored, not imputed, not counted in numerator or denominator):
- X:9846095 A/G, X:11464514 C/T, X:51498820 C/T, X:52867918 C/T, X:67801708 T/C, X:71188133 G/A

## Variants that could not be recovered
After running the imputation tool (exit 0; recovered 46 of 53 missing), **1 autosomal required variant remained unrecovered** and is therefore unmatched/unscored:
- **10:46046324 T/C** — missing from patient VCF and not recovered by imputation.

(The 6 chrX variants reported above are excluded from the required set by spec and are not counted as coverage shortfalls. pgsc_calc's match summary independently reports the same 7 "unmatched" = this 1 autosomal + 6 chrX.)

## Pipeline notes
- Input VCF was unsorted/unindexed. Imputation was run on the raw input; its `.vcf.gz` output was then coordinate-sorted (`bcftools sort`) and tabix-indexed for pgsc_calc compatibility — operational transforms only; no variant or genotype content was altered (record count unchanged: 110).
- pgsc_calc invoked with `--target_build GRCh38 --pgs_id PGS000577 --min_overlap 0.0001`; pipeline completed successfully (exit 0).
- pgsc_calc match summary: matched=101, excluded(palindromic/ambiguous)=9, unmatched=7.
