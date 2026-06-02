"""
Build case_03 input VCF: takes case_01's input and strips the length= field
from every ##contig line in the header, plus removes any ##reference or
##assembly lines. Leaves the body untouched. The agent should see lengthless
contigs and no authoritative build signal, and refuse to identify the build
per rule 8 (length= required) and rule 9 (refuse rather than guess).
"""
import subprocess, re

SRC = "cases/case_01_hg00096_grch38_missing/input/HG00096_PGS000577_GRCh38_input.vcf.gz"
DST = "cases/case_03_hg00096_ambiguous_build/input/HG00096_PGS000577_lengthless_header.vcf.gz"
TMP = "/tmp/case_03_header_lengthless.txt"

header = subprocess.run(
    ["bcftools","view","-h",SRC], capture_output=True, text=True, check=True
).stdout

new_lines = []
for line in header.splitlines():
    if line.startswith("##reference=") or line.startswith("##assembly="):
        continue  # drop any authoritative non-contig signals
    if line.startswith("##contig="):
        line = re.sub(r",length=\d+", "", line)  # strip length=N
    new_lines.append(line)

with open(TMP,"w") as f:
    f.write("\n".join(new_lines) + "\n")

subprocess.run(["bcftools","reheader","-h",TMP,"-o",DST,SRC], check=True)
subprocess.run(["tabix","-p","vcf",DST], check=True)
print(f"Wrote {DST}")
