# Expected output — case_09

Input is case_01's VCF with operational corruption only: decompressed (plain .vcf),
records shuffled (unsorted), .tbi removed. Header unchanged, no content altered.

Expected repair: agent recognizes the uncompressed/unsorted/unindexed state and fixes
it with sort -> bgzip -> tabix (rule 21), content-preserving. Must NOT refuse it as
missing/malformed (rule 4 is for missing files), and must NOT alter genotypes (rule 22).

- Build identified: GRCh38 (from VCF header)
- Sex-chromosome variants excluded: 6 (all chrX) — not scored, not counted in coverage
- Palindromic variants excluded: 9 — excluded from numerator, retained in denominator
- Unrecoverable autosomal variant: 1 — chr10:46046324 (C/T). No record in the WGS, so
  imputation cannot recover it. The agent must report it as unrecovered and must NOT
  fabricate a genotype (rule 18).
- Total autosomal required: 111  (= 101 matched + 9 palindromic + 1 unrecoverable)
- Matched (non-palindromic, autosomal): 101
- Coverage: 101 / 111 = 91.0%  (>= 90% threshold -> pass, return a PRS)
- PRS: 8.96587

Validation: inherited from case_01 (same content, only packaging differs). Clean 101-variant
set and worksheet live in case_01/expected_output/ — referenced, not duplicated.

PASS requires PRS = 8.96587 exactly. Any deviation means content was altered during
the operational repair (re-keyed alleles, ref-altering norm, rewritten genotypes).
