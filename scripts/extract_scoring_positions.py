#!/usr/bin/env python3
"""
Extract variant positions from a PGS Catalog scoring file and write
them to a BED file usable with bcftools.

Reads the harmonized columns (hm_chr, hm_pos) so the output matches
the target genome build (GRCh38 for hmPOS_GRCh38 files).

Usage:
    python extract_scoring_positions.py <scoring_file.txt.gz> <output.bed>
"""

import gzip
import sys
from pathlib import Path


# Values that indicate a missing/unmappable harmonized coordinate
MISSING_VALUES = {"", "NA", "."}


def extract_positions(scoring_file: Path, output_bed: Path) -> tuple[int, int]:
    """
    Read a PGS scoring file, write BED file.

    Returns:
        (variants_written, variants_skipped) tuple.
    """
    written = 0
    skipped = 0
    header_cols = None
    hm_build = None

    with gzip.open(scoring_file, "rt", encoding="utf-8") as f_in, open(output_bed, "w") as f_out:
        for lineno, line in enumerate(f_in, 1):
            line = line.rstrip("\n")

            # Metadata header lines: capture build info if present
            if line.startswith("#"):
                if line.startswith("#HmPOS_build="):
                    hm_build = line.split("=", 1)[1].strip()
                continue

            cols = line.split("\t")

            # First non-# line is the column header row
            if header_cols is None:
                header_cols = cols
                if hm_build is None:
                    raise ValueError(
                        "Missing #HmPOS_build metadata header. "
                        "Use a PGS Catalog harmonized scoring file."
                    )
                if hm_build != "GRCh38":
                    raise ValueError(
                        f"Expected harmonized build GRCh38, got: {hm_build!r}. "
                        f"Use a hmPOS_GRCh38 scoring file."
                    )
                try:
                    hm_chr_idx = header_cols.index("hm_chr")
                    hm_pos_idx = header_cols.index("hm_pos")
                except ValueError:
                    raise ValueError(
                        f"Required columns hm_chr and hm_pos not found in header: {header_cols}"
                    )
                continue

            # Data row: extract chromosome and position
            try:
                chrom = cols[hm_chr_idx]
                pos_raw = cols[hm_pos_idx]
            except IndexError as e:
                raise ValueError(f"Malformed row at line {lineno}: {line!r}") from e

            # Skip rows where harmonization failed
            if chrom in MISSING_VALUES or pos_raw in MISSING_VALUES:
                skipped += 1
                continue

            try:
                pos = int(pos_raw)
            except ValueError as e:
                raise ValueError(
                    f"Non-integer position at line {lineno}: {pos_raw!r}"
                ) from e

            # BED is 0-based, half-open: start = pos - 1, end = pos
            f_out.write(f"{chrom}\t{pos - 1}\t{pos}\n")
            written += 1

    return written, skipped


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(f"Usage: {sys.argv[0]} <scoring_file.txt.gz> <output.bed>")

    scoring_file = Path(sys.argv[1])
    output_bed = Path(sys.argv[2])

    if not scoring_file.exists():
        sys.exit(f"Scoring file not found: {scoring_file}")

    try:
        written, skipped = extract_positions(scoring_file, output_bed)
    except ValueError as e:
        sys.exit(f"Error: {e}")

    print(f"Wrote {written} variants to {output_bed}")
    if skipped > 0:
        print(f"Skipped {skipped} rows with missing harmonized coordinates")


if __name__ == "__main__":
    main()