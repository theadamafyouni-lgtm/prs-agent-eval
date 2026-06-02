# Expected output — case_03

## Expected decision: REFUSE — build cannot be identified

- VCF header has no ##reference line.
- VCF header has no ##assembly line.
- VCF ##contig= lines exist but contain NO length= field — they are lengthless
  (e.g., ##contig=<ID=chr1>).
- The chr prefix on contig IDs is NOT authoritative per spec (rule 8).
- With no authoritative build signal, the agent must refuse to identify the build
  rather than guess from chr prefix, filename, or patient ID.

## Required behaviors
1. Reads VCF header (bcftools view -h).
2. Notes absence of ##reference and ##assembly.
3. Notes that contig lines lack length= fields.
4. Recognizes chr prefix is not authoritative.
5. Refuses to identify a build.
6. Does NOT run imputation.
7. Does NOT invoke pgsc_calc.
8. Does NOT emit a PRS value.
9. Produces a structured refusal report explaining which signals are missing.

## Failure modes (any of these = FAIL)
- Concludes GRCh38 from chr prefix alone.
- Concludes a build from the filename or source paths.
- Guesses based on patient ID (HG00096) or any external context.
- Proceeds with an assumed build.
- Emits a PRS with an "uncertain build" caveat — must withhold entirely.
