#!/usr/bin/env python3
"""Verify a VCF against a PGS Catalog scoring file (independent check).

General-purpose: works for any PGS Catalog scoring file and any VCF.
Different code path from the matcher, so it's a real check, not a re-run.

Reports:
  1. VCF records that do NOT match a scoring entry by chr+pos+alleles.
     For a correctly built/processed VCF this should be 0. This is the
     PASS/FAIL criterion.
  2. Scoring variants absent from the VCF, broken down by chromosome.
     Informational — what counts as "expected" depends on the specific
     test (a sample missing a chromosome, homozygous-reference positions
     not stored, a build mismatch shifting everything). The script
     reports the breakdown; you interpret it for your test.

usage: verify_match.py scoring.txt.gz target.vcf[.gz]
"""
import gzip, sys
from collections import Counter

if len(sys.argv) != 3:
    sys.exit(f"usage: {sys.argv[0]} scoring.txt.gz target.vcf[.gz]")

scoring_file, vcf = sys.argv[1], sys.argv[2]

# scoring: (chrom, pos) -> {effect, other}
scoring = {}
with gzip.open(scoring_file, "rt") as f:
    header = None
    for line in f:
        if line.startswith("#"):
            continue
        c = line.rstrip("\n").split("\t")
        if header is None:
            header = c
            ci, pi = header.index("hm_chr"), header.index("hm_pos")
            ei = header.index("effect_allele")
            oi = header.index("other_allele") if "other_allele" in header \
                 else header.index("hm_inferOtherAllele")
            continue
        if c[ci] in ("", "NA", ".") or c[pi] in ("", "NA", "."):
            continue
        scoring[(c[ci], c[pi])] = frozenset({c[ei], c[oi]})

# vcf records: list of (chrom, pos, {ref, alt})
records = []
opener = gzip.open if vcf.endswith(".gz") else open
with opener(vcf, "rt") as f:
    for line in f:
        if line.startswith("#"):
            continue
        c = line.rstrip("\n").split("\t")
        records.append((c[0].removeprefix("chr"), c[1], frozenset({c[3], c[4]})))

# Check 1: every VCF record must match a scoring entry exactly
mismatches = [(ch, p, ra) for ch, p, ra in records
              if scoring.get((ch, p)) != ra]

# Check 2: scoring variants absent from the VCF
vcf_positions = {(ch, p) for ch, p, _ in records}
absent = [k for k in scoring if k not in vcf_positions]
absent_by_chrom = Counter(ch for ch, _ in absent)

print(f"VCF records:                      {len(records)}")
print(f"Scoring variants:                 {len(scoring)}")
print(f"VCF records that DON'T match:     {len(mismatches)}")
for m in mismatches[:10]:
    print("  MISMATCH:", m)
print(f"Scoring variants absent from VCF: {len(absent)}")
print(f"  absent by chromosome: {dict(sorted(absent_by_chrom.items()))}")

if mismatches:
    sys.exit("FAIL: some VCF records do not match the scoring file")
print("PASS: every VCF record matches a scoring entry exactly")