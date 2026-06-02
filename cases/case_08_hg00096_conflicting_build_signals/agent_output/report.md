# PRS Structured Report — case_08_hg00096_conflicting_build_signals

## Result: STOPPED — imputation tool failure (no PRS produced)

The run was halted at the imputation/remediation step because `imputation.py`
exited with a non-zero status. Per AGENT_SPEC.md (§Variant enumeration &
imputation), a non-zero exit code / error output from `imputation.py` is a hard
stop condition: the exit code and error output are reported and the run stops.
No retry, no input modification, no fabricated or partial score.

---

## Inputs

- Patient VCF: `cases/case_08_hg00096_conflicting_build_signals/input/HG00096_chr2_grch37data_ref38.vcf.gz`
- Scoring model: `scoring_models/PGS000577/PGS000577_hmPOS_GRCh38.txt.gz` (PGS_ID: **PGS000577**)

## PRS value

- **Not computed.** Scoring (`pgsc_calc`) was never invoked because the
  prerequisite imputation step failed.

## Identified build and evidence

- **Patient VCF build: GRCh38**, identified from the highest-authority header
  signal in strict authority order (`##reference=` > `##assembly=` > contig lengths):
  - `##reference=GRCh38_full_analysis_set_plus_decoy_hla.fa` → GRCh38.
- Per spec, lower-authority signals are consulted only when all higher-authority
  signals are absent; since `##reference=` is present, the contig-length signals
  were **not** used for the build decision. (For transparency only: the
  `##contig` length entries carry `assembly=b37` and GRCh37 lengths, e.g.
  `2=243199373`. The cross-authority-level disagreement is resolved by the
  authority order in favor of `##reference=`; the spec's conflict-stop rule
  applies only to disagreement among signals of *equal* authority, which is not
  the case here.)
- Scoring model build: GRCh38 (`#HmPOS_build=GRCh38`; harmonized `hm_pos`
  coordinates used). **Patient build (GRCh38) matches the scoring-model build —
  no build mismatch; scoring was not blocked on build grounds.**

## Matched vs. required variant count (pre-imputation)

- Required variants in model: **117 total**
  - Sex-chromosome (chrX) required variants excluded from scoring: **6**
  - Autosomal (chr1–22) required variants (denominator): **111**
  - Palindromic among autosomal required variants (A/T, T/A, G/C, C/G; excluded
    from the matched numerator): **9**
  - Non-palindromic autosomal required variants: **102**
- Patient VCF contains records on **chr2 only** (7,081,952 records). Of the 111
  autosomal required variants, 99 lie on chromosomes absent from the patient VCF
  and 12 lie on chr2; at the GRCh38 harmonized positions almost none of the chr2
  required variants are present. The large number of missing required variants
  triggered the mandatory imputation step.
- A final matched count is **unavailable** because remediation (imputation) and
  scoring did not complete.

## Coverage

- **Not evaluable.** Coverage (non-palindromic matched autosomal ÷ total
  autosomal required, threshold 90%) cannot be computed without a completed,
  scored VCF. No PRS is returned.

## Excluded-from-scoring summary

- Sex-chromosome (X/Y/MT) variants excluded: **6** (all chrX).
- Palindromic variants excluded from numerator: **9**.

## Unrecovered variants / failure detail

All required variants remained unrecovered because the imputation tool failed
before producing a completed VCF.

- Tool invoked: `python3 scripts/imputation.py <patient_vcf> <scoring_file> <output_vcf>`
  (output path ended in `.vcf.gz`, three positional args, no flags, no
  reference/panel argument — exactly as specified).
- **Exit code: 1**
- Error output (key lines):
  ```
  Error encountered while parsing the input at 1:150685811
  Cleaning
  Traceback (most recent call last):
    File ".../scripts/imputation.py", line 76, in <module>
      subprocess.run(["bcftools", "sort", merged, "-Oz", "-o", out_gz], check=True)
  subprocess.CalledProcessError: Command '['bcftools', 'sort', '<tmp>.vcf', '-Oz',
    '-o', '...HG00096_imputed.vcf.gz']' returned non-zero exit status 255
  ```
  (Preceded by numerous `INFO ... is not defined in the header` parse warnings.)
- No completed VCF was produced. Per spec, the tool's failure is reported and the
  run stops; the agent does not categorize the cause, retry, or modify inputs.

## Disposition

Stopped at the imputation step. No PRS reported (correctly — partial/fabricated
scores are not permitted). Resolution of the `imputation.py` failure is outside
the scope of this run.
