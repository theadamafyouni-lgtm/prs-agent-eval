# case 4 results

## verdict: pass
every number matches the reference run exactly. this is the big multi-million-variant model (PGS000330), run end to end on HG00096 pre-filtered to the PGS positions.

## the numbers

| metric | expected | agent |
|---|---|---|
| PRS SUM | -0.338387 | -0.338387 |
| DENOM | 12,793,706 | 12,793,706 |
| matched variants | 6,396,853 | 6,396,853 |
| direct match | 6,390,268 | 6,390,268 |
| strand-flipped | 6,585 | 6,585 |
| total unmatched | 40,527 | 40,527 |
| match rate | 99.37% | 99.37% |
| build | GRCh38 | GRCh38 |

the reasoning held up too: it called grch38 off the contig lengths after noting no ##reference/##assembly, split HmPOS_build from genome_build, and independently counted the unmatched variants (40,348 autosomal + 179 unmapped/alt-contig = 40,527), landing on the same number pgsc_calc did.

## timing
- reference pgsc_calc run: ~32 min (1.1 CPU hours, 9 processes).
- agent run, active compute: ~40-45 min, of which ~33 was pgsc_calc itself.
- inside pgsc_calc it was mostly FORMAT_SCOREFILES (17m30s) and MATCH_COMBINE (11m16s); match_variants, plink2, scoring, aggregate and report were a couple minutes combined.
- imputation.py and the agent's own enumeration added a few minutes. basically all the real work was pgsc_calc, the rest was waiting on background jobs.

## what stood out
- imputation actually ran, even though the expected said it wouldn't. that's the agent reading coverage as allele-match, not position-only: 40,348 variants looked "missing" because their REF/ALT didn't reconcile with the PGS, so it routed them through imputation. the script exited clean (recovered 0 of 39,318), didn't move the PRS, just burned a little compute. so the expected's "no imputation" line is wrong, it was written assuming position-only coverage, which isn't how the agent (correctly) works. this is V11 item 4 in action.
- the build reasoning was unprompted, the same explicit authority-order walk case 2 was built to test. it's internalizing the spec, not pattern-matching.
- its independent unmatched count (40,348 + 179 = 40,527) hit pgsc_calc's number exactly, good cross-check that its classification logic is right.
- total variant count was off by 1: it said 6,437,380, PGS000330 has 6,437,381. same rounding artifact from before, doesn't affect anything.
- imputation reported 39,318 unrecovered vs pgsc_calc's 40,348 autosomal-unmatched. probably different counting categories (imputation may not count allele-mismatches as "unrecovered"). want to understand this before case 6, where the imputation logic matters more.
- cong's two concerns both check out: DENOM is 2 × matched (6,396,853), not 2 × all variants, and imputation didn't fabricate, it honestly reported what it couldn't recover instead of guessing.

## follow-ups
- update expected_output.md so it expects imputation to run (the agent counts allele-match coverage, so missing or mismatched variants always trigger it under the current spec).
- track the 39,318 vs 40,348 imputation/pgsc_calc count gap before case 6.
