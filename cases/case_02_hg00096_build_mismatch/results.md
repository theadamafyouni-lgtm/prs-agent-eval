# case 2 results

## verdict: pass

the agent caught the build mismatch and refused, which is the whole point of this case. all 8 required behaviors showed up and none of the 4 failure modes did.

## what happened

this case takes a real grch38 HG00096 body and relabels the contig lengths to grch37 in the header (via bcftools reheader), so the patient file reads as grch37 while the model is grch38-harmonized. the agent read the header, called the patient build grch37 off the contig lengths, called the model HmPOS_build grch38, saw they disagree, and refused per rule 10. no imputation, no pgsc_calc, no PRS, and it wrote a structured refusal naming both builds with the contig-length evidence.

the failure modes i was watching for all stayed away. it didn't call the build off the chr prefix, didn't try a liftover, didn't quietly score anyway, and didn't emit a PRS dressed up with a "builds don't match" caveat. the quiet-scoring one is the silent failure i care about most, and it withheld the number entirely.

## what stood out

- it ignored the filename on purpose. the input is literally named ..._mislabeled_grch37.vcf.gz, and it noted the hint but said build ID comes from the header alone and the header resolves cleanly to grch37. that's exactly the misdirection this case was built to test, and it held to the spec instead of taking the bait.

- it split HmPOS_build from genome_build without being told to. the scoring file has genome_build=grch37 and HmPOS_build=grch38, and it correctly used HmPOS_build as the one that matters for matching (the hm_chr/hm_pos columns are what scoring actually uses) and treated genome_build as the original GWAS coordinates. that's the V11 item 2 behavior, and it got it right on implicit reasoning with no explicit rule for it yet.

- it walked the authority order out loud: ##reference absent, ##assembly absent, fall through to contig lengths. reads like the reasoning is actually internalized, not pattern-matched.

- it ended with a recommended-resolution section suggesting either a grch37 model or a grch38 patient file. technically beyond the ask, but stays inside the spec and is useful to whoever reads the report.

