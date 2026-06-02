#!/usr/bin/env python3
"""Fill missing scoring variants in a VCF from a hardcoded WGS reference."""
import gzip, subprocess, sys, tempfile
from collections import Counter
from pathlib import Path

WGS = "/root/samples/EUR/HG00096/HG00096_wgs_GRCh38.vcf.gz"
MISSING = {"", "NA", "."}

corrupted, scoring_file, out_gz = sys.argv[1:4]

# load scoring positions -> {effect, other}, normalizing chr-prefix
scoring, header = {}, None
with gzip.open(scoring_file, "rt") as f:
    for line in f:
        if line.startswith("#"):
            continue
        c = line.rstrip("\n").split("\t")
        if header is None:
            header = c
            ci, pi = header.index("hm_chr"), header.index("hm_pos")
            ei = header.index("effect_allele")
            oi = header.index("other_allele") if "other_allele" in header else header.index("hm_inferOtherAllele")
            continue
        ch, p, eff, oth = c[ci].removeprefix("chr"), c[pi], c[ei], c[oi]
        if any(v in MISSING for v in (ch, p, eff, oth)):
            continue
        scoring[(ch, p)] = frozenset({eff, oth})

# read patient VCF: headers, data records, present positions (normalized to bare)
opener = gzip.open if corrupted.endswith(".gz") else open
present, headers, records = set(), [], []
with opener(corrupted, "rt") as f:
    for line in f:
        if line.startswith("#"):
            headers.append(line)
        else:
            records.append(line if line.endswith("\n") else line + "\n")
            c = line.split("\t")
            present.add((c[0].removeprefix("chr"), c[1]))

# detect chr-prefix conventions: patient VCF (for output) and WGS (for BED query)
patient_prefix = "chr" if any(r.startswith("chr") for r in records) else ""
wgs_hdr = subprocess.run(["bcftools", "view", "-h", WGS], capture_output=True, text=True, check=True).stdout
wgs_prefix = "chr" if "##contig=<ID=chr" in wgs_hdr else ""

# missing positions -> temp BED (matching the WGS's contig convention)
missing = [(ch, p) for ch, p in scoring if (ch, p) not in present]
with tempfile.NamedTemporaryFile("w", suffix=".bed", delete=False) as f:
    for ch, p in missing:
        f.write(f"{wgs_prefix}{ch}\t{int(p)-1}\t{p}\n")
    bed = f.name

# pull missing from WGS, split any multi-allelics
view = subprocess.run(["bcftools", "view", "-R", bed, "--regions-overlap", "pos", WGS, "-Ov"], capture_output=True, text=True, check=True)
norm = subprocess.run(["bcftools", "norm", "-m", "-any", "-Ov"], input=view.stdout, capture_output=True, text=True, check=True)
Path(bed).unlink()

# keep only WGS records with EXACT allele match against scoring,
# rewriting the contig column to match the patient VCF's convention
recovered, recovered_pos = [], set()
for line in norm.stdout.splitlines():
    if line.startswith("#"):
        continue
    c = line.split("\t")
    ch, pos = c[0].removeprefix("chr"), c[1]
    if frozenset({c[3], c[4]}) == scoring.get((ch, pos)):
        c[0] = f"{patient_prefix}{ch}"
        recovered.append("\t".join(c) + "\n")
        recovered_pos.add((ch, pos))

# merge, sort, bgzip, index
with tempfile.NamedTemporaryFile("w", suffix=".vcf", delete=False) as f:
    f.writelines(headers + records + recovered)
    merged = f.name
subprocess.run(["bcftools", "sort", merged, "-Oz", "-o", out_gz], check=True)
subprocess.run(["bcftools", "index", "-t", "-f", out_gz], check=True)
Path(merged).unlink()

# report
could_not = [m for m in missing if m not in recovered_pos]
print(f"expected: {len(scoring)}, present: {len(present & set(scoring))}, missing: {len(missing)}, recovered: {len(recovered_pos)}, unrecovered: {len(could_not)}")
if could_not:
    print(f"unrecovered by chrom: {dict(Counter(ch for ch, _ in could_not))}")
print(f"wrote {out_gz}")