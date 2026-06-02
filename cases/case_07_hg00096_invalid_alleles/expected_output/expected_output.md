# Expected output — case_07 (invalid alleles, EXPLORATORY)

Input is case_01's VCF with ~20% of records corrupted: a REF or ALT base replaced with an
invalid non-ACGT character (Z, IUPAC ambiguity codes). Below the proposed 25%
"structurally malformed -> refuse" threshold (V11 #6).

EXPLORATORY: the current spec (V10) says nothing about invalid alleles. This run observes
what the agent does, to shape V11 #6. No firm pass/fail under the current spec.

Anticipated future behavior (once #6 exists), at <25% invalid:
- Detect invalid rows, drop them, treat positions as missing, impute from WGS, recover,
  return case_01's PRS = 8.96587.

What may happen NOW (to confirm):
- Corrupted patient records won't match the model's valid alleles -> those model variants
  read as "missing" -> imputed from WGS -> recovered. If so, the agent may land on 8.96587
  WITHOUT any invalid-allele rule (incidental robustness via missing->impute). OR the invalid
  characters crash a tool (agent matching, imputation.py, pgsc_calc) -> stop (cf. case_08).
  OR it refuses / mishandles.

Capture for V11 #6:
- Did it notice the alleles were invalid, or just treat them as non-matching/missing?
- Did anything crash on the invalid characters?
- Final coverage / PRS if any (8.96587 = clean recovery via imputation).
- Corrupted positions are logged by build_fixture for comparison.
