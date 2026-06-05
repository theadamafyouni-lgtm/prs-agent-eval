# expected — case 9

this is case 1's VCF with operational damage only: decompressed to plain .vcf, records shuffled out of order, and the .tbi removed. the header is untouched and no actual content changed.

the agent should recognize the uncompressed/unsorted/unindexed state and fix it with sort -> bgzip -> tabix (rule 21), preserving content. it must not refuse it as missing or malformed (rule 4 is for missing files), and must not touch the genotypes (rule 22).

- build: grch38 (from the header).
- sex-chromosome variants excluded: 6 (all chrX), not scored, not counted in coverage.
- palindromic excluded: 9, out of the numerator, kept in the denominator.
- unrecoverable autosomal variant: 1, chr10:46046324 (C/T). no record in the WGS, so imputation can't recover it. the agent reports it as unrecovered and does not fabricate a genotype (rule 18).
- total autosomal required: 111 (101 matched + 9 palindromic + 1 unrecoverable).
- matched (non-palindromic, autosomal): 101.
- coverage: 101/111 = 91.0% (over the 90% line, so it scores).
- PRS: 8.96587.

validation is inherited from case 1, since it's the same content and only the packaging differs. the clean 101-variant set and the worksheet live in case_01/expected_output/, referenced not duplicated.

a pass needs PRS = 8.96587 exactly. any deviation means content got altered during the repair (re-keyed alleles, a ref-altering normalization, rewritten genotypes).
