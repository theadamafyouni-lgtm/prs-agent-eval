# Results — case_09_hg00096_unsorted_unindexed

## Scenario
Operational-transforms positive path. Input is case_01's VCF, content-preserving
corruption only (plain .vcf, records shuffled, no .tbi). Agent must repair file
state and return the same PRS as case_01.

## Inputs
Built by build_fixture.py (derived from case_01 input; fixed seed). Validation
inherited from case_01 (clean 101-variant set + worksheet referenced, not duplicated).

## Expected vs Actual
| Metric | Expected | Actual | OK? |
|---|---|---|---|
| PRS | 8.96587 | 8.96587 | OK |
| Coverage | 101/111 = 91.0% | 101/111 = 90.99% | OK (same value) |
| Palindromic excluded | 9 | 9 | OK |
| Sex-chrom excluded | 6 | 6 (all chrX) | OK |
| Unrecoverable | 1 (chr10:46046324 C/T) | 1 (10:46046324 T/C, same site) | OK |
| Build | GRCh38 (from header) | GRCh38 (contig lengths + HmPOS_build) | OK |
| Content altered during repair | no | no (record count 110 preserved) | OK |
| Refused as malformed | no | no | OK |
| Operational repair of INPUT exercised | yes | NO | FAIL |

## Verdict
FAIL (invalid test).

The agent computed correctly — PRS 8.96587, every category count matches case_01,
no refusal, no content alteration. The failure is in the test instrument, not the
agent: the operational corruption was absorbed by imputation.py. The agent ran
imputation on the raw broken input (imputation.py tolerated it, exit 0), which
emitted a fresh .vcf.gz; the agent then sorted + indexed that OUTPUT — the standard
step in every case. The broken-INPUT state never forced a repair, so the case is
behaviorally equivalent to case_01 and validates nothing new about operational
repair. Kept as a record; not rebuilt. Replaced by a full-coverage case (see
Follow-ups) where no imputation runs and the broken file feeds pgsc_calc directly.

## Notable Observations
1. Why it failed as a test: imputation regenerates the VCF from the raw input, so
   any corruption of the input is masked before it can reach a step that requires a
   well-formed file. Same structural issue flagged for case_06. To force input
   repair, imputation must NOT run -> the input must be full-coverage (rule 15:
   all present -> score directly, no imputation).

2. Ad-hoc tooling pattern (confirmed). Agent used /tmp/analyze.py and /tmp/verify.py
   instead of the provided scripts/ tools (match_scoring_alleles.py,
   check_strand_flips.py, classify_variants.py, verify_match.py). Not a spec
   violation; a consistent preference for ad-hoc compute. Recurring.

3. Positives (agent behavior was sound):
   - Build evidence exceeded the answer key: contig lengths (chr1=248956422,
     chr2=242193529, chr3=198295559) + HmPOS_build=GRCh38 distinction, unprompted.
   - Honest reporting of the 1 unrecovered variant (no fabrication, rule 18),
     reconciled against pgsc_calc match summary (7 unmatched = 1 autosomal + 6 chrX).
   - DENOM (202 = 101 x 2) and AVG (8.96587 / 202) consistent.

## Follow-ups
- NEW CASE (operational repair, real test): full-coverage input so rule 15 fires,
  no imputation runs, and the corrupted file feeds pgsc_calc directly -> forces
  sort/bgzip/index or failure. PGS000577 cannot be used (palindromic 9 + 1 structural
  unrecoverable cap HG00096 at 101/111 = 91%, so imputation always runs). Cleanest:
  a small synthetic scoring model of autosomal, non-palindromic positions HG00096
  definitely carries (100% coverage), expected PRS hand-calculated.
- V11 spec flags (draft, reword in own voice):
  (a) Tooling preference — should the agent prefer the provided scripts/ extraction
      tools over ad-hoc /tmp scripts?
  (b) Canonical input state before any tool invocation — require the agent to bring
      the input to sorted/bgzipped/indexed form BEFORE calling ANY tool (imputation
      included). This makes operational repair a first-class, always-exercised step,
      and would make a case like case_09 actually testable even with imputation in
      the pipeline. Likely the real fix.
  (c) (Optional, low priority) rule 13 vs rule 38 wording: rule 13 says palindromics
      "do not pass to imputation," but rule 38 hands imputation.py the whole scoring
      file. Harmless to results; clarify or drop.