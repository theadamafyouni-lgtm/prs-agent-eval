# case 1 results

## verdict: pass (2026-05-28)
ran the agent end to end off the command.txt prompt and it hit every mark. this is the run that locks in 8.96587 for the 101-variant set.

## what happened
this case feeds HG00096 (grch38) against PGS000577 with 37 of the 101 matchable autosomal variants pulled out, so the agent has to identify the build, drop the sex chromosomes, impute the missing autosomal variants back, gate on coverage, and score. it did all of it.
- build: grch38 off the contig lengths.
- dropped the 6 chrX variants and didn't count them toward coverage.
- found the missing autosomal variants and imputed them back.
- the one variant that genuinely can't be recovered (chr10:46046324, C/T, no record in the WGS) it reported as unrecovered and did not fabricate a genotype, which is the rule 18 behavior i wanted.
- excluded the 9 palindromic variants from the matched count, kept them in the denominator.
- matched 101 of 111 autosomal required, coverage 91%, over the 90% line, so it scored.
- PRS came back 8.96587, matches.

## the part i was watching
the coverage gate. it gated on the autosomal number (101/111 = 91%), not on pgsc_calc's own 101/117 = 86.32% figure, which would have wrongly tripped a refusal. sex chromosomes stayed out of the denominator, exactly how i want it handled.

## one thing to flag
the structured tables were all correct, but the arithmetic in its written-out prose summary was off. so the data is right, the narration isn't always. worth keeping in mind since the prose is what a person reads first.
