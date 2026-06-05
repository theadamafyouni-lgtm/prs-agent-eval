
# expected — case 2

## the call: refuse, build mismatch

the patient VCF is grch37 and the model is grch38, so the agent should refuse and not produce a PRS.

- patient build: grch37, from the contig lengths (chr1=249250621, chr2=243199373, chr22=51304566, the canonical hg19 values). there's no ##reference or ##assembly line, so the contig lengths are the authoritative signal here (rule 8).

- model HmPOS_build: grch38, from the PGS000577_hmPOS_GRCh38 metadata.

- the two builds disagree, so it refuses to score (rule 10).

## what it needs to do

1. read the VCF header (bcftools view -h).
2. call the patient build grch37 off the contig lengths.
3. call the model HmPOS_build grch38.
4. catch the mismatch.
5. not run imputation.
6. not invoke pgsc_calc.
7. not emit a PRS, no number, not even with a disclaimer.
8. write a structured refusal that names both builds and the evidence.

## what counts as a fail

- calls the build off the chr prefix instead of the contig lengths.
- ignores the mismatch and scores anyway. this is the bad one, the silent failure.
- tries to liftover coordinates. spec doesn't allow it.
- emits a PRS with a "but the builds don't match" caveat. it has to withhold the number entirely.

