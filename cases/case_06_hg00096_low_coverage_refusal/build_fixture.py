#!/usr/bin/env python3
"""
build_fixture.py - case_06 (low-coverage refusal)

Synthetic model = all of PGS000577 (real, recoverable) + N_FAKE fake autosomal
non-palindromic variants at positions ABSENT from HG00096's WGS (tabix-verified),
so imputation cannot recover them. The fakes drag coverage below 90% -> refuse.

Why synthetic: you can't manufacture low coverage by dropping real variants --
imputation refills them from the WGS. Positions the WGS lacks are the only way to
force genuine, unrecoverable missingness. (Interim approach until imputation.py is
parameterized to take a subsetted WGS source.)

    python3 build_fixture.py
"""

import gzip
import random
import subprocess
from pathlib import Path

N_FAKE = 40                # 101 / (111 + 40) ~= 67% coverage -> clear refuse
SEED = 0x06C0FFEE

SCRIPT_DIR = Path(__file__).resolve().parent
EVAL_ROOT = SCRIPT_DIR.parent.parent
REAL_MODEL = EVAL_ROOT / "scoring_models" / "PGS000577" / "PGS000577_hmPOS_GRCh38.txt.gz"
WGS = Path("/root/samples/EUR/HG00096/HG00096_wgs_GRCh38.vcf.gz")
OUT_DIR = SCRIPT_DIR / "input"
OUT_MODEL = OUT_DIR / "PGSSYNTH06_hmPOS_GRCh38.txt.gz"

CHROM_LEN = {
    1: 248956422, 2: 242193529, 3: 198295559, 4: 190214555, 5: 181538259,
    6: 170805979, 7: 159345973, 8: 145138636, 9: 138394717, 10: 133797422,
    11: 135086622, 12: 133275309, 13: 114364328, 14: 107043718, 15: 101991189,
    16: 90338345, 17: 83257441, 18: 80373285, 19: 58617616, 20: 64444167,
    21: 46709983, 22: 50818468,
}
NONPAL = [("A", "G"), ("G", "A"), ("C", "T"), ("T", "C")]  # never palindromic


def wgs_prefix():
    out = subprocess.run(["tabix", "-l", str(WGS)], capture_output=True, text=True)
    return "chr" if any(n.startswith("chr") for n in out.stdout.split()) else ""


def wgs_has(prefix, chrom, pos):
    region = f"{prefix}{chrom}:{pos}-{pos}"
    out = subprocess.run(["tabix", str(WGS), region], capture_output=True, text=True)
    return bool(out.stdout.strip())


def main():
    if not REAL_MODEL.exists():
        raise SystemExit(f"real model not found: {REAL_MODEL}")
    if not WGS.exists():
        raise SystemExit(f"WGS not found: {WGS}")
    if not Path(str(WGS) + ".tbi").exists():
        raise SystemExit(f"WGS not tabix-indexed; run: tabix -p vcf {WGS}")

    with gzip.open(REAL_MODEL, "rt") as fh:
        raw = fh.read().splitlines()
    meta = [l for l in raw if l.startswith("#")]
    body = [l for l in raw if not l.startswith("#")]
    col_header, data_rows = body[0], body[1:]
    idx = {c: i for i, c in enumerate(col_header.split("\t"))}
    ncol = len(col_header.split("\t"))

    prefix = wgs_prefix()
    rng = random.Random(SEED)
    fakes, tries = [], 0
    while len(fakes) < N_FAKE and tries < N_FAKE * 100:
        tries += 1
        chrom = rng.randint(1, 22)
        pos = rng.randint(1_000_000, CHROM_LEN[chrom] - 1_000_000)
        if wgs_has(prefix, chrom, pos):
            continue                      # in WGS -> recoverable, skip
        ea, oa = rng.choice(NONPAL)
        row = [""] * ncol
        def put(name, val):
            if name in idx: row[idx[name]] = val
        put("rsID", f"rs_FAKE06_{len(fakes)+1:03d}")
        put("chr_name", str(chrom)); put("chr_position", str(pos))
        put("effect_allele", ea); put("other_allele", oa)
        put("effect_weight", "0.1")
        put("hm_chr", str(chrom)); put("hm_pos", str(pos))
        fakes.append("\t".join(row))

    if len(fakes) < N_FAKE:
        raise SystemExit(f"only {len(fakes)} WGS-absent positions found; widen search")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with gzip.open(OUT_MODEL, "wt") as fh:
        fh.write("\n".join(meta + [col_header] + data_rows + fakes) + "\n")

    cov = 101 / (111 + len(fakes)) * 100
    print(f"real model     : {REAL_MODEL}")
    print(f"synth model    : {OUT_MODEL}")
    print(f"real rows      : {len(data_rows)}")
    print(f"fake rows      : {len(fakes)} (autosomal, non-palindromic, WGS-absent -> unrecoverable)")
    print(f"WGS chrom style: '{prefix}' prefix")
    print(f"expected cov   : 101 / (111 + {len(fakes)}) = {cov:.1f}%  -> REFUSE (<90%)")


if __name__ == "__main__":
    main()
