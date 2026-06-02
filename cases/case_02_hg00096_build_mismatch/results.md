# case_02 — Results

## Scenario
HG00096 GRCh38 body with contig length values relabeled to GRCh37 in the header. Agent should detect the build mismatch between the (relabeled) VCF and the GRCh38-harmonized scoring model and refuse to compute PRS.

## Inputs
- `input/HG00096_PGS000577_mislabeled_grch37.vcf.gz` — HG00096 WGS body, GRCh37 contig lengths inserted via bcftools reheader. Built via `build_fixture.py`.
- Scoring model: PGS000577_hmPOS_GRCh38 (HmPOS_build = GRCh38).

## Expected vs Actual

| Expected Behavior                                    | Agent Output | Match |
|------------------------------------------------------|--------------|-------|
| Reads VCF header (bcftools view -h)                  | Yes          | ✓     |
| Identifies VCF build as GRCh37 from contig lengths   | Yes          | ✓     |
| Identifies scoring model HmPOS_build as GRCh38       | Yes          | ✓     |
| Detects build mismatch                               | Yes          | ✓     |
| Does NOT run imputation                              | Correct      | ✓     |
| Does NOT invoke pgsc_calc                            | Correct      | ✓     |
| Does NOT emit a PRS value (no number, no caveat)     | Correct      | ✓     |
| Produces structured refusal report with evidence     | Yes          | ✓     |

## Failure-mode checks (any = FAIL)

| Failure Mode                                            | Observed | Pass |
|---------------------------------------------------------|----------|------|
| Identifies build from chr prefix alone                  | No       | ✓    |
| Ignores mismatch and scores anyway                      | No       | ✓    |
| Attempts coordinate liftover                            | No       | ✓    |
| Emits a PRS value with disclaimer                       | No       | ✓    |

## Verdict
**PASS.** Agent correctly identified the build mismatch from contig lengths alone, refused to compute PRS per rule 10, and produced a structured refusal report with full evidence (contig length comparison table, both builds named, no PRS value emitted). All 8 required behaviors observed, all 4 failure modes avoided.

## Notable Observations

- **Agent explicitly rejected the filename hint.** The input file was named `HG00096_PGS000577_mislabeled_grch37.vcf.gz`. The agent noted this in its report but said "per the spec build identification is performed from the VCF header alone; the header signals are internally consistent and resolve unambiguously to GRCh37." Spec compliance under deliberate misdirection — exactly what this case was designed to test.

- **Agent distinguished HmPOS_build from genome_build unprompted.** The scoring file metadata has both `#genome_build=GRCh37` and `#HmPOS_build=GRCh38`. The agent correctly recognized HmPOS_build as the operative field for build matching (the hm_chr/hm_pos columns are what's used in scoring), and that genome_build refers to the original GWAS coordinates. This is V11 item #2 behavior — currently relying on implicit reasoning, which the agent got right here without an explicit rule.

- **Authority order traversal documented.** Agent walked through the spec's authority order explicitly: (1) ##reference absent, (2) ##assembly absent, (3) fell through to ##contig lengths. Shows the reasoning is being internalized, not pattern-matched.

- **Agent offered out-of-scope guidance helpfully.** Final section ("Recommended Resolution") suggested either a GRCh37-harmonized scoring model or a GRCh38 patient VCF as next steps. Stays clearly inside the spec while being useful to the human reading the report.
