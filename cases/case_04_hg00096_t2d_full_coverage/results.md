# case_04 — Results

## Scenario
HG00096 WGS pre-filtered to PGS000330 positions; agent runs end-to-end PRS on a large multi-million-variant scoring model.

## Inputs
- `input/HG00096_PGS000330.vcf.gz` — HG00096's joint-callset records at PGS000330 positions. Built via `build_fixture.py`.

## Expected vs Actual

| Metric              | Expected      | Agent Output | Match |
|---------------------|---------------|--------------|-------|
| PRS SUM             | -0.338387     | -0.338387    | ✓     |
| DENOM               | 12,793,706    | 12,793,706   | ✓     |
| Matched variants    | 6,396,853     | 6,396,853    | ✓     |
| Direct match        | 6,390,268     | 6,390,268    | ✓     |
| Strand-flipped      | 6,585         | 6,585        | ✓     |
| Total unmatched     | 40,527        | 40,527       | ✓     |
| Match rate          | 99.37%        | 99.37%       | ✓     |
| Build identified    | GRCh38        | GRCh38       | ✓     |
| pgsc_calc invoked correctly | yes  | yes          | ✓     |

## Timing
- Reference run (pgsc_calc end-to-end): 31m 55s (1.1 CPU hours, 9 processes)
- Agent run, end-to-end active compute: ~40–45 min
  - pgsc_calc portion: ~33 min (21:49:35 → 22:22:39)
    - FORMAT_SCOREFILES: 17m 30s
    - MATCH_COMBINE: 11m 16s
    - MATCH_VARIANTS: 1m 40s
    - PLINK2_VCF (make compatible): 1m 8s
    - scoring + aggregate + report: ~1m 7s combined
  - imputation.py: a few minutes
  - Agent enumeration / coverage analysis: minutes before scoring
- Heavy lifting was almost entirely pgsc_calc; rest of elapsed time was waiting on background jobs.

## Verdict
**PASS.** All numeric metrics match the reference exactly. Agent's reasoning was rigorous: explicitly identified GRCh38 from contig lengths after noting absence of ##reference/##assembly, distinguished HmPOS_build vs genome_build, and independently enumerated unmatched variants (40,348 autosomal + 179 unmapped/alt-contig = 40,527) — matching pgsc_calc exactly.

## Notable Observations

- **Imputation step was invoked** despite expected_output.md predicting it wouldn't be. This is the agent correctly interpreting coverage as allele-match (per Cong's concern #3 — only matched REF/ALT count toward scoring), not position-only. From the agent's view, 40,348 variants were "missing" because their REF/ALT didn't reconcile with PGS, and these were routed through imputation. The script ran cleanly (exit 0, recovered 0 of 39,318), didn't affect the final PRS, and added minor wasted compute. **expected_output.md should be updated** — the "no imputation invoked" prediction was based on a position-only coverage assumption that doesn't match how the agent (correctly) operates. This is also V11 item #4 in action.

- **Build identification reasoning was unprompted and rigorous.** Agent did the same explicit-authority-order reasoning case_02 was designed to test — without external prompting. The spec's authority order is being internalized.

- **Independent enumeration matched pgsc_calc exactly.** Agent computed 40,348 autosomal-missing + 179 unmapped/alt-contig = 40,527. Same as pgsc_calc's unmatched count. Strong cross-check that the agent's classification logic was correct.

- **Total variant count off by 1.** Agent reported 6,437,380 total; PGS000330 has 6,437,381. Same rounding artifact noted in earlier sessions. Doesn't affect correctness.

- **Imputation reported 39,318 unrecovered**, differs from pgsc_calc's 40,348 autosomal-unmatched. Likely different counting categories (imputation may not include allele-mismatch in its "unrecovered" set). Worth understanding before case_06 (low-coverage refusal) where imputation logic matters more.

- **Cong's concerns verified.** (3) DENOM = 2 × 6,396,853 matched, not 2 × all variants. (4) Imputation didn't fabricate — script honestly reported unrecovered count rather than guessing.

## Follow-up
- Update `expected_output.md` to reflect that imputation IS expected to be invoked (the agent counts allele-match coverage, so missing/mismatched variants will always trigger imputation under current spec).
- Track the imputation-vs-pgsc_calc count discrepancy (39,318 vs 40,348) before case_06.
