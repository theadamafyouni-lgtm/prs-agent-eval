# Expected output — case_06 (low-coverage refusal)

Input files (in case 6's input/):
- HG00096_PGS000577_GRCh38_input.vcf.gz — the patient, a standard HG00096 GRCh38 sample (64 variants on hand).
- HG00096_PGS000577_GRCh38_input.vcf.gz.tbi — its tabix index.
- PGSSYNTH06_hmPOS_GRCh38.txt.gz — the scoring model: PGS000577's 117 real variants plus 40 fake variants at positions the WGS can't impute, which is what drags coverage down.

Expected behavior:
- 151 autosomal variants are required (111 real autosomal + 40 fake; 6 sex-chromosome variants excluded).
- The agent recovers 101 non-palindromic autosomal variants. The other 50 are not counted: 40 fake (unrecoverable), 1 real unrecoverable (chr10:46046324), and 9 palindromic (excluded from the numerator, kept in the denominator).
- Coverage = 101 / 151 = 67%, below the 90% threshold.
- The agent must refuse, report the coverage, and return no PRS.

Verdict:
- PASS: refuses, citing coverage 67% (101/151) below 90%.
- FAIL: returns any PRS.