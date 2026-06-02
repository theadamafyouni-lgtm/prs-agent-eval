#!/usr/bin/env python3
"""Classify every scoring variant for a patient: matched / ambiguous / no_match / no_record.

Explains exactly why each scoring variant is or isn't in the clean test patient,
broken down by reason and by chromosome. Useful for coverage decisions and case docs.

  matched    -> in the clean VCF (scored)
  ambiguous  -> palindromic A/T or C/G (dropped; strand unresolvable)
  no_match   -> WGS has a record here but alleles don't match the model
  no_record  -> no record in the WGS at all (hom-ref or no-call)

usage: classify_variants.py SCORING.txt.gz WGS.vcf[.gz] CLEAN.vcf.gz
"""
import subprocess, sys, tempfile
from collections import Counter
from pathlib import Path
import build_test_patient as b


def load_vcf_positions(path):
    recs = {}
    with b.open_any(path) as f:
        for line in f:
            if line.startswith("#"):
                continue
            c = line.rstrip("\n").split("\t")
            recs[(c[0].removeprefix("chr"), c[1])] = frozenset({c[3], c[4]})
    return recs


def classify(scoring, clean_positions, wgs_positions):
    """Pure classification — testable without bcftools."""
    rows = []
    for (ch, pos), pair in scoring.items():
        if (ch, pos) in clean_positions:
            reason = "matched"
        elif b.is_ambiguous(pair):
            reason = "ambiguous"
        elif (ch, pos) in wgs_positions:
            reason = "no_match"
        else:
            reason = "no_record"
        rows.append((ch, pos, "/".join(sorted(pair)), reason))
    return rows


def main():
    if len(sys.argv) != 4:
        sys.exit(f"usage: {sys.argv[0]} SCORING.txt.gz WGS.vcf[.gz] CLEAN.vcf.gz")
    scoring_file, wgs, clean_vcf = sys.argv[1:4]

    scoring, _ = b.load_scoring(scoring_file)
    clean = load_vcf_positions(clean_vcf)

    prefix = b.detect_wgs_prefix(wgs)
    with tempfile.NamedTemporaryFile("w", suffix=".bed", delete=False) as f:
        bed = f.name
    b.write_bed(scoring, prefix, bed)
    normed = b.extract_and_split(wgs, bed)
    Path(bed).unlink()
    wgs_positions = set()
    for line in normed.splitlines():
        if not line.startswith("#"):
            c = line.split("\t")
            wgs_positions.add((c[0].removeprefix("chr"), c[1]))

    rows = classify(scoring, clean, wgs_positions)

    reason_counts = Counter(r[3] for r in rows)
    chrom_by_reason = {}
    for ch, pos, alleles, reason in rows:
        chrom_by_reason.setdefault(reason, Counter())[ch] += 1

    print(f"total scoring variants: {len(scoring)}\n")
    for reason in ("matched", "ambiguous", "no_match", "no_record"):
        by_chrom = dict(sorted(chrom_by_reason.get(reason, {}).items(),
                               key=lambda kv: (kv[0].isdigit() is False, kv[0])))
        print(f"{reason:>10}: {reason_counts[reason]:3d}   by chrom: {by_chrom}")

    print("\nabsent variants (not in clean set):")
    for ch, pos, alleles, reason in sorted(rows, key=lambda r: (r[0].zfill(2), int(r[1]))):
        if reason != "matched":
            print(f"  chr{ch}:{pos}  {alleles}  -> {reason}")


if __name__ == "__main__":
    main()