#!/usr/bin/env python3
"""Build a clean test-patient VCF from a patient WGS and a PGS scoring model.

Pipeline (one scoring model per run):
  1. Read scoring model -> {(chrom, pos): {effect, other}} and a BED of positions.
  2. bcftools view -R bed WGS    -> extract only the scoring positions.
  3. bcftools norm -m -any       -> split multiallelic sites to one ALT per row.
  4. For each record at a scoring position, decide:
       - ambiguous scoring pair (palindromic A/T or C/G) -> DROP by default
         (strand can't be resolved from alleles alone). Use --keep-ambiguous
         to keep them instead.
       - {REF,ALT} == {effect,other}      -> KEEP   (exact match)
       - partner-swap matches             -> CORRECT REF/ALT, KEEP (strand flip)
       - otherwise                        -> DROP   (no match)
  5. Write a bgzipped + tabix-indexed VCF, print a per-stage report.

This is a fixture-construction tool. The agent never runs it. It works for any
PGS Catalog harmonized scoring file (reads hm_chr / hm_pos / effect_allele /
other_allele columns) and any single-sample WGS of the SAME genome build as the
scoring model.

usage:
  build_test_patient.py [--keep-ambiguous] SCORING.txt.gz WGS.vcf[.gz] OUT.vcf.gz
"""
import argparse
import gzip
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

MISSING = {"", "NA", "."}
PARTNER = {"A": "T", "T": "A", "C": "G", "G": "C"}


def open_any(path):
    p = str(path)
    return gzip.open(p, "rt") if p.endswith(".gz") else open(p, "rt")


def is_ambiguous(alleles):
    """True if the allele pair is palindromic / strand-ambiguous (A/T or C/G)."""
    return alleles in (frozenset({"A", "T"}), frozenset({"C", "G"}))


def partner_swap(alleles):
    """Complement each allele: {A, C} -> {T, G}."""
    return frozenset(PARTNER.get(a, a) for a in alleles)


def load_scoring(scoring_file):
    """Return (scoring, hm_build).

    scoring: {(chrom_without_chr_prefix, pos): frozenset({effect, other})}
    hm_build: value of #HmPOS_build= metadata line, or None if absent.
    """
    scoring = {}
    hm_build = None
    header = None
    with open_any(scoring_file) as f:
        for line in f:
            if line.startswith("#"):
                if line.startswith("#HmPOS_build="):
                    hm_build = line.split("=", 1)[1].strip()
                continue
            c = line.rstrip("\n").split("\t")
            if header is None:
                header = c
                ci, pi = header.index("hm_chr"), header.index("hm_pos")
                ei = header.index("effect_allele")
                oi = (header.index("other_allele") if "other_allele" in header
                      else header.index("hm_inferOtherAllele"))
                continue
            ch = c[ci].removeprefix("chr")
            p, eff, oth = c[pi], c[ei], c[oi]
            if any(v in MISSING for v in (ch, p, eff, oth)):
                continue
            scoring[(ch, p)] = frozenset({eff, oth})
    return scoring, hm_build


def detect_wgs_prefix(wgs):
    """Return 'chr' if the WGS contigs use a chr prefix, else ''."""
    hdr = subprocess.run(["bcftools", "view", "-h", wgs],
                         capture_output=True, text=True, check=True).stdout
    return "chr" if "##contig=<ID=chr" in hdr else ""


def write_bed(scoring, wgs_prefix, bed_path):
    """Write a 0-based half-open BED of scoring positions in the WGS's convention."""
    with open(bed_path, "w") as f:
        for ch, p in scoring:
            f.write(f"{wgs_prefix}{ch}\t{int(p) - 1}\t{p}\n")


def extract_and_split(wgs, bed_path):
    """bcftools view -R (extract scoring positions) | norm -m -any (split multiallelics)."""
    view = subprocess.run(
        ["bcftools", "view", "-R", bed_path, "--regions-overlap", "pos", wgs, "-Ov"],
        capture_output=True, text=True, check=True)
    norm = subprocess.run(
        ["bcftools", "norm", "-m", "-any", "-Ov"],
        input=view.stdout, capture_output=True, text=True, check=True)
    return norm.stdout


