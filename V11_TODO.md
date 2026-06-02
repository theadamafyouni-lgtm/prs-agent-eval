# V11 Spec — Items to Add or Clarify

Open items identified during V7-V10 work. Each entry: what's needed, why, where in the spec it fits.

## 1. Model selection by patient ancestry (NEW — next week's main work)

Multiple scoring models often exist for the same trait, trained on different populations
(e.g., PGS000014, PGS000330, PGS002243 for T2D). Agent needs explicit guidance on:

- How to read each scoring model's ancestry from PGS Catalog metadata
- How the patient's ancestry is supplied (input contract — likely metadata file alongside the VCF, e.g., `ancestry.json` with `"population": "EUR"`)
- How to choose when more than one model matches a request

Spec location: New phase or extension of Phase 3 (Scoring model match).

## 2. HmPOS_build vs genome_build distinction

PGS Catalog scoring files have both fields:
- `genome_build` = original GWAS build
- `HmPOS_build` = harmonized operative build (this is what should match the target VCF)

The agent has been getting this right via implicit reasoning (case_02 demonstrated correct
behavior), but it should be an explicit rule rather than depending on the agent inferring it.

Spec location: Phase 3 (Scoring model match), rule 10.

## 3. Coverage threshold denominator semantics

Which variants count toward rule 32's 90% coverage gate denominator?

The denominator should be the **theoretically scoreable** subset of the scoring model — variants the agent could plausibly match given any valid input on the target build. Specifically exclude:

- **Unmapped variants** (empty `hm_chr` — couldn't be lifted to target build)
- **Alt/random contigs** (mapped but not to canonical chr1-22)
- **Sex chromosomes** (for autosomal-only modeling)
- **Palindromic SNPs** if we're filtering them (depends on resolution of #5)

Numerator: matched in patient (direct or strand-resolved).

Including unmappable variants in the denominator would penalize the agent for an impossible task. PGS000330 example: 179 of 6,437,381 total are structurally unscoreable on GRCh38, so denominator should be 6,437,201 (autosomal mappable), not the full 6,437,381.

This affects case_01's pass criteria directly.

Spec location: Phase 6 (Reporting), rule 32.

## 4. Imputation skip threshold (NEW — flagged during case_04)

Currently the agent calls imputation.py whenever there's any missing data, even at 99%+
matched coverage. For high-coverage inputs this is wasted compute (imputation finds nothing
to add, especially when input was derived from the WGS source itself).

Add a rule like: "If matched coverage ≥ X% (suggest 95%), imputation step is optional
and may be skipped."

Spec location: Phase 4 (Variant enumeration & imputation), rules 11-22.

## 5. Ambiguous SNP filtering applicability

Currently the agent filters palindromic SNPs (A/T, G/C) because their strand can't be
resolved. But: should this still apply when VCF and scoring model share the same build?
If alleles are on the same coordinate system, strand ambiguity may not arise the same way.

Decision needed: when (if ever) is palindromic filtering skipped?

Spec location: Phase 4.

## 6. Invalid allele handling (needed before case_07)

For VCF rows where REF or ALT contains non-ACGT characters (Z, M, dots, IUPAC ambiguity codes, etc.):

**Behavior:** Drop the invalid row, treat the position as missing, route through imputation
(same pathway as missing variants). This unifies invalid and missing into a single
"needs imputation" category rather than having a separate handling mode.

**Threshold for malformed input:** If invalid rows exceed 25% of total input, treat input
as structurally malformed and refuse. Below that threshold, recovery via imputation is appropriate.

Implication for case_07: this becomes a recovery test (not refusal) — the agent should
successfully impute past the invalid rows and compute a valid PRS.

Spec location: Phase 4.

## 7. Trust posture toward internal tools (NEW — flagged during case_04)

Currently the agent verifies tool output after every call, including for controlled
internal scripts (`scripts/imputation.py`, etc.) whose exit codes are meaningful and
which we wrote ourselves. This adds compute and reasoning noise without catching new
failure modes for in-house tools.

Add a rule that distinguishes:
- Internal/controlled tools (in `scripts/`, exit-code-meaningful) → trust on clean exit, skip post-execution verification
- External/uncontrolled tools (bcftools, pgsc_calc, etc.) → verify outputs as needed

Spec location: New rule under Phase 4 or a general "tool usage" section.

## 8. Canonical input state before tool invocation (NEW — flagged during case_09)

The agent should bring the input VCF to canonical operational form — coordinate-sorted,
bgzipped, tabix-indexed — **before** invoking any tool (imputation.py, pgsc_calc), not after.

**Why:** case_09 handed the agent an uncompressed, unsorted, unindexed VCF. The agent ran
imputation.py on the raw file (imputation tolerated it, exit 0) and only sorted/indexed the
imputation *output* — the standard downstream step every case already does. The broken-input
state was absorbed by imputation and never forced a repair, so the operational-repair test
couldn't verify the behavior it was built for. The permission to do operational transforms
exists (rule 21), but nothing requires the agent to apply it to the input up front — so the
behavior is unobservable whenever imputation runs.

**What this buys:** making input canonicalization a required first step turns operational
repair into an always-exercised, observable behavior — testable even with imputation in the
pipeline (would have made case_09 a valid test without a rebuild). Content-preserving only
(sort/bgzip/index); no allele re-keying or genotype changes, consistent with rules 21-22.

Note: also explains why case_09 and case_06 can't test what they intend under the current
spec — imputation regenerates the VCF from the raw input and masks any input manipulation.

Spec location: Phase 4, as an input-preparation step ahead of rule 16 (imputation), or a
general rule near rule 19.

## 9. Tool selection: provided tools vs ad-hoc compute (NEW — flagged during case_09)

Across case_09 the agent wrote its own `/tmp` scripts for variant enumeration, palindromic
flagging, strand matching, coverage, and post-imputation verification — instead of the
provided `scripts/` tools (`match_scoring_alleles.py`, `check_strand_flips.py`,
`classify_variants.py`, `verify_match.py`). Not a spec violation (the spec doesn't mandate
those tools), but a consistent pattern across the whole run.

**Decision needed:** should the spec express a preference — use a provided extraction tool
when one fits, fall back to ad-hoc compute only when none does? Or is ad-hoc compute fine
provided the reasoning is sound? This touches the core methodology ("agent makes judgments,
tools do mechanical extraction"): ad-hoc compute *is* the agent doing extraction itself,
which may or may not be what we intend.

Relates to item 7 — both are tool-usage posture (7 = whether to verify tool output; this =
whether to use the provided tools at all). Could share one "tool usage" section.

Spec location: same "tool usage" section as item 7.

## 10. rule 13 vs rule 38 wording — palindromic into imputation (low priority)

Rule 13 says palindromic variants "do not pass to imputation," but rule 38 invokes
imputation.py with the whole scoring file, which includes palindromic (and sex-chrom)
variants — so they enter imputation regardless. Harmless to results (the coverage division
excludes them; imputation can't resolve palindromic strand anyway), but the two rules
contradict on their face.

**Clarify:** does rule 13 mean "don't include palindromic in the agent's own missing-set
tracking" (the achievable reading, given rule 19 black-box + rule 38 whole-file), or is the
agent expected to build and pass a filtered scoring file? Probably the former — soften
rule 13's wording to match what's actually enforceable.

Spec location: Phase 4, rule 13 (cross-ref rule 38).