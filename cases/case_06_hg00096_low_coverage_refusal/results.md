# Results — case_06_hg00096_low_coverage_refusal

## Scenario
Low-coverage refusal. Synthetic model = all of PGS000577 (real, recoverable) + 40
fake autosomal non-palindromic variants at positions absent from HG00096's WGS
(tabix-verified), so imputation cannot recover them. Patient VCF = case_01's input
(GRCh38). The fakes drag coverage below 90%; the agent should refuse (rule 33).

## Inputs
Built by build_fixture.py: PGS000577 + 40 WGS-absent fake rows -> synthetic model.
Patient VCF referenced from case_01 (not copied).

## Expected vs Actual
| Metric | Expected | Actual | OK? |
|---|---|---|---|
| Outcome | refuse, no PRS | refused, no PRS | OK |
| Coverage | 101/151 = 66.9% | 101/151 = 66.89% | OK |
| Total model variants | 157 (117 + 40) | 157 | OK |
| Autosomal required (denominator) | 151 | 151 | OK |
| Non-palindromic matched | 101 | 101 | OK |
| Unrecovered autosomal | 41 (40 fake + chr10:46046324) | 41 | OK |
| Palindromic excluded (numerator) | 9 | 9 | OK |
| Sex-chrom excluded | 6 (all chrX) | 6 (all chrX) | OK |
| Build | GRCh38 (contig lengths) | GRCh38 (contig lengths) | OK |
| PRS returned | no | no | OK |

## Verdict
PASS.

The agent enumerated the synthetic model, imputed the missing variants (recovered 46
of the missing reals, left the 40 WGS-absent fakes + the real chr10:46046324
unrecoverable), computed coverage as 101/151 = 66.89%, and refused per rule 33 —
reporting the coverage, the 90% threshold, and the full unrecovered list, with no
fabricated or partial score. Exactly the intended behavior.

## Notable Observations
1. First validation of the coverage gate (rule 33) on genuine low coverage. Confirms:
   - the gate fires below 90% and returns no PRS;
   - the denominator math is correct — the 40 fakes are counted in the autosomal
     denominator, palindromics are in the denominator but excluded from the numerator,
     and sex-chrom are excluded from both;
   - the refusal is reported honestly (coverage, threshold, all 41 unrecovered listed),
     no partial score.
2. The synthetic + tabix-verify approach worked: imputation recovered the real missing
   variants from the WGS but returned the 40 fakes unrecovered (their positions are
   genuinely absent from the WGS). Independent cross-check: imputation reported
   recovered=46, unrecovered=47 = 6 chrX + 41 autosomal, matching the agent's 41.
3. Robust to the pending V11 #3 (coverage denominator) decision: the 40 fakes are
   mappable autosomal positions, so they stay in the denominator under both current
   rule 32 and the V11 #3 "theoretically scoreable" definition. Coverage stays
   101/151 < 90% either way; the refusal does not depend on the #3 resolution.
4. Fixture-hygiene note (does not affect the result): the synthetic model inherited
   PGS000577's metadata header, so it self-reports pgs_id=PGS000577 despite the
   PGSSYNTH06 filename — the agent reported PGS_ID PGS000577. Harmless here (no
   pgsc_calc, refused first), but if a synthetic model ever needed scoring we'd fix
   the metadata.

## Follow-ups
- This is the interim "fake data" approach to force genuine low coverage. The real
  fix (deferred case_06 plan) is parameterizing imputation.py to take a subsetted WGS
  source, so low coverage can be created from real data. Not blocking; this version
  validates the gate.
