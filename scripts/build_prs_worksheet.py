#!/usr/bin/env python3
"""Join a VCF against the scoring model into a flat CSV for a manual PRS calc.

One row per scoring variant (sorted by chrom/pos): the scoring weight,
alleles and rsID next to the patient's genotype from the VCF (or flagged
ABSENT). Computes nothing -- the dosage logic and the PRS sum are yours.

usage: build_prs_worksheet.py sample.vcf[.gz] scoring.txt.gz out.csv
"""
import csv, gzip, sys

MISSING = {"", "NA", "."}


def open_any(path):
    p = str(path)
    return gzip.open(p, "rt") if p.endswith(".gz") else open(p, "rt")


def chrom_key(ch):
    return (0, int(ch)) if ch.isdigit() else (1, ch)


def load_scoring(scoring_file):
    """ordered list of (chrom_no_prefix, pos, effect, other, weight, rsid)."""
    rows = []
    header = None
    with gzip.open(scoring_file, "rt") as f:
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
                wi = header.index("effect_weight")
                ri = header.index("hm_rsID") if "hm_rsID" in header else None
                continue
            chrom, pos, eff, oth, wt = c[ci], c[pi], c[ei], c[oi], c[wi]
            rsid = c[ri] if ri is not None and c[ri] not in MISSING else "."
            if any(v in MISSING for v in (chrom, pos, eff, wt)):
                continue
            rows.append((chrom, pos, eff, oth, wt, rsid))
    return rows


def load_vcf(path):
    """(chrom_no_prefix, pos) -> (ref, alt, gt)."""
    recs = {}
    with open_any(path) as f:
        for line in f:
            if line.startswith("#"):
                continue
            c = line.rstrip("\n").split("\t")
            chrom, pos, ref, alt = c[0].removeprefix("chr"), c[1], c[3], c[4]
            fmt, sample = c[8].split(":"), c[9].split(":")
            gt = sample[fmt.index("GT")] if "GT" in fmt else "."
            recs[(chrom, pos)] = (ref, alt, gt)
    return recs


def main():
    if len(sys.argv) != 4:
        sys.exit(f"usage: {sys.argv[0]} sample.vcf[.gz] scoring.txt.gz out.csv")
    vcf, scoring_file, out_csv = sys.argv[1:4]

    scoring = load_scoring(scoring_file)
    vcf_recs = load_vcf(vcf)

    out_rows = []
    present = 0
    for chrom, pos, eff, oth, wt, rsid in scoring:
        rec = vcf_recs.get((chrom, pos))
        if rec is None:
            out_rows.append([chrom, pos, eff, oth, wt, rsid,
                             ".", ".", ".", "ABSENT"])
        else:
            ref, alt, gt = rec
            out_rows.append([chrom, pos, eff, oth, wt, rsid,
                             ref, alt, gt, "present"])
            present += 1

    out_rows.sort(key=lambda r: (chrom_key(r[0]), int(r[1])))

    cols = ["chrom", "pos", "effect_allele", "other_allele", "effect_weight",
            "rsID", "vcf_ref", "vcf_alt", "vcf_gt", "status"]
    with open(out_csv, "w", newline="") as out:
        w = csv.writer(out)
        w.writerow(cols)
        w.writerows(out_rows)

    print(f"scoring variants: {len(scoring)}")
    print(f"present in VCF:   {present}")
    print(f"absent from VCF:  {len(scoring) - present}")
    print(f"wrote {out_csv}")


if __name__ == "__main__":
    main()