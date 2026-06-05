# case 7 results

## verdict: fail (for now)
baseline fail, and i expected it. i set this case up to pass by having the agent drop the bad rows, impute them back from the WGS, and return 8.96587 like case 1. but i never wrote the rule that tells it to do that, it's parked for v11, so there was no way for it to pass this run. it failed because the rule isn't written, not because the agent did anything wrong.

## what the agent did
the part i actually cared about, catching the garbage, it got completely right.
- it figured out the build was grch38 from the contig lengths (this file has no reference or assembly line).
- it found all 20 rows i corrupted, didn't miss one.
- it named the bad bases i used (B, J, L, S) and even pointed out that B and S are IUPAC codes you can't put in REF, while J and L aren't real bases at all.
- it noticed the variant ID still had the original allele in it (like 2:10570604:C:T) and used that to prove the REF had been messed with.

so it clearly realized the file had junk in it, which is the whole reason this case exists.

then it stopped. it decided the file was malformed and refused, no PRS. its reasoning was that these aren't missing variants so they don't get imputed, and a malformed file means stop.

## what i expected
i wanted it to drop those 20 rows, treat them as missing, impute them, and score, landing back on 8.96587. so an actual PRS, not a refusal.

## why it didn't match
nothing in the spec tells it an invalid allele should be dropped and imputed, so when it hit my junk alleles its only move was to call the file corrupt and stop, which is fair given what it has. once i write the invalid-allele rule this turns into a pass. the detection was already perfect, it's just the recovery that isn't wired up yet.
