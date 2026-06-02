# verify_match.py

Independent verification that a VCF's records match a scoring model — reports PASS/FAIL based on allele mismatches and shows which scoring variants are absent from the VCF.

## Usage

```bash
python3 verify_match.py input.vcf.gz scoring.txt.gz
```

## Inputs

- VCF to verify
- Scoring file to verify against

## Outputs

- Diagnostic report printed to stdout (no file output)

## What it prints

- PASS / FAIL based on whether any present records have allele mismatches
- Number of records checked
- Number of mismatches found
- Scoring variants absent from the VCF, broken down by chromosome

## Notes

- PASS means **correctness**, not **completeness** — it confirms that the records you have are correctly matched; it does *not* require every scoring variant to be present
- Absent variants are reported separately so you can interpret what's expected for the test (e.g. 6 chrX absent is expected if your WGS has no chrX; 0 absent is expected if you're checking a fully imputed output)
- Independent of how the input VCF was built — useful as a final sanity check on `source/`, an imputed output, or anything else