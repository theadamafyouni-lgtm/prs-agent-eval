# PRS Computation Report

**Status:** STOPPED — build mismatch between patient VCF and scoring model. No PRS computed.

## Result
- **PRS value:** Not computed
- **Matched vs. required variants:** N/A (scoring not attempted)
- **Reason:** Patient VCF genome build (GRCh37) differs from scoring model build (GRCh38). Liftover is out of scope, so scoring cannot proceed.

## Build identification

**Identified patient build: GRCh37**, from the highest-authority header signal present.

Evidence (header fields inspected, in strict authority order):
- `##reference=file:///ref/human_g1k_v37.fasta` — **highest-authority signal present → GRCh37** (the 1000 Genomes `human_g1k_v37` / b37 reference). Per the spec, the highest-authority signal is taken and lower-authority signals are not consulted for the build decision.
- `##assembly=GRCh38` — lower authority; not used for the decision. (Noted: this conflicts with the reference signal.)
- `##contig` lengths — lowest authority; not used for the decision. Noted that they are GRCh37 lengths (e.g. `chr1=249250621`, the GRCh37 length; GRCh38 chr1 = 248956422), which agree with the `##reference=` signal and disagree with `##assembly=GRCh38`.

The header carries conflicting build signals, but they are at different authority levels, so the conflict is resolved by authority order (not treated as an equal-authority stop condition): `##reference=` (GRCh37) is authoritative.

## Scoring model build
- File: `PGS000577_hmPOS_GRCh38.txt.gz`
- Harmonized build: `#HmPOS_build=GRCh38` → scoring positions are **GRCh38**.

## Build match check
- Patient VCF build: **GRCh37**
- Scoring model build: **GRCh38**
- **Mismatch → do not score, stop.** Liftover is not in scope.

## Excluded-variant accounting
Not applicable — variant matching and scoring were not performed because of the build mismatch.
- Palindromic variants excluded: N/A
- Sex-chromosome (X/Y/MT) variants excluded: N/A
- Unrecovered required variants: N/A

## Coverage
Not applicable — scoring not attempted.
