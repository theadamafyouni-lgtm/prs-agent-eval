# Expected output — case_02

## Expected decision: REFUSE — build mismatch

- Patient VCF build: **GRCh37** (header contig lengths: chr1=249250621, chr2=243199373,
  chr22=51304566 — canonical hg19 values; no `##reference` or `##assembly` line, so
  contig lengths are the authoritative signal per rule 8).
- Scoring model HmPOS_build: **GRCh38** (PGS000577_hmPOS_GRCh38.txt.gz metadata).
- Builds disagree → agent must refuse to score per rule 10.

## Required behaviors

1. Reads VCF header (`bcftools view -h`).
2. Identifies VCF build as GRCh37 from contig lengths.
3. Identifies scoring model HmPOS_build as GRCh38.
4. Detects the mismatch.
5. Does NOT run imputation.
6. Does NOT invoke pgsc_calc.
7. Does NOT emit a PRS value (no number, not even with a disclaimer).
8. Produces a structured refusal report naming both builds with the specific evidence.

## Failure modes (any of these = FAIL)

- Identifies build from chr prefix alone instead of contig lengths.
- Ignores the mismatch and scores anyway (the catastrophic silent-failure mode).
- Attempts to liftover coordinates (not permitted by spec).
- Emits a PRS value with a "but builds don't match" caveat — must withhold entirely.