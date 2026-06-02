# build_prs_worksheet.py

Joins a patient VCF against a scoring model into a flat CSV — one row per scoring variant — so you can compute a PRS by hand in a spreadsheet. Computes nothing itself: the dosage and contribution columns are yours to add.

## Usage

```bash
python3 build_prs_worksheet.py sample.vcf[.gz] scoring.txt.gz out.csv
```

## Inputs

- Patient VCF (`.vcf` or `.vcf.gz`)
- Scoring file (`.txt.gz`)
- Output path (`.csv`)

## Outputs

- A CSV with one row per scoring variant. Columns:
  - `chrom`, `pos`, `effect_allele`, `other_allele`, `effect_weight`, `rsID` — the scoring model side
  - `vcf_ref`, `vcf_alt`, `vcf_gt`, `status` — the patient side (`status` is `present` or `ABSENT`)
- Sorted by chromosome (numeric first, then X) then position
- Imports straight into Google Sheets / Excel via File → Import

## What it prints

- Total scoring variants
- Number present in the VCF
- Number absent from the VCF

## Notes — how to compute the PRS from this file

- `PRS = Σ (dosage × effect_weight)` across present rows with a defined dosage
- **Dosage** = number of copies of `effect_allele` the patient carries, from `vcf_gt`:
  - Count the number of `1`s in the GT (call it `n1`)
  - If `effect_allele == vcf_alt` → dosage = `n1`
  - If `effect_allele == vcf_ref` → dosage = `2 − n1`
  - If GT contains `.` (no-call) → exclude the row
- **Contribution** = `dosage × effect_weight`
- **PRS** = `SUM` of the contribution column

## Other notes

- For PGS000577, weights are log odds ratios — the sum is on the log-odds scale and matches pgsc_calc's `SUM` column
- `rsID` will be `.` for many PGS000577 variants (known quirk of the `hm_rsID` column)
- `ABSENT` rows are kept in the output for visibility — they don't enter the sum, but you can see exactly which scoring variants are missing
- The non-VCF-side columns (1–6) are the full scoring model in GRCh38, so this file doubles as a model-inspection view