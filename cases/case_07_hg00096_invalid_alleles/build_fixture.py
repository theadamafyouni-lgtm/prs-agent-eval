#!/usr/bin/env python3
"""
Build the case 7 input: take the clean case 1 VCF, corrupt the alleles of 20
variants with invalid letters, and record which 20 were changed.

Substitution (per spec design): A->B, C->S, T->L, G->J
Edits are done on the raw text, so the invalid bases write fine regardless of
what a VCF parser would accept.
"""

import gzip
import random

# ---- config: set these before running ----
CLEAN_VCF = "/root/pgs_project/tests/agent_eval/cases/case_01_hg00096_grch38_missing/expected_output/HG00096_PGS000577_GRCh38_clean.vcf.gz"
OUT_VCF = "/root/pgs_project/tests/agent_eval/cases/case_07_hg00096_invalid_alleles/input/HG00096_PGS000577_GRCh38_invalid.vcf"
CHANGED = "/root/pgs_project/tests/agent_eval/cases/case_07_hg00096_invalid_alleles/expected_output/changed_variants.txt"
N         = 20
FIELD     = "REF"   # corrupt this allele only: "REF" or "ALT"
SUBS      = {"A": "B", "C": "S", "T": "L", "G": "J"}
SEED      = 7       # deterministic selection
# -------------------------------------------

PALINDROMES = {("A", "T"), ("T", "A"), ("C", "G"), ("G", "C")}
COL = {"REF": 3, "ALT": 4}[FIELD]


def is_eligible(fields):
    # autosomal, biallelic SNP, non-palindromic so it counts toward the score
    chrom = fields[0].replace("chr", "")
    if chrom not in {str(i) for i in range(1, 23)}:
        return False
    ref, alt = fields[3].upper(), fields[4].upper()
    if len(ref) != 1 or len(alt) != 1:
        return False
    if ref not in SUBS or alt not in SUBS:
        return False
    if (ref, alt) in PALINDROMES:
        return False
    return True


def corrupt(allele):
    return "".join(SUBS.get(b.upper(), b) for b in allele)


# read all lines, find eligible data records
opener = gzip.open if CLEAN_VCF.endswith(".gz") else open
with opener(CLEAN_VCF, "rt") as fh:
    lines = fh.readlines()

eligible = []
for i, line in enumerate(lines):
    if line.startswith("#"):
        continue
    if is_eligible(line.rstrip("\n").split("\t")):
        eligible.append(i)

if len(eligible) < N:
    raise SystemExit(f"only {len(eligible)} eligible variants, need {N}")

random.seed(SEED)
chosen = sorted(random.sample(eligible, N))

# corrupt the chosen records and log the change
changed = []
for i in chosen:
    fields = lines[i].rstrip("\n").split("\t")
    original = fields[COL]
    fields[COL] = corrupt(original)
    lines[i] = "\t".join(fields) + "\n"
    changed.append((fields[0], fields[1], fields[2], original, fields[COL]))

with open(OUT_VCF, "w") as fh:
    fh.writelines(lines)

with open(CHANGED, "w") as fh:
    fh.write(f"# {N} variants corrupted in {FIELD}; map A->B C->S T->L G->J\n")
    fh.write("CHROM\tPOS\tID\tORIGINAL\tCHANGED\n")
    for row in changed:
        fh.write("\t".join(row) + "\n")

print(f"corrupted {len(changed)} variants in {FIELD}, wrote:")
print(f"  input:   {OUT_VCF}")
print(f"  changed: {CHANGED}")
print("\nselected variants:")
for row in changed:
    print("  " + "\t".join(row))