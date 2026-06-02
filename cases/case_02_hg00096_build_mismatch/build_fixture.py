"""
Build case_02 input VCF: takes case_01's input (HG00096 GRCh38) and relabels
the header to claim GRCh37 via swapped contig lengths. The body is untouched.
The agent should detect the resulting build mismatch vs. PGS000577 (HmPOS=GRCh38).
"""
import subprocess, re

SRC = "cases/case_01_hg00096_grch38_missing/input/HG00096_PGS000577_GRCh38_input.vcf.gz"
DST = "cases/case_02_hg00096_build_mismatch/input/HG00096_PGS000577_mislabeled_grch37.vcf.gz"
TMP = "/tmp/case_02_header_grch37.txt"

# Canonical GRCh37 (hg19) contig lengths from UCSC.
GRCH37 = {
    "chr1": 249250621,  "chr2": 243199373,  "chr3": 198022430,  "chr4": 191154276,
    "chr5": 180915260,  "chr6": 171115067,  "chr7": 159138663,  "chr8": 146364022,
    "chr9": 141213431,  "chr10": 135534747, "chr11": 135006516, "chr12": 133851895,
    "chr13": 115169878, "chr14": 107349540, "chr15": 102531392, "chr16": 90354753,
    "chr17": 81195210,  "chr18": 78077248,  "chr19": 59128983,  "chr20": 63025520,
    "chr21": 48129895,  "chr22": 51304566,  "chrX": 155270560,  "chrY": 59373566,
    "chrMT": 16569,     "chrM": 16569,
}
# Also handle unprefixed names
GRCH37.update({k.replace("chr",""): v for k,v in list(GRCH37.items()) if k.startswith("chr")})

header = subprocess.run(
    ["bcftools","view","-h",SRC], capture_output=True, text=True, check=True
).stdout

new_lines = []
for line in header.splitlines():
    if line.startswith("##contig="):
        m = re.search(r"ID=([^,>]+)", line)
        if m and m.group(1) in GRCH37:
            line = re.sub(r"length=\d+", f"length={GRCH37[m.group(1)]}", line)
    new_lines.append(line)

with open(TMP,"w") as f:
    f.write("\n".join(new_lines) + "\n")

subprocess.run(["bcftools","reheader","-h",TMP,"-o",DST,SRC], check=True)
subprocess.run(["tabix","-p","vcf",DST], check=True)
print(f"Wrote {DST}")
