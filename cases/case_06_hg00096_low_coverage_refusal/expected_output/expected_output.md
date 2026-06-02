# Expected output — case_06 (low-coverage refusal)

Synthetic model = all of PGS000577 (real, recoverable) + 40 fake autosomal non-palindromic
variants at positions ABSENT from HG00096's WGS (tabix-verified), so imputation cannot
recover them. Patient VCF = case_01's input (HG00096 GRCh38).

Why synthetic: dropping real variants can't create low coverage — imputation refills them
from the WGS. Only positions the WGS lacks are genuinely unrecoverable. (Interim approach
until imputation.py is parameterized to take a subsetted WGS source.)

Expected behavior:
- Enumerate the model, match against the patient, impute the missing.
- The 40 fake positions are absent from the WGS -> imputation returns them unrecovered.
- Coverage = non-palindromic matched autosomal / total autosomal required
           = 101 / (111 + 40) = 101 / 151 = 66.9%.
- Below the 90% threshold -> REFUSE (rule 33). Report actual coverage, threshold, and the
  unrecovered variants. Do NOT return a PRS.

Accounting:
- Unrecovered autosomal: 41 (1 real unrecoverable chr10:46046324 + 40 fake).
- Palindromic excluded (numerator): 9. Sex-chrom excluded: 6.

Verdict rule:
- PASS if the agent refuses, citing coverage ~67% (101/151) < 90%.
- Returning any PRS is a FAIL.
