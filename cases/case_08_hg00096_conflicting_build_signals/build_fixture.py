#!/usr/bin/env python3
"""
Build the case 8 input: keep the real GRCh38 records from the clean VCF and
attach a deliberately self-contradicting header so build detection has no clean
answer. This is a limitation probe, not a pass test.

Three contradictions injected into the header:
  1. ##reference claims one build, ##assembly claims the other (metadata vs metadata)
  2. ##contig lengths alternate GRCh37 / GRCh38 across chromosomes (no consensus)
  3. chrM length 16571 = the GRCh37 rCRS+2 tell, while autosomes are mixed
The genotype records are the genuine GRCh38 data, left exactly as they are.
"""

import gzip

# ---- config: set these before running ----
CLEAN_VCF = "/root/pgs_project/tests/agent_eval/cases/case_01_hg00096_grch38_missing/expected_output/HG00096_PGS000577_GRCh38_clean.vcf.gz"
OUT_VCF   = "/root/pgs_project/tests/agent_eval/cases/case_08_hg00096_conflicting_build_signals/input/HG00096_PGS000577_conflicting_build.vcf"

# What the top-authority line lies about. ##assembly gets the opposite build.
#   "GRCh37" -> reference says GRCh37 over GRCh38 data; agent that trusts it
#              calls the file GRCh37 and refuses on model mismatch (wrong reason).
#   "GRCh38" -> reference happens to match the real build; agent proceeds and
#              scores, blind to the contradictions below (right answer by luck).
REFERENCE_CLAIM = "GRCh37"
# -------------------------------------------

GRCH37 = {1:249250621,2:243199373,3:198022430,4:191154276,5:180915260,
          6:171115067,7:159138663,8:146364022,9:141213431,10:135534747,
          11:135006516,12:133851895,13:115169878,14:107349540,15:102531392,
          16:90354753,17:81195210,18:78077248,19:59128983,20:63025520,
          21:48129895,22:51304566,"M":16571}
GRCH38 = {1:248956422,2:242193529,3:198295559,4:190214555,5:181538259,
          6:170805979,7:159345973,8:145138636,9:138394717,10:133797422,
          11:135086622,12:133275309,13:114364328,14:107043718,15:101991189,
          16:90338345,17:83257441,18:80373285,19:58617616,20:64444167,
          21:46709983,22:50818468,"M":16569}

REF_FASTA = {"GRCh37": "file:///ref/human_g1k_v37.fasta",
             "GRCh38": "file:///ref/GRCh38_full_analysis_set.fasta"}
other = "GRCh38" if REFERENCE_CLAIM == "GRCh37" else "GRCh37"

# build the contradicting header block
inject = []
inject.append(f"##reference={REF_FASTA[REFERENCE_CLAIM]}")
inject.append(f"##assembly={other}")
for n in range(1, 23):                       # odd -> GRCh37 length, even -> GRCh38 length
    length = GRCH37[n] if n % 2 == 1 else GRCH38[n]
    inject.append(f"##contig=<ID=chr{n},length={length}>")
inject.append(f"##contig=<ID=chrM,length={GRCH37['M']}>")   # the rCRS+2 tell

# read clean file, keep records + non-build meta, drop original contig/reference/assembly
opener = gzip.open if CLEAN_VCF.endswith(".gz") else open
with opener(CLEAN_VCF, "rt") as fh:
    lines = fh.readlines()

fileformat = "##fileformat=VCFv4.2\n"
kept_meta, chrom_line, records = [], None, []
for line in lines:
    if line.startswith("##fileformat"):
        fileformat = line
    elif line.startswith(("##FILTER", "##INFO", "##FORMAT", "##ALT")):
        kept_meta.append(line)                # structural lines only
    elif line.startswith("##"):
        continue                              # drop contig/reference/assembly (we inject our own) AND all provenance (##source, ##fileDate, ##bcftools_*) that leak the build via filenames
    elif line.startswith("#CHROM"):
        chrom_line = line
    else:
        records.append(line)

with open(OUT_VCF, "w") as out:
    out.write(fileformat)
    for m in inject:
        out.write(m + "\n")
    out.writelines(kept_meta)
    out.write(chrom_line)
    out.writelines(records)

print(f"wrote {OUT_VCF}")
print(f"  reference claims: {REFERENCE_CLAIM}   assembly claims: {other}")
print(f"  contigs: odd chr = GRCh37 length, even chr = GRCh38 length, chrM = 16571")
print(f"  records kept (real GRCh38): {len(records)}")
