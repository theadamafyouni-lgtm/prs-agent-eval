# case_01 — HG00096, GRCh38, missing data (autosomal coverage pass)

## Scenario
Patient HG00096 (1000 Genomes, GRCh38) scored against PGS000577. The input VCF is
missing 37 of the patient's 101 matchable autosomal variants (simulated missing data).
Tests build identification, sex-chromosome exclusion, imputation of missing autosomal
variants, autosomal coverage gating, and scoring.

## Inputs
- Patient VCF:   input/HG00096_PGS000577_GRCh38_input.vcf.gz  (64 variants)
- Scoring model: scoring_models/PGS000577/PGS000577_hmPOS_GRCh38.txt.gz  (117 variants)
- Agent prompt:  command.txt
- Answer key:    expected_output/expected_output.md

## Pass criteria (expected behavior)
1. Identifies build as GRCh38 from the header.
2. Excludes the 6 X-chromosome variants (autosomal-only scoring).
3. Detects missing autosomal variants and runs imputation to recover them.
4. Coverage = 101 / 111 = 91.0% >= 90% -> proceeds to score.
5. Excludes the 9 palindromic variants from the matched count.
6. Runs pgsc_calc and returns the PRS.
7. Reports PRS, matched/required count, palindromic excluded (9), sex-chromosome excluded (6), and build evidence.

## Result — PASS (2026-05-28)
Agent run end-to-end via command.txt prompt. All pass criteria met.

| Check | Expected | Agent |
|---|---|---|
| Build | GRCh38 | GRCh38 (contig lengths) |
| Sex-chrom excluded | 6 chrX | 6 |
| Palindromic excluded | 9 | 9 |
| Unrecoverable autosomal | chr10:46046324, reported not fabricated | chr10:46046324, reported not fabricated |
| Autosomal required | 111 | 111 |
| Matched | 101 | 101 |
| Coverage | 101/111 = 91.0% -> pass | 90.99% -> scored |
| PRS | 8.96587 | 8.96587 |

Notes:
- Confirms PRS 8.96587 for the 101-variant set. [CONFIRM] flag on answer key can be removed.
- Agent correctly gated on autosomal coverage (101/111 = 91%) and did not gate on pgsc_calc's
  own 101/117 = 86.32% figure.
- Minor: agent's Remediation prose had a garbled missing-variant breakdown ("38 + 8 = 53");
  structured tables were all correct.
