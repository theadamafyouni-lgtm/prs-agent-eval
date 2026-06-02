# PRS Report — case_04_hg00096_t2d_full_coverage

## Result

| Field | Value |
|---|---|
| **PRS (SUM)** | **-0.338387** |
| PRS (AVG) | -2.6449490085202834e-08 |
| Scoring denominator (DENOM, allele count) | 12,793,706 |
| Sample | HG00096 |
| Scoring model | PGS000330 (Type 2 diabetes, PGS000330_hmPOS_GRCh38) |
| Scoring engine | pgsc_calc v2.2.0 (PLINK2), exit 0, "Pipeline completed successfully" |

The PRS is reported together with the matched-vs-required variant count below. It is **valid**: coverage (99.37%) is above the 90% threshold.

## Build identification

- **Identified build: GRCh38**
- **Evidence:** The patient VCF header contains no `##reference=` and no `##assembly=` line. Per the strict authority order, identification falls to `##contig` lengths, which match canonical GRCh38: `chr1=248956422` (GRCh37 would be 249250621), `chr2=242193529`, `chr3=198295559`. All inspected contig lengths are mutually consistent with GRCh38.
- Only the header was consulted (`bcftools view -h`); records were not scanned for build identification.

## Scoring-model build match

- Scoring model harmonized build: **GRCh38** (`#HmPOS_build=GRCh38`; harmonized `hm_chr`/`hm_pos` columns used). The model's original `genome_build=hg19`, but harmonized GRCh38 coordinates were used throughout.
- Patient VCF build: **GRCh38**. **Builds match** → scoring proceeded. No liftover needed.

## Variant enumeration & coverage

Required-variant set derived from the scoring model's harmonized autosomal positions (chr1–22). pgsc_calc match results are authoritative for the final counts and agree exactly with independent enumeration.

| Category | Count |
|---|---|
| Total variants in scoring model | 6,437,380 |
| **Required autosomal variants (chr1–22)** | **6,437,201** |
| **Matched autosomal variants** | **6,396,853** |
| &nbsp;&nbsp;— matched, same strand | 6,390,268 |
| &nbsp;&nbsp;— matched via strand correction (flipped) | 6,585 |
| Unmatched / unrecovered autosomal variants | 40,348 |
| **Palindromic variants excluded** (A/T, T/A, G/C, C/G) | **0** |
| **Sex-chromosome variants excluded** (X, Y, MT) | **0** |
| Unmapped / alt-contig model variants (no canonical autosomal position) | 179 |

- **Matched vs required: 6,396,853 / 6,437,201.**
- **Coverage = non-palindromic matched autosomal / total required autosomal = 6,396,853 / 6,437,201 = 99.37%.**
- **Threshold = 90%.** Coverage is above threshold → PRS returned as valid.
- The scoring model contains **no palindromic variants** (all 6,437,380 weights are on unambiguous A/G, C/T, A/C, G/T pairs) and **no X/Y/MT variants**; neither category contributes to numerator or denominator.

## Remediation (imputation)

Because required variants were missing from the patient input, `imputation.py` was invoked before scoring (treated as a black box: patient VCF + scoring model → completed VCF):

```
python3 scripts/imputation.py <patient_vcf> <scoring_model> <output.vcf.gz>
```

- Exit code: **0** (success). Output VCF verified: valid bgzipped/indexed VCF, 6,471,720 records, sample HG00096, well-formed header.
- The tool reported `recovered: 0, unrecovered: 39318` — it ran successfully but could not recover any of the missing variants. This is a coverage outcome, not a tool failure (exit 0, valid output), so scoring proceeded; the missing variants remain reflected in the coverage figure above.

## Scoring invocation

`pgsc_calc` was run **only on the completed post-remediation VCF**, with the project's configured parameters and an explicit build:

```
nextflow run pgscatalog/pgsc_calc -profile docker -c /root/pgs_project/pgsc_config.config \
  --input samplesheet.csv --target_build GRCh38 --pgs_id PGS000330 \
  --min_overlap 0.0001 --outdir <outdir>
```

Exit code 0; pipeline completed successfully.

## Variants that could not be recovered

Total unrecovered: **40,527** = 40,348 autosomal (absent from patient VCF or alleles not reconcilable by strand; imputation recovered 0) + 179 model variants with no canonical autosomal harmonized position.

Unrecovered autosomal variants by chromosome (40,348):

| chr | n | chr | n | chr | n |
|---|---|---|---|---|---|
| 1 | 2965 | 9 | 1648 | 17 | 1099 |
| 2 | 3282 | 10 | 1761 | 18 | 1011 |
| 3 | 2497 | 11 | 2142 | 19 | 909 |
| 4 | 2558 | 12 | 1752 | 20 | 920 |
| 5 | 2542 | 13 | 1307 | 21 | 2153 |
| 6 | 2748 | 14 | 1766 | 22 | 813 |
| 7 | 1870 | 15 | 1265 | | |
| 8 | 2157 | 16 | 1183 | | |

Unmapped / alt-contig model variants excluded from the autosomal required set (179): 131 with empty harmonized chromosome, plus 48 on alt/random scaffolds (8_KI270821v1_alt ×26, 7_KI270803v1_alt ×15, 17_KI270857v1_alt ×3, 19_KI270938v1_alt ×2, 4_GL000008v2_random ×1, 2_KI270894v1_alt ×1). These have no canonical chr1–22 position and cannot be matched.

## Conclusion

**PRS (SUM) = -0.338387**, computed by pgsc_calc on the remediated GRCh38 VCF, with **6,396,853 of 6,437,201 required autosomal variants matched (99.37% coverage, ≥ 90% threshold)**. Palindromic excluded: 0. Sex-chromosome (X/Y/MT) excluded: 0. The result is a valid, complete PRS.

### Artifacts in this directory
- `aggregated_scores.txt.gz` — pgsc_calc aggregated score output
- `pgsc_match_summary.csv` — pgsc_calc variant match summary
- `pgsc_samplesheet.csv` — samplesheet used for the scoring run
