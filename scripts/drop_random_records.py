#!/usr/bin/env python3
"""
Randomly drop a fraction of variant records from a VCF.

Reads a (bgzipped or plain) VCF, preserves all header lines, and
keeps each variant record with probability (1 - fraction). Writes
uncompressed VCF; bgzip and index it afterward.

Reproducible: uses a configurable random seed so re-running with the
same seed produces the same output.

Usage:
    python drop_random_records.py [--fraction F] [--seed N] <input.vcf[.gz]> <output.vcf>
"""

import argparse
import gzip
import random
import sys
from pathlib import Path


def drop_random_records(
    input_vcf: Path,
    output_vcf: Path,
    fraction: float,
    seed: int,
) -> tuple[int, int]:
    """
    Read VCF, randomly drop a fraction of variant records,
    write the rest (plus all headers) to output as uncompressed VCF.

    Returns:
        (kept, dropped) tuple.
    """
    if not 0.0 <= fraction <= 1.0:
        raise ValueError(f"fraction must be between 0 and 1, got {fraction}")

    # Handle both .vcf and .vcf.gz inputs transparently
    open_input = gzip.open if input_vcf.suffix == ".gz" else open

    rng = random.Random(seed)
    kept = 0
    dropped = 0

    with open_input(input_vcf, "rt", encoding="utf-8") as f_in, \
         open(output_vcf, "w", encoding="utf-8") as f_out:
        for line in f_in:
            if line.startswith("#"):
                f_out.write(line)
            elif rng.random() >= fraction:
                f_out.write(line)
                kept += 1
            else:
                dropped += 1

    return kept, dropped


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Randomly drop a fraction of variant records from a VCF."
    )
    parser.add_argument("input_vcf", type=Path, help="Input VCF (.vcf or .vcf.gz)")
    parser.add_argument("output_vcf", type=Path, help="Output VCF (uncompressed)")
    parser.add_argument(
        "--fraction",
        type=float,
        default=0.30,
        help="Fraction of variant records to drop (default: 0.30)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    args = parser.parse_args()

    if not args.input_vcf.exists():
        sys.exit(f"Input VCF not found: {args.input_vcf.resolve()}")

    try:
        kept, dropped = drop_random_records(
            args.input_vcf, args.output_vcf, args.fraction, args.seed
        )
    except ValueError as e:
        sys.exit(f"Error: {e}")

    total = kept + dropped
    print(f"Input records: {total}")
    print(f"Kept:    {kept} ({100 * kept / total:.1f}%)")
    print(f"Dropped: {dropped} ({100 * dropped / total:.1f}%)")
    print(f"Wrote: {args.output_vcf}")


if __name__ == "__main__":
    main()