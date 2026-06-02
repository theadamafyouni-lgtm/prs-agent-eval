# drop_random_records.py

Randomly drops a fraction of variant records from a VCF while keeping all header lines. Used to build corrupted test inputs from a clean source VCF.

## Usage

```bash
python3 drop_random_records.py [--fraction F] [--seed N] input.vcf[.gz] output.vcf
```

## Inputs

- Input VCF (`.vcf` or `.vcf.gz`)
- Output path (uncompressed `.vcf` — bgzip + tabix afterward)
- `--fraction` (optional): fraction of variant records to drop, default `0.30`
- `--seed` (optional): random seed for reproducibility, default `42`

## Outputs

- Uncompressed VCF with all header lines preserved and `(1 − fraction)` of the variant records

## What it prints

- Input record count
- Kept count + percentage
- Dropped count + percentage

## Notes

- Universal — works on any VCF, not specific to any one test case
- Deterministic given the seed: re-running with the same seed produces exactly the same corrupted file
- Header lines (`##` and `#CHROM`) are always preserved untouched
- Output is uncompressed; bgzip + tabix-index as separate steps afterward
- Each variant is dropped independently (Bernoulli), so the actual dropped fraction will be near the target but not exact