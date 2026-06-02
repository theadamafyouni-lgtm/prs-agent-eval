#!/usr/bin/env python3
"""
case_04 fixture builder.

Creates input/HG00096_PGS000330.vcf.gz: HG00096's WGS filtered to PGS000330
scoring positions. Position-level filter only; pgsc_calc enforces exact
REF/ALT match downstream in MATCH_VARIANTS. The pre-filter exists to avoid
the MATCH_VARIANTS OOM on 8GB VMs (70M WGS records + 6.4M scoring positions
loaded simultaneously by pgscatalog-match).
"""
import subprocess
from pathlib import Path

CASE = Path(__file__).parent
WGS = Path("/root/samples/EUR/HG00096/HG00096_wgs_GRCh38.vcf.gz")
PGS = Path("/root/pgs_project/tests/agent_eval/scoring_models/PGS000330/PGS000330_hmPOS_GRCh38.txt.gz")

positions = CASE / "pgs_positions.tsv.gz"
output = CASE / "input" / "HG00096_PGS000330.vcf.gz"
output.parent.mkdir(exist_ok=True)

# Extract chr+pos from PGS file, prefix with 'chr', sort, dedup, bgzip, index
awk = r'''/^#/ {next} !h { for(i=1;i<=NF;i++){if($i=="hm_chr")c=i; if($i=="hm_pos")p=i} h=1; next } $c != "" && $p != "" {print "chr"$c"\t"$p}'''
subprocess.run(f"zcat {PGS} | awk -F'\\t' '{awk}' | sort -k1,1 -k2,2n -u | bgzip > {positions}", shell=True, check=True)
subprocess.run(["tabix", "-s", "1", "-b", "2", "-e", "2", str(positions)], check=True)

# Filter WGS to those positions, index
subprocess.run(["bcftools", "view", "-T", str(positions), "-Oz", "-o", str(output), str(WGS)], check=True)
subprocess.run(["tabix", "-p", "vcf", str(output)], check=True)

# Cleanup intermediate position file (regenerable)
positions.unlink()
Path(str(positions) + ".tbi").unlink()

print(f"Done. {output}")
