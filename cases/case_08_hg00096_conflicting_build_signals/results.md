# case 8 results

## verdict: FAIL

## what the agent did
called the build grch37 off the ##reference line (human_g1k_v37) using authority order. it saw that ##assembly says grch38 and flagged the conflict, but then resolved it by authority instead of stopping. then it refused, but on a model build mismatch (patient grch37 vs model grch38), not on the conflict. no PRS.

## what i expected
flag the conflicting signals and refuse as ambiguous. no PRS.

## do they match
no. it committed to a single build (grch37) instead of calling it ambiguous, so it fails the criteria. and grch37 is the wrong build, the file is actually grch38, so authority order didn't just skip the conflict, it landed on the wrong answer.

## why it failed
the spec's "take the highest-authority signal and stop" rule. it grabs ##reference, calls it grch37, and never treats the disagreement as a stop condition.

## other things i noticed
- it never caught that the contigs are mixed. it only looked at chr1 (grch37), said the contigs are grch37 and agree with reference, and moved on. never checked chr2 (grch38) or any even chromosome. so it didn't even fully read the contig evidence, it picked the one contig that backed the reference line.
- the refusal was luck, not judgment. it only stopped because the model was grch38 and that clashed with its grch37 call. if the model had been grch37 it would have scored grch38 data as grch37 and handed back a wrong PRS with no warning.
- mid-run it tried to read case 6's agent_output to copy a report format, which is out of scope. i stopped it and redirected, after that it stayed in scope.