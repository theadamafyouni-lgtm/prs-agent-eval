#V10 Agent Specs

##Scope & inputs

Compute a valid PRS for one patient given a patient VCF and a scoring model. Nothing else is in scope.
The scoring model is authoritative on which variants are required and how they are weighted. Do not add to its variant set, substitute alternatives, or override its weights.
Operate only on the patient VCF and the scoring model. No reference panel, population dataset, or external genotype source exists; never request or assume one.
If any required file (patient VCF, scoring model, or tool output) is missing, unreadable, or malformed, report it and stop. Do not proceed on partial inputs. Missing variants inside the patient VCF are handled by the remediation workflow, not as a missing-input condition.
Never read, reference, or rely on any ground-truth, expected-output, or answer file, even if present or discoverable on disk.
Access only the supplied patient VCF, the supplied scoring model, the outputs of tools invoked during this run, and temporary files created during this run. All other files on disk are out of scope.

##Build identification

Before scoring, identify the patient VCF's genome build by reading its header with bcftools view -h <patient_vcf>. Only the header is consulted; do not scan records.
Use header fields as build signals in strict authority order: ##reference= first, then ##assembly=, then ##contig=<ID=...,length=...> entries compared against canonical chromosome lengths. Take the highest-authority signal present and stop. Lower-authority signals are consulted only when all higher-authority signals are absent. If signals of equal authority disagree — for example, contig lengths inconsistent with each other — do not score. Report the conflict and stop.
Recognized builds are GRCh37 (hg19) and GRCh38 (hg38). If the inspected fields do not resolve unambiguously to one of these, do not score. Report which fields were inspected and what was found.

##Scoring model match

If the patient VCF and scoring model are on different genome builds (e.g. GRCh37 vs GRCh38), do not score. Report the mismatch and stop. Liftover is not in scope.

##Variant enumeration & imputation

Before scoring, enumerate the variants the model requires and compare against the variants present in the patient VCF.
Exclude all variants on chromosomes X, Y, and MT from the required-variant set before matching. The PRS is computed over autosomal variants (chr1–22) only, following standard practice for autosomal PRS (Choi, Mak, O'Reilly 2018). Sex-chromosome variants are not scored, not imputed, and not counted toward coverage in either the numerator or denominator.
Identify palindromic variants among the required variants: those whose effect/non-effect alleles form a complementary pair (A/T, T/A, G/C, C/G). Strand cannot be inferred for these without external frequency data, so they cannot be matched unambiguously. Exclude palindromic variants from the matched count, and do not pass them to imputation.
If patient alleles match the scoring model only after strand complementation (e.g. scoring G/A, patient C/T), invoke the strand-correction step before scoring. Do not drop those variants or correct them by hand. Variants whose alleles cannot be reconciled through strand complementation are unrecoverable: do not coerce them into a match, and do not pass them to imputation.
If all required variants are already present and matching, score directly. Do not run imputation unnecessarily.
If any required variants are missing, invoke the imputation.py tool before scoring. Never score a VCF that still has required variants missing.
Never silently drop missing required variants and score the remainder. Missing required variants are a remediation condition, not something to ignore.
Never fabricate, guess, or hand-fill genotypes. Missing variants are recovered only through the imputation tool.
Treat the imputation tool as a black box: pass the VCF and scoring model, receive a completed VCF in return. Do not read, open, or view the tool's source files at any time, for any purpose, including diagnosing errors or troubleshooting invocation. Do not reimplement or reason about its internals. The tool's behavior is observable only through its inputs, outputs, and exit codes.
Never supply, request, or improvise a reference/panel argument to any tool. Invoke tools only with the inputs received.
Do not post-process or modify the imputation tool's output. Operational transformations required for downstream tool compatibility (e.g., bgzip compression, indexing, sorting) are permitted, provided they do not alter variant or genotype content. Any merging or normalization remains the tool's responsibility.
Do not change the biological meaning of the patient's existing genotype calls. Representation-level transforms by tools (bi-allelic splitting, strand correction) are fine; rewriting which alleles the patient carries is not.
After imputation, verify the completed VCF before scoring. Do not assume the tool succeeded without checking its output.
Any non-zero exit code, error output, or malformed output from imputation.py is a stop condition. The agent does not categorize tool errors by perceived cause — for example, distinguishing "invocation issues" from "real tool failures" is not in scope. Report the tool's exit code and error output, then stop. Do not retry with a different invocation. Do not modify inputs and re-run. Do not proceed past the error.

##Scoring invocation

Run pgsc_calc only on the completed post-remediation VCF, never on the raw or unremediated input.
Invoke pgsc_calc with the project's configured parameters (minimum overlap, target build). Do not override or substitute them.
Do not compute or estimate the PRS yourself. pgsc_calc is the only scoring engine.
When invoking pgsc_calc, pass --target_build GRCh37 or --target_build GRCh38 matching the identified build. Never invoke pgsc_calc without an explicit build.
Any non-zero exit code, error output, or pipeline failure from pgsc_calc is a stop condition. Report the failure. Do not retry, do not fabricate a number, do not estimate, do not attempt alternative scoring approaches.

##Reporting

Always report the PRS together with the matched-versus-required variant count. Never report the score in isolation.
List (or summarize by category) the required variants that could not be recovered, and why. Do not present a partial score as if it were complete.
Coverage is defined as non-palindromic matched autosomal variants divided by total required autosomal variants. Sex-chromosome (X, Y, MT) variants are excluded from both numerator and denominator. Palindromic variants are excluded from the numerator only; the denominator retains all autosomal required variants. The 90% threshold applies to this coverage value.
If coverage (as defined above) is below 90% after remediation, do not return a PRS. Report the actual coverage, the configured threshold, and the unrecovered variants. A partial score below threshold is not a valid result.
Produce one structured report: the PRS value, the matched-versus-required variant count, and a list (or category breakdown) of variants that could not be recovered. The format is fixed.
The report must additionally include the count of palindromic variants and the count of sex-chromosome variants excluded from scoring.
The structured report must include the identified build and the evidence used to identify it. e.g., "GRCh38 identified from contig lengths: chr1=248956422".

##Invocation reference

Project tools live in scripts/. Reference them by filename (e.g., scripts/imputation.py).
Invoke imputation.py as: python3 scripts/imputation.py <corrupted_vcf> <scoring_file> <output_vcf>. Three positional arguments, no flags. The output_vcf path must end in .vcf.gz.
Invoke pgsc_calc as: nextflow run pgscatalog/pgsc_calc -profile docker -c /root/pgs_project/pgsc_config.config --input <samplesheet> --target_build <build> --pgs_id <PGS_ID> --min_overlap 0.0001 --outdir <output_dir>.
The pgsc_calc samplesheet is a CSV with header sampleset,path_prefix,chrom,format. For a multi-chromosome VCF, use one row with path_prefix as the file's path stripped of the .vcf.gz extension, chrom empty, and format set to vcf.
Derive PGS_ID from the scoring filename. PGS000577_hmPOS_GRCh38.txt.gz becomes PGS000577.
pgsc_calc writes output to <output_dir>/score/.
