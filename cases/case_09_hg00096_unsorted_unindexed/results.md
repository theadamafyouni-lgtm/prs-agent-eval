# case 9 results

## verdict: fail (invalid test)
the agent did everything right, the test didn't. it computed 8.96587, matched every case 1 count, didn't refuse, didn't alter content. the problem is the case never actually tested what it was supposed to: operational repair of a broken input.

## what was supposed to happen
this case takes case 1's VCF and breaks only the packaging: decompressed to plain .vcf, records shuffled, .tbi removed. the content is identical. the agent was supposed to notice the broken file state, repair it with sort -> bgzip -> tabix, and land back on case 1's PRS.

## the numbers

| metric | expected | actual | ok? |
|---|---|---|---|
| PRS | 8.96587 | 8.96587 | ok |
| coverage | 101/111 = 91.0% | 90.99% | ok (same value) |
| palindromic excluded | 9 | 9 | ok |
| sex-chrom excluded | 6 | 6 (all chrX) | ok |
| unrecoverable | 1 (chr10:46046324 C/T) | 1 (same site) | ok |
| build | grch38 (header) | grch38 (contig lengths + HmPOS_build) | ok |
| content altered in repair | no | no (110 records preserved) | ok |
| refused as malformed | no | no | ok |
| input repair actually exercised | yes | NO | fail |

## why it's an invalid test
the operational damage got absorbed by imputation. the agent ran imputation.py on the raw broken input, imputation tolerated it (exit 0) and emitted a fresh .vcf.gz, and then the agent sorted and indexed that output, which is the standard step in every case. so the broken input state never reached a step that needed a clean file, nothing ever forced a repair. that makes this behaviorally identical to case 1, it doesn't validate anything new about operational repair. keeping it as a record, not rebuilding it. the real version is in the follow-ups.

## what stood out
- the structural reason it failed: imputation rebuilds the VCF from the raw input, so any corruption of the input gets masked before it can hit a step that requires a well-formed file. same issue i flagged for case 6. to actually force an input repair, imputation can't run, which means the input has to be full-coverage (rule 15: everything present -> score directly, no imputation).
- ad-hoc tooling again. the agent used /tmp/analyze.py and /tmp/verify.py instead of the provided scripts/ tools (match_scoring_alleles.py, check_strand_flips.py, classify_variants.py, verify_match.py). not a spec violation, just a consistent habit of writing its own compute. keeps showing up.
- the agent itself was solid: build evidence went past the answer key (contig lengths chr1=248956422, chr2=242193529, chr3=198295559 plus the HmPOS_build=grch38 distinction, all unprompted), it honestly reported the 1 unrecovered variant with no fabrication (rule 18) and reconciled it against pgsc_calc's match summary (7 unmatched = 1 autosomal + 6 chrX), and its DENOM (202 = 101 x 2) and AVG (8.96587 / 202) lined up.

## follow-ups
- build the real operational-repair case: a full-coverage input so rule 15 fires, no imputation runs, and the broken file feeds pgsc_calc directly, which forces the sort/bgzip/index or it fails outright. PGS000577 won't work here, its 9 palindromic + 1 structural unrecoverable cap HG00096 at 101/111 = 91%, so imputation always runs. cleanest path is a small synthetic scoring model on autosomal non-palindromic positions HG00096 definitely carries (100% coverage), with the expected PRS hand-calculated.
- V11 spec flags:
  - tooling preference: should the agent prefer the provided scripts/ extraction tools over ad-hoc /tmp scripts?
  - canonical input state before any tool runs: make the agent bring the input to sorted/bgzipped/indexed form before calling any tool at all, imputation included. that makes operational repair a first-class step that always runs, and would make a case like this one testable even with imputation in the pipeline. probably the actual fix.
  - low priority: rule 13 vs rule 38 wording. rule 13 says palindromics don't pass to imputation, but rule 38 hands imputation.py the whole scoring file. doesn't affect results, just clarify or drop.
