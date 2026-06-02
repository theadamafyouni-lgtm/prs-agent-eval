# case_04 — Expected Output

## Scenario
HG00096 WGS pre-filtered to PGS000330 positions; agent should run end-to-end PRS computation on a large multi-million-variant scoring model.

## Expected Agent Behavior
1. Identify build as GRCh38 from header signals (contig lengths).
2. Match against PGS000330_hmPOS_GRCh38 (HmPOS_build = GRCh38). No mismatch — proceed.
3. Determine variant coverage from input — full position coverage, no imputation needed.
4. Invoke pgsc_calc with `--target_build GRCh38` and `--pgs_id PGS000330`.
5. Report PRS SUM and matched-variant count from pgsc_calc output.

## Expected Values
- **PRS SUM:** -0.338387
- **DENOM:** 12,793,706 (= 2 × matched variants)
- **Matched variants:** 6,396,853
  - Direct exact match: 6,390,268 (99.27%)
  - Matched via strand flip: 6,585 (0.10%)
- **Unmatched:** 40,527 (0.63%)
- **Match rate of PGS000330:** 99.37%

## Pass Criteria
- Agent returns PRS SUM = -0.338387 (or equivalent within float precision)
- Agent reports matched variant count = 6,396,853
- Agent does not fabricate the unmatched 40,527 — reports them honestly as excluded
- No imputation step invoked (input already complete at PGS positions)

## Reference Run
Independent pgsc_calc run on the same input is preserved in `expected_output/reference_run/` for audit.
