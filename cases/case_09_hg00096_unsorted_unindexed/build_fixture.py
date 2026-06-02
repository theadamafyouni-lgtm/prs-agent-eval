#!/usr/bin/env python3
"""
build_fixture.py - case_09 (operational transforms, positive path)

Takes case_01's finished input VCF and applies content-preserving operational
corruption:
  - decompress to plain text (no .gz)
  - shuffle the data-record order (file becomes unsorted)
  - emit with no .tbi index

The header block is left untouched and in its original order, so ##fileformat
stays first and build identification still succeeds normally. Only record
ORDER changes - the set of records, their fields, and the genotype calls are
byte-identical to the source. This is purely an operational transform.

Expected agent behavior: recognize the input is uncompressed / unsorted /
unindexed, repair it (sort -> bgzip -> tabix) per AGENT_SPEC rule 21, then run
the normal pipeline. Because the source still carries case_01's dropped
variants, imputation also runs, and the agent should land on the same PRS as
case_01 (8.96587).

Reproducible: fixed RNG seed, so re-running regenerates the identical fixture.

Run from anywhere; paths are anchored on this script's location.
    python3 build_fixture.py
"""

import gzip
import random
from pathlib import Path

SEED = 0xC0FFEE  # deterministic shuffle

SCRIPT_DIR = Path(__file__).resolve().parent            # cases/case_09_.../
CASES_DIR = SCRIPT_DIR.parent                           # cases/

SRC = (
    CASES_DIR
    / "case_01_hg00096_grch38_missing"
    / "input"
    / "HG00096_PGS000577_GRCh38_input.vcf.gz"
)
OUT_DIR = SCRIPT_DIR / "input"
OUT = OUT_DIR / "HG00096_PGS000577_GRCh38_scrambled.vcf"  # plain, no .gz, no .tbi


def read_vcf_lines(path):
    with gzip.open(path, "rt") as fh:
        return fh.read().splitlines()


def main():
    if not SRC.exists():
        raise SystemExit(f"source input not found: {SRC}")

    lines = read_vcf_lines(SRC)
    header = [ln for ln in lines if ln.startswith("#")]
    body = [ln for ln in lines if not ln.startswith("#")]

    # validity / content-preservation invariants
    assert header and header[0].startswith("##fileformat"), \
        "source header does not start with ##fileformat"
    assert body, "source has no data records"

    # shuffle ONLY the data records; header order is preserved
    shuffled = body[:]
    random.Random(SEED).shuffle(shuffled)
    assert len(shuffled) == len(body)
    assert sorted(shuffled) == sorted(body), "scramble altered record content"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w") as fh:
        fh.write("\n".join(header + shuffled) + "\n")

    # never ship a stale index alongside the fixture
    tbi = Path(str(OUT) + ".tbi")
    if tbi.exists():
        tbi.unlink()

    print(f"source        : {SRC}")
    print(f"output        : {OUT}  (plain .vcf, no .tbi)")
    print(f"header lines  : {len(header)}")
    print(f"data records  : {len(body)} (order scrambled, content identical)")
    print("note          : agent must sort -> bgzip -> tabix before scoring")


if __name__ == "__main__":
    main()
