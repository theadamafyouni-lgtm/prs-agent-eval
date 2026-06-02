# Expected output — case_01

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
