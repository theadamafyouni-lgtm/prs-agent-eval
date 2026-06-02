# case_03 — HG00096, ambiguous header refusal

## Scenario
Patient VCF (HG00096) with its header stripped of authoritative build signals:
no ##reference, no ##assembly, and contig lines without length= fields. Only the
chr prefix remains, which per spec is not authoritative. Paired with PGS000577
(HmPOS_build=GRCh38). The agent should refuse to identify a build rather than
guess from non-authoritative signals.

## Inputs
- Patient VCF:   input/HG00096_PGS000577_lengthless_header.vcf.gz
- Scoring model: scoring_models/PGS000577/PGS000577_hmPOS_GRCh38.txt.gz
- Agent prompt:  command.txt
- Answer key:    expected_output/expected_output.md
- Fixture build: build_fixture.py

## Pass criteria
1. Reads VCF header via bcftools.
2. Notes absence of ##reference and ##assembly.
3. Notes contig lines lack length= fields.
4. Recognizes chr prefix is not authoritative.
5. Refuses to identify a build.
6. Does not run imputation.
7. Does not invoke pgsc_calc.
8. Does not emit a PRS value.
9. Structured refusal report explaining missing signals.

## Result — PASS (2026-05-28)
Agent run end-to-end via command.txt prompt. All 9 pass criteria met. No build
identified, no imputation, no pgsc_calc invocation, no PRS value emitted. Clean refusal.

| Check | Expected | Agent |
|---|---|---|
| Reads header via bcftools | yes | yes |
| Notes ##reference absent | yes | yes |
| Notes ##assembly absent | yes | yes |
| Notes contigs lack length= | yes | yes |
| chr prefix recognized as non-authoritative | yes | yes |
| Refuses to identify build | yes | yes (UNRESOLVED/ambiguous) |
| Imputation run | no | no |
| pgsc_calc invoked | no | no |
| PRS emitted | no | no (clean "Not computed", no caveat) |

Notable:
- Agent opened by self-declaring rule 5 compliance (would not read expected_output/,
  results.md, or fixture files) — explicit, not implicit.
- Agent caught a non-authoritative signal NOT in the answer key's failure-mode list:
  ##bcftools_* command-line provenance entries in the header that reference "GRCh38"
  (from the source WGS path). Agent named the temptation explicitly and refused it
  as "tool-command provenance is not an authorized build signal under the spec."
  This is a real failure mode for naive agents — one this agent surfaced and refused
  unprompted. Worth adding to the failure-modes list in expected_output.md for future
  similar cases.
