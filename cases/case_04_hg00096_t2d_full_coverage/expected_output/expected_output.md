# expected — case 4

## scenario
HG00096 WGS pre-filtered down to the PGS000330 positions. the agent should run a full end-to-end PRS on this big multi-million-variant model.

## what it should do
1. call the build grch38 from the header (contig lengths).
2. match against PGS000330_hmPOS_GRCh38 (HmPOS_build=grch38). builds agree, so proceed.
3. work out coverage from the input. it's full position coverage, so no imputation needed.
4. run pgsc_calc with --target_build GRCh38 and --pgs_id PGS000330.
5. report the PRS SUM and matched-variant count from the pgsc_calc output.

## the numbers it should land on
- PRS SUM: -0.338387
- DENOM: 12,793,706 (2 × matched variants)
- matched variants: 6,396,853
  - direct exact match: 6,390,268 (99.27%)
  - matched via strand flip: 6,585 (0.10%)
- unmatched: 40,527 (0.63%)
- match rate against PGS000330: 99.37%

## what counts as a pass
- returns PRS SUM = -0.338387 (or the same within float precision).
- reports matched variant count = 6,396,853.
- doesn't fabricate the 40,527 unmatched, reports them honestly as excluded.
- no imputation step (input is already complete at the PGS positions).

## reference run
an independent pgsc_calc run on the same input is kept in expected_output/reference_run/ for audit.
