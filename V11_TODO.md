# v11 spec — to add / clarify

Open items from V7-V10. Each: what's needed, why, where it goes.

## 1. model selection by ancestry (next week's main work)
Multiple models per trait (T2D: PGS000014/000330/002243). Agent needs: how to read each model's ancestry from PGS Catalog metadata, how patient ancestry is supplied (likely an ancestry.json next to the VCF, e.g. {"population":"EUR"}), how to pick when more than one matches.
Where: new phase, or extend phase 3.

## 2. HmPOS_build vs genome_build
Scoring files carry both. genome_build = original GWAS build; HmPOS_build = harmonized operative build, and that's the one that must match the VCF. Agent gets it right by inference now (case 2); make it an explicit rule.
Where: phase 3, rule 10.

## 3. coverage denominator
Denominator = the theoretically scoreable subset of the model. Exclude unmapped (empty hm_chr), alt/random contigs, sex chromosomes, palindromic (pending #5). Numerator = matched in patient (direct or strand-resolved). Don't penalize the agent for unmappable variants. Affects case 1's pass criteria.
Where: phase 6, rule 32.

## 4. imputation skip threshold
Don't call imputation when coverage is already high (it finds nothing, especially when the input came from the WGS). Rule: matched coverage ≥ 95%, imputation optional.
Where: phase 4, rules 11-22.

## 5. palindromic filtering applicability
We filter palindromic (A/T, G/C) for strand ambiguity. Decide: when VCF and model share a build, does strand ambiguity even arise, and when (if ever) do we skip the filter?
Where: phase 4.

## 6. invalid allele handling (needed before case 7 passes)
REF/ALT with non-ACGT chars (IUPAC codes, dots, etc.): drop the row, treat the position as missing, route through imputation, same path as missing. >25% invalid = malformed, refuse; below that, recover.
Run finding (case 7): the agent's default is invalid → malformed → stop the whole file (it cited the malformed-input and unrecoverable rules to justify it). So the rule has to explicitly say invalid = drop + impute and that this overrides malformed-stop, or it keeps refusing.
Where: phase 4.

## 7. trust posture toward internal tools
Stop re-verifying our own scripts/ output after a clean exit. Internal tools (scripts/, exit codes meaningful) → trust on clean exit. External tools (bcftools, pgsc_calc) → verify.
Where: new "tool usage" section.

## 8. canonical input before tool calls
Sort + bgzip + tabix the input before calling any tool, not after. Case 9 handed a raw unsorted file; imputation tolerated it and the agent only fixed the output, so the operational-repair test never fired. Making canonicalization a required first step makes that behavior always observable. Content-preserving only.
Where: phase 4, before rule 16 (or near rule 19).

## 9. provided tools vs ad-hoc compute
Case 9: the agent wrote its own /tmp scripts for enumeration, palindromic flagging, strand matching, coverage, and verification instead of the provided scripts/ tools. Not a violation but consistent. Decide: prefer a provided tool when one fits, ad-hoc only as fallback? Or is ad-hoc fine if the reasoning is sound? Touches the core methodology (agent judges, tools extract).
Where: same "tool usage" section as #7.

## 10. rule 13 vs 38 wording (low priority)
Rule 13 says palindromic don't pass to imputation, but rule 38 passes the whole scoring file, so they enter anyway. Harmless (coverage excludes them). Clarify rule 13 to mean "don't track palindromic in the agent's own missing-set," not "build a filtered file."
Where: phase 4, rule 13 (cross-ref 38).

## 11. build identification — authority order is broken (needed before case 8 passes)
"Take the highest-authority signal and stop" makes the agent commit to one build and ignore contradicting signals. Case 8: reference said GRCh37, assembly said GRCh38, contigs were mixed; the agent took reference, called it GRCh37 (wrong, the file is GRCh38), and never treated the disagreement as a stop. It also only checked chr1 and generalized, never noticing the contigs are internally mixed.
Rule needs: when present signals disagree on the build (metadata vs contigs, or contigs vs each other), don't resolve by authority, call it ambiguous and refuse. And check multiple contigs, not just chr1.
Open: how strong is "sure enough" to commit, and whether to add coordinate/FASTA verification (external-truth path) — bigger change, run past Cong.
Where: phase 2 (build identification).