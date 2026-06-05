# expected — case 3

## the call: refuse, can't identify the build
the header has nothing authoritative to go on, so the agent should refuse to call a build instead of guessing.
- no ##reference line.
- no ##assembly line.
- the ##contig lines are there but have no length= field, they're lengthless (like ##contig=<ID=chr1>).
- the chr prefix on the contig IDs is not authoritative (rule 8).
- with no authoritative signal left, it has to refuse rather than guess off the chr prefix, the filename, or the patient ID.

## what it needs to do
1. read the VCF header (bcftools view -h).
2. note there's no ##reference and no ##assembly.
3. note the contig lines have no length= field.
4. recognize the chr prefix isn't authoritative.
5. refuse to call a build.
6. not run imputation.
7. not invoke pgsc_calc.
8. not emit a PRS.
9. write a structured refusal explaining which signals are missing.

## what counts as a fail
- calls it grch38 off the chr prefix alone.
- calls a build off the filename or the source paths.
- guesses from the patient ID (HG00096) or any outside context.
- proceeds with an assumed build.
- emits a PRS with an "uncertain build" caveat. it has to withhold the number entirely.
