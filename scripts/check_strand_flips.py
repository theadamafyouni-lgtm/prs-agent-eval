#!/usr/bin/env python3
"""Detect and correct strand flips in a VCF against a PGS scoring model.

At each scoring position: keep the record if alleles already match,
correct REF/ALT to their partner letters if a partner-swap matches,
drop if neither. Palindromic (A/T, C/G) variants are kept as-is when
their alleles already match -- a hidden flip can't be detected from
the alleles alone, and same-strand provenance is assumed.

GT field is not touched on a corrected flip: the indices still point
to the same physical alleles, just relabeled to the partner letters.

usage: check_strand_flips.py input.vcf[.gz] scoring.txt.gz out.vcf
"""
import gzip, sys

MISSING = {"", "NA", "."}
PARTNER = {"A": "T", "T": "A", "C": "G", "G": "C"}


def open_any(path):
    p = str(path)
    return gzip.open(p, "rt") if p.endswith(".gz") else open(p, "rt")


def partner_swap(alleles):
    return frozenset(PARTNER.get(a, a) for a in alleles)


def load_scoring(scoring_file):
    out = {}
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
                continue
            ch, p, eff, oth = c[ci], c[pi], c[ei], c[oi]
            if any(v in MISSING for v in (ch, p, eff, oth)):
                continue
            out[(ch, p)] = frozenset({eff, oth})
    return out


def main():
    if len(sys.argv) != 4:
        sys.exit(f"usage: {sys.argv[0]} input.vcf[.gz] scoring.txt.gz out.vcf")
    in_vcf, scoring_file, out_vcf = sys.argv[1:4]

    scoring = load_scoring(scoring_file)
    exact = flipped = dropped = 0

    with open_any(in_vcf) as f_in, open(out_vcf, "w") as f_out:
        for line in f_in:
            if line.startswith("#"):
                f_out.write(line)
                continue
            cols = line.rstrip("\n").split("\t")
            if len(cols) < 5:
                continue
            ch, pos, ref, alt = cols[0].removeprefix("chr"), cols[1], cols[3], cols[4]
            scoring_set = scoring.get((ch, pos))
            if scoring_set is None:
                f_out.write(line if line.endswith("\n") else line + "\n")
                continue
            vcf_set = frozenset({ref, alt})
            if vcf_set == scoring_set:
                f_out.write(line if line.endswith("\n") else line + "\n")
                exact += 1
            elif partner_swap(vcf_set) == scoring_set:
                cols[3] = PARTNER.get(ref, ref)
                cols[4] = PARTNER.get(alt, alt)
                f_out.write("\t".join(cols) + "\n")
                flipped += 1
            else:
                dropped += 1

    print(f"exact match:           {exact}")
    print(f"strand flip corrected: {flipped}")
    print(f"dropped (no match):    {dropped}")
    print(f"wrote {out_vcf}")


if __name__ == "__main__":
    main()