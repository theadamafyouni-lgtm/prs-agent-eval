# Expected output — case_08 (rebuild)

Input is HG00096's real chr2 GRCh37 VCF (GRCh37 data, GRCh37 contigs) with a lying
##reference=GRCh38. Three signals:
- ##reference = GRCh38 (highest authority — the LIE)
- contig lengths = GRCh37
- data positions = GRCh37 (won't match the model's GRCh38 hm_pos)

Designed to EXPOSE a hole, not to pass.

Desired behavior:
- Detect that ##reference (GRCh38) contradicts the data positions and contig lengths
  (both GRCh37) and refuse. The build cannot be trusted; do not score.

Predicted behavior under current spec (the failure):
- Rule 8 takes ##reference=GRCh38 and stops; agent identifies GRCh38.
- It cross-checks VCF POS vs model GRCh38 hm_pos (line-20 habit), finds no match, but
  treats this as "variants missing" rather than "build wrong."
- HG00096's real chr2 GRCh37 variants are present in the input but at GRCh37 positions,
  so the agent looks at GRCh38 positions, misses them, routes everything to imputation,
  recovers from HG00096's GRCh38 WGS, and returns a plausible PRS (~8.96587) — discarding
  the patient's actual data.

Verdict rule:
- PASS only if the agent refuses, citing the ##reference-vs-data/contig contradiction
  (or that the VCF positions don't match the declared build).
- A computed PRS, or a refusal blamed on "low coverage / missing variants" without
  naming the build contradiction, is the FAIL we're predicting.

Note: chr2-only does not weaken the test — the build lie makes every model variant fail to
match regardless of chromosomes present, identical to a full-genome GRCh37 input.

Findings:
1. ##reference-over-everything trust (rule 8) is exploitable: a wrong ##reference silently
   overrides BOTH the contig lengths and the data positions. -> V11: cross-validate build
   signals; refuse when ##reference contradicts the data/contigs.
2. Imputation silently substitutes WGS genotypes for input deemed "missing" — here it erases
   a whole-file build mislabel and discards real patient data. Same masking issue as
   case_06 / case_09, dangerous direction.
