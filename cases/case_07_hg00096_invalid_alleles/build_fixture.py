#!/usr/bin/env python3
"""
build_fixture.py - case_07 (invalid alleles, EXPLORATORY)

Corrupts ~20% of case_01's input records by replacing a REF or ALT base with an
invalid (non-ACGT) character (Z, IUPAC ambiguity codes). No spec rule defines
invalid-allele handling yet -- this run OBSERVES current behavior to shape V11 #6.

~20% is deliberately below the proposed 25% "structurally malformed -> refuse"
threshold, so the target behavior (once #6 exists) is RECOVERY: drop invalid rows,
treat as missing, impute from WGS, recover, return case_01's 8.96587.

Left operationally clean (bgzipped, tabix-indexed) to isolate invalid-allele handling.

    python3 build_fixture.py
"""

import gzip
import random
import subprocess
from pathlib import Path

FRACTION = 0.20
SEED = 0x07BAD
INVALID = ["Z", "R", "Y", "S", "W", "K", "M", "B", "D", "H", "V"]  # non-ACGT

SCRIPT_DIR = Path(__file__).resolve().parent
CASES_DIR = SCRIPT_DIR.parent
SRC = (CASES_DIR / "case_01_hg00096_grch38_missing" / "input"
       / "HG00096_PGS000577_GRCh38_input.vcf.gz")
OUT_DIR = SCRIPT_DIR / "input"
OUT_VCF = OUT_DIR / "HG00096_PGS000577_invalid_alleles.vcf"
OUT_GZ = Path(str(OUT_VCF) + ".gz")


def read_lines(path):
    with gzip.open(path, "rt") as fh:
        return fh.read().splitlines()


def main():
    if not SRC.exists():
        raise SystemExit(f"source not found: {SRC}")

    lines = read_lines(SRC)
    header = [l for l in lines if l.startswith("#")]
    body = [l for l in lines if not l.startswith("#")]

    rng = random.Random(SEED)
    n = max(1, round(len(body) * FRACTION))
    targets = sorted(rng.sample(range(len(body)), n))

    log = []
    for i in targets:
        cols = body[i].split("\t")          # 0 CHROM 1 POS 2 ID 3 REF 4 ALT ...
        field = rng.choice([3, 4])          # corrupt REF or ALT
        bad = rng.choice(INVALID)
        old = cols[field]
        cols[field] = bad
        body[i] = "\t".join(cols)
        log.append((cols[0], cols[1], "REF" if field == 3 else "ALT", old, bad))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_VCF, "w") as fh:
        fh.write("\n".join(header + body) + "\n")
    if OUT_GZ.exists():
        OUT_GZ.unlink()
    subprocess.run(["bgzip", "-f", str(OUT_VCF)], check=True)
    subprocess.run(["tabix", "-p", "vcf", str(OUT_GZ)], check=True)

    print(f"source       : {SRC}")
    print(f"output       : {OUT_GZ} (+ .tbi)")
    print(f"records      : {len(body)}")
    print(f"corrupted    : {n} ({n/len(body)*100:.1f}%)  [below proposed 25% refuse threshold]")
    print(f"invalid chars: {sorted(set(x[4] for x in log))}")
    print("corrupted records (chr pos field old->new):")
    for x in log:
        print(f"  {x[0]} {x[1]} {x[2]} {x[3]}->{x[4]}")


if __name__ == "__main__":
    main()
