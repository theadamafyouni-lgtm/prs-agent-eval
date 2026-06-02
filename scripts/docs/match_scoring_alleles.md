# match_scoring_alleles.py

Filters a VCF to keep only records whose `{REF, ALT}` exactly matches a scoring file's `{effect_allele, other_allele}` at that position. Used to build a clean `source/` from a position-matched VCF by dropping multi-allelic splits that aren't what PGS is scoring.

## Usage

```bash
python3 match_scoring_alleles.py input.vcf[.gz] scoring.txt.gz out.vcf.gz
```

## Inputs

- Input VCF (`.vcf` or `.vcf.gz`)
- PGS Catalog scoring file (`.txt.gz`)
- Output path (`.vcf.gz`)

## Outputs

- A bgzipped + tabix-indexed VCF containing only records whose alleles exactly match the scoring file as a set

## What it prints

- Records kept (exact allele match)
- Records dropped (allele mismatch)
- Records dropped (position not in scoring file)

## Notes

- Set match — orientation is allowed: `{REF=A, ALT=G}` matches scoring `{effect=A, other=G}` *and* `{effect=G, other=A}`
- Does **not** handle strand flips — for those use `check_strand_flips.py`
- Drops the off-allele records at multi-allelic-split positions (e.g. if WGS has `A→G` and `A→T` both at one position and PGS scores `A/G`, only the `A→G` row survives)
- Assumes bi-allelic-split input (one ALT per row)
- Handles `.vcf` and `.vcf.gz` input; output is always bgzipped + indexed in one step