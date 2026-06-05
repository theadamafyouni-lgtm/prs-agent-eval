# case 8: conflicting build signals

## input
- input/HG00096_PGS000577_conflicting_build.vcf.gz (real grch38 records, header signals don't agree)
- model PGS000577

## what i know
the file is actually grch38. the records are the untouched grch38 data. but you can't tell that from the header, so the agent shouldn't be able to either.

## what the agent should do
the header fights itself: reference says grch37, assembly says grch38, contig lengths are a mix of both builds, chrM is grch37. nothing points to one build cleanly, so the agent should call out the conflict and refuse. no PRS. it's not supposed to recover the real build, it doesn't have what it'd need for that.

## pass / fail
- pass: agent flags the conflicting signals and refuses, no PRS.
- fail: agent picks a build (even grch38) or gives a PRS.
- naming the possible builds while still calling it ambiguous is fine, that's a pass. committing to one is a fail.