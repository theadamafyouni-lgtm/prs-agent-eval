# PRS Structured Report

## Result: NO SCORE RETURNED — coverage below threshold

A valid PRS could not be returned. After remediation (imputation), the
non-palindromic autosomal coverage was **66.89%**, which is below the configured
**90%** minimum. Per AGENT_SPEC.md (§Reporting), a partial score below threshold
is not a valid result, so no PRS value is reported.

All inputs were well-formed, the genome builds matched, and the imputation tool
completed successfully (exit code 0). The refusal is due solely to insufficient
variant coverage after remediation.

## Inputs

| Item | Value |
|------|-------|
| Patient VCF | `cases/case_01_hg00096_grch38_missing/input/HG00096_PGS000577_GRCh38_input.vcf.gz` |
| Scoring model | `cases/case_06_hg00096_low_coverage_refusal/input/PGSSYNTH06_hmPOS_GRCh38.txt.gz` |
| PGS ID | PGS000577 |

## Build identification

- **Identified build: GRCh38**
- **Evidence:** The patient VCF header contains no `##reference=` or `##assembly=`
  lines. The highest-authority signal present is `##contig` length. GRCh38
  identified from contig lengths: `chr1=248956422` (GRCh37 chr1 would be
  249250621); `chr2=242193529`, `chr3=198295559` are likewise GRCh38 lengths.
- **Scoring model build:** GRCh38. The model is the harmonized product
  (`HmPOS_build=GRCh38`); matching used the harmonized positions (`hm_chr`/`hm_pos`).
  Patient VCF coordinates align with these harmonized positions (e.g.
  chr1:150685811).
- **Build match:** Patient (GRCh38) and scoring model (GRCh38) agree. No mismatch.

## Variant accounting

| Category | Count |
|----------|-------|
| Total variants in scoring model | 157 |
| Sex-chromosome variants excluded (X/Y/MT) | 6 (all chrX) |
| Total **autosomal** required variants (coverage denominator) | 151 |
| Palindromic autosomal variants (excluded from numerator only) | 9 |
| Non-palindromic autosomal required | 142 |
| Non-palindromic autosomal **matched** after imputation (numerator) | 101 |
| Non-palindromic autosomal **unrecovered** after imputation | 41 |
| Strand-corrected matches | 0 |

**Matched vs required: 101 / 151 autosomal variants.**

## Coverage

- **Coverage = non-palindromic matched autosomal / total autosomal required = 101 / 151 = 66.89%**
- **Configured threshold: 90%**
- **66.89% < 90% → below threshold. No PRS returned.**

## Remediation performed

Imputation was invoked because required variants were missing from the patient VCF
(64/151 autosomal matched before remediation, 42.38%).

- Tool: `scripts/imputation.py` (three positional args; output `.vcf.gz`)
- Exit code: **0** (success); output VCF verified readable, 110 records.
- Reported by tool: present=64, recovered=46, unrecovered=47 (of which 6 are chrX,
  excluded from scoring).
- Coverage improved from 42.38% to 66.89%, still below threshold.

## Excluded variants (not scored)

### Sex-chromosome variants excluded (6, all chrX)
chrX:9846095, chrX:11464514, chrX:51498820, chrX:52867918, chrX:67801708, chrX:71188133
(GRCh38 harmonized positions)

### Palindromic autosomal variants excluded from numerator (9)
chr3:107243674 (G/C), chr6:32433162 (G/C), chr9:22041999 (G/C),
chr10:112952395 (G/C), chr11:67184494 (C/G), chr11:108272729 (G/C),
chr14:36669089 (C/G), chr15:40630717 (C/G), chr18:54246103 (C/G)

## Unrecovered required variants after imputation (41, autosomal non-palindromic)

These required variants remained absent from the patient VCF after imputation and
could not be recovered. (Coordinates are GRCh38 harmonized; effect/other allele shown.)

| chr:pos | effect/other |
|---------|--------------|
| chr1:51333009 | A/G |
| chr1:187593357 | G/A |
| chr3:4644812 | A/G |
| chr3:124836168 | A/G |
| chr5:137950050 | G/A |
| chr7:7179097 | G/A |
| chr7:88004724 | G/A |
| chr7:139953972 | T/C |
| chr8:99525165 | T/C |
| chr8:142579219 | A/G |
| chr9:3200625 | C/T |
| chr9:66546079 | T/C |
| chr9:102875740 | A/G |
| chr9:111150948 | C/T |
| chr10:9491721 | G/A |
| chr10:46046324 | T/C |
| chr10:83773946 | G/A |
| chr11:68059936 | G/A |
| chr11:93506860 | C/T |
| chr12:18664244 | T/C |
| chr13:50735745 | T/C |
| chr13:52722876 | T/C |
| chr13:64012154 | C/T |
| chr14:38555243 | G/A |
| chr15:1992369 | T/C |
| chr15:4027020 | G/A |
| chr15:9755017 | C/T |
| chr15:92836671 | T/C |
| chr16:3853996 | T/C |
| chr16:16982925 | G/A |
| chr16:30493366 | G/A |
| chr16:40272877 | T/C |
| chr16:61963273 | C/T |
| chr16:89038954 | A/G |
| chr19:16711351 | G/A |
| chr19:38032309 | G/A |
| chr19:47859750 | T/C |
| chr20:32023859 | C/T |
| chr20:48232229 | T/C |
| chr21:8223644 | G/A |
| chr22:33952038 | G/A |

**Category summary:** all 41 unrecovered variants are autosomal, non-palindromic
required variants that imputation could not fill. They are distributed across
chromosomes 1, 3, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19, 20, 21, 22.

## Conclusion

No PRS is returned. Post-remediation coverage (66.89%) is below the configured 90%
threshold. The result is a refusal driven by insufficient coverage, not by any
input or tool failure.