def clean_records(normed_vcf, scoring, drop_ambiguous):
    """Apply the allele logic. Returns (header_lines, kept_records, stats)."""
    header_lines = []
    kept = []
    stats = Counter()
    for line in normed_vcf.splitlines(keepends=True):
        if line.startswith("#"):
            header_lines.append(line)
            continue
        c = line.rstrip("\n").split("\t")
        ch, pos, ref, alt = c[0].removeprefix("chr"), c[1], c[3], c[4]
        scoring_pair = scoring.get((ch, pos))
        if scoring_pair is None:
            stats["no_scoring_entry"] += 1
            continue
        if drop_ambiguous and is_ambiguous(scoring_pair):
            stats["ambiguous_dropped"] += 1
            continue
        vcf_pair = frozenset({ref, alt})
        if vcf_pair == scoring_pair:
            kept.append(line if line.endswith("\n") else line + "\n")
            stats["exact_match"] += 1
        elif partner_swap(vcf_pair) == scoring_pair:
            c[3] = PARTNER.get(ref, ref)
            c[4] = PARTNER.get(alt, alt)
            kept.append("\t".join(c) + "\n")
            stats["strand_flip_corrected"] += 1
        else:
            stats["no_match_dropped"] += 1
    return header_lines, kept, stats


def main():
    ap = argparse.ArgumentParser(
        description="Build a clean test-patient VCF from a WGS and a PGS scoring model.")
    ap.add_argument("scoring", help="PGS Catalog harmonized scoring file (.txt.gz)")
    ap.add_argument("wgs", help="single-sample WGS VCF (.vcf or .vcf.gz), same build as scoring")
    ap.add_argument("out", help="output VCF (must end in .vcf.gz)")
    ap.add_argument("--keep-ambiguous", action="store_true",
                    help="keep palindromic A/T and C/G variants (default: drop them)")
    args = ap.parse_args()

    if not args.out.endswith(".vcf.gz"):
        sys.exit("output must end in .vcf.gz")
    for path in (args.scoring, args.wgs):
        if not Path(path).exists():
            sys.exit(f"file not found: {path}")

    scoring, hm_build = load_scoring(args.scoring)
    n_ambiguous = sum(1 for pair in scoring.values() if is_ambiguous(pair))
    print(f"scoring variants:        {len(scoring)}  (HmPOS_build={hm_build})")
    print(f"  of which ambiguous:    {n_ambiguous}")

    wgs_prefix = detect_wgs_prefix(args.wgs)
    with tempfile.NamedTemporaryFile("w", suffix=".bed", delete=False) as f:
        bed_path = f.name
    write_bed(scoring, wgs_prefix, bed_path)

    normed = extract_and_split(args.wgs, bed_path)
    Path(bed_path).unlink()

    header_lines, kept, stats = clean_records(
        normed, scoring, drop_ambiguous=not args.keep_ambiguous)

    out_vcf = args.out[:-3]  # strip .gz; bgzip recreates it
    with open(out_vcf, "w") as f:
        f.writelines(header_lines)
        f.writelines(kept)
    subprocess.run(["bgzip", "-f", out_vcf], check=True)
    subprocess.run(["bcftools", "index", "-t", "-f", args.out], check=True)

    print(f"exact match:             {stats['exact_match']}")
    print(f"strand flip corrected:   {stats['strand_flip_corrected']}")
    if args.keep_ambiguous:
        print(f"ambiguous kept:          (not dropped; --keep-ambiguous set)")
    else:
        print(f"ambiguous dropped:       {stats['ambiguous_dropped']}")
    print(f"no match dropped:        {stats['no_match_dropped']}")
    kept_n = stats["exact_match"] + stats["strand_flip_corrected"]
    print(f"kept (written):          {kept_n}")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()