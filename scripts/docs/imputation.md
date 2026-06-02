# imputation.py

Recovers missing scoring variants in a corrupted VCF by pulling them from a WGS reference file. Exact-matches alleles and merges the recovered records back in. Never reads the ground-truth file — recovery happens blind, from the WGS only.

## Usage

```bash
python3 imputation.py corrupted.vcf[.gz] scoring.txt.gz wgs.vcf.gz out.vcf.gz
```

## Inputs

- Corrupted patient VCF (missing some scoring variants)
- Scoring file (`.txt.gz`) — defines what variants *should* be present
- WGS reference VCF (`.vcf.gz`, tabix-indexed) — source for the missing variants
- Output path (`.vcf.gz`)

## Outputs

- A bgzipped + tabix-indexed VCF combining the corrupted input + the recovered missing variants, sorted

## What it prints

- Scoring variants expected
- Present in input
- Missing (attempted impute)
- Recovered from WGS
- Could **not** recover, broken down by chromosome
- Final output record count

## Notes

- Uses `bcftools view -R --regions-overlap pos` for exact-position lookup against the WGS
- Pipes through `bcftools norm -m -any` to split any multi-allelic records before the exact-match filter — defensive even though our WGS is bi-allelic-split
- Recovered variants must exactly match scoring `{effect, other}` alleles as a set — never invents genotypes
- Reports unrecoverable variants transparently (e.g. chrX absent from the WGS shows up as "could not recover: {'X': 6}") rather than silently dropping them
- Does **not** modify existing genotypes — only adds recovered ones
- Never reads `source/` or any other ground-truth file — test integrity