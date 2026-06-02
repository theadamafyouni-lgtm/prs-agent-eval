# check_strand_flips.py

Detects and corrects strand flips in a VCF against a PGS scoring model. Keeps records that already match, complements REF/ALT for records whose partner-swapped alleles match, drops anything that matches neither.

## Usage

```bash
python3 check_strand_flips.py input.vcf[.gz] scoring.txt.gz out.vcf
```

## Inputs

- Input VCF (`.vcf` or `.vcf.gz`)
- Scoring file (`.txt.gz`)
- Output path (uncompressed `.vcf` — bgzip + tabix afterward)

## Outputs

- A VCF where every kept record's alleles are on the same strand as the scoring file

## What it prints

- Exact match count (alleles already matched)
- Strand flip corrected count (alleles matched after partner-swap; REF/ALT have been complemented)
- Dropped (no match either way — different variant or error)
- Output path

## Notes

- Partner letters: A↔T, C↔G
- A correction only changes REF and ALT — the GT field is **not** touched. The indices (`0`, `1`) still point to the same physical alleles, just relabeled with their partner letters.
- Palindromic variants (A/T, C/G) whose alleles already match fall into "exact" — a hidden strand flip can't be detected from alleles alone, and same-strand provenance is assumed
- Built for SNPs — indels won't survive the single-base partner swap and land in "dropped"
- Records at positions not in the scoring file pass through unchanged
- Output is uncompressed; bgzip + tabix-index as separate steps if needed downstream
- Also the construction tool for Case C: take a clean VCF and deliberately complement non-ambiguous variants to build a strand-flip test input