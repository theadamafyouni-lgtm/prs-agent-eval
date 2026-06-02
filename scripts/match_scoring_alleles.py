#!/usr/bin/env python3
"""Match a VCF's variants to a PGS scoring file by chr + pos + alleles.

Keeps only records whose {REF, ALT} exactly match the scoring model's
{effect_allele, other_allele}. Writes a bgzipped, tabix-indexed VCF and
prints the kept/dropped counts.

Assumes bi-allelic-split input (one ALT per row) — true for 1000 Genomes
Phase 3 high-coverage data. Symbolic/missing alleles won't match and are
dropped, which is intended for SNP scoring models.

usage: match_scoring_alleles.py scoring.txt.gz in.vcf[.gz] out.vcf.gz
"""
import gzip, subprocess, sys

if len(sys.argv) != 4:
    sys.exit(f"usage: {sys.argv[0]} scoring.txt.gz in.vcf[.gz] out.vcf.gz")

scoring_file, in_vcf, out_gz = sys.argv[1], sys.argv[2], sys.argv[3]
if not out_gz.endswith(".vcf.gz"):
    sys.exit("output must end in .vcf.gz")
out_vcf = out_gz[:-3]  # write uncompressed first, then bgzip

# (chrom, pos) -> {effect, other} from the scoring file
alleles = {}
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
        alleles[(c[ci], c[pi])] = frozenset({c[ei], c[oi]})

# Match the VCF against the scoring alleles
kept = dropped = 0
opener = gzip.open if in_vcf.endswith(".gz") else open
with opener(in_vcf, "rt") as fin, open(out_vcf, "w") as fout:
    for line in fin:
        if line.startswith("#"):
            fout.write(line); continue
        c = line.rstrip("\n").split("\t")
        chrom = c[0].removeprefix("chr")
        if frozenset({c[3], c[4]}) == alleles.get((chrom, c[1])):
            fout.write(line); kept += 1
        else:
            dropped += 1

# Compress + index (fixed, deterministic post-steps)
subprocess.run(["bgzip", "-f", out_vcf], check=True)
subprocess.run(["bcftools", "index", "-t", "-f", out_gz], check=True)

print(f"kept {kept}, dropped {dropped}")
print(f"wrote {out_gz} ({kept} records)")