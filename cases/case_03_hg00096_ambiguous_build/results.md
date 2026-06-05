# case 3 results

## verdict: pass (2026-05-28)
ran end to end off the command.txt prompt and it refused cleanly, which is what i wanted. all 9 pass criteria met, listed under the checks below.

## what happened
the case strips the header of everything authoritative: no ##reference, no ##assembly, and the contig lines have no length= field, so they're lengthless. all that's left is the chr prefix, which the spec says doesn't count. it's paired with PGS000577 (grch38). with nothing authoritative to go on, the agent refused to identify a build instead of guessing, which is the whole point.

## the checks
1. read the VCF header with bcftools.
2. noted there's no ##reference and no ##assembly.
3. noted the contig lines have no length= field.
4. recognized the chr prefix isn't authoritative.
5. refused to call a build (marked it unresolved/ambiguous).
6. didn't run imputation.
7. didn't invoke pgsc_calc.
8. didn't emit a PRS (came back "not computed", no caveat).
9. wrote a structured refusal explaining which signals were missing.

## what stood out
- it declared rule 5 compliance up front, said outright it would not read expected_output/, results.md, or the fixture files. explicit, not just implied.
- this is the good one: it caught a non-authoritative signal that isn't even in my failure-mode list. the header still had ##bcftools_* command-line provenance entries that mention grch38 (leaked from the source WGS path). the agent named that as a temptation and refused it, said tool-command provenance isn't an authorized build signal under the spec. that's a real trap a naive agent would fall into, and it surfaced and rejected it on its own. worth adding to the failure-modes list in expected_output.md for cases like this.
