# extract_scoring_positions.py

Pulls the variant positions out of a PGS Catalog harmonized scoring file and writes them to a BED file that bcftools can use to subset a VCF.

## Usage

```bash
python3 extract_scoring_positions.py scoring.txt.gz output.bed
```

## Inputs

- A harmonized PGS Catalog scoring file (`*hmPOS_GRCh38.txt.gz`)
- An output path for the BED file

## Outputs

- A BED file: one row per scoring variant with valid GRCh38 coordinates
- BED format is `chrom\tstart\tend` (0-based, half-open: `start = pos - 1`, `end = pos`)

## What it prints

- Number of variants written
- Number skipped (rows with no valid GRCh38 coordinate)

## Notes

- Uses the harmonized `hm_chr` and `hm_pos` columns — i.e. the GRCh38 coordinates, not the original GRCh37 ones
- Skips rows where `hm_chr` or `hm_pos` is `NA` (liftover failed for that variant)
- Validates the file is GRCh38 via the `#HmPOS_build` metadata header — fails loudly if you point it at the wrong build
- Chromosomes are written as bare numbers (`1`, not `chr1`) — add a `chr` prefix with `sed -i 's/^/chr/' output.bed` if your VCF uses one