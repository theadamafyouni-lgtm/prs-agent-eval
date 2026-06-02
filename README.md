# genome-ai-prs

Evaluation framework for an LLM agent running polygenic risk score (PRS) calculations via `pgsc_calc`. Each case is a real (input, expected output) pair that tests whether the agent makes the right judgments and produces correct PRS values on realistic genetic data.

## Why this exists

PRS calculation involves dozens of small judgment calls — which genome build is the data in, how to handle missing variants, whether the scoring model matches the patient's build, what coverage threshold is enough. This framework checks that the agent makes those judgments correctly by running it against cases where the right answer is known from independent `pgsc_calc` runs.

## Core principle

The agent makes all interpretation decisions. Tools and scripts perform only mechanical data extraction. For example, build detection works by having the agent read VCF headers with `bcftools` and reason about which genome build the data is from — there is no hardcoded `detect_build.py`. The agent's reasoning is what's being tested.

## Layout
genome-ai-prs/
├── README.md                    # this file: how to navigate the framework
├── AGENT_SPEC.md                # canonical rules the agent must follow (V10, 42 rules)
├── CLAUDE.md                    # Claude Code pointer: read AGENT_SPEC.md
├── V11_TODO.md                  # in-progress spec items for next version
├── scoring_models/              # PGS Catalog scoring files, shared across cases
├── scripts/                     # helper scripts (imputation.py, etc.)
└── cases/                       # all test cases live here
├── case_01_hg00096_missing_data/
├── case_02_hg00096_build_mismatch/
├── case_03_hg00096_ambiguous_build/
├── case_04_hg00096_t2d_full_coverage/
├── case_06_hg00096_low_coverage_refusal/
├── case_07_hg00096_invalid_alleles/
├── case_08_hg00096_conflicting_build_signals/
└── case_09_hg00096_unsorted_unindexed/

## Per-case structure

Each case folder contains:

- `input/` — the patient VCF the agent receives
- `expected_output/` — gold-standard reference from an independent `pgsc_calc` run on the same input
- `agent_output/` — what the agent produced when run on this case
- `build_fixture.py` — how the input was constructed (reproducibility)
- `command.txt` — the prompt the agent was given
- `results.md` — what was tested and pass/fail verdict

## Running a case

From this directory, open Claude Code and paste the prompt from the case's `command.txt`.

Example, for `case_04_hg00096_t2d_full_coverage`:
Compute the PRS for the patient VCF at
cases/case_04_hg00096_t2d_full_coverage/input/HG00096_PGS000330.vcf.gz
using the scoring model at
scoring_models/PGS000330/PGS000330_hmPOS_GRCh38.txt.gz.
Write your structured report to
cases/case_04_hg00096_t2d_full_coverage/agent_output/.

Claude Code reads `CLAUDE.md` at session start, which points at `AGENT_SPEC.md`. The rules are loaded automatically.

## Adding a new case
mkdir -p cases/case_NN_concept/{input,expected_output,agent_output}

Then:

1. Write `build_fixture.py` capturing how the input is constructed.
2. Run it to generate `input/`.
3. Compute the expected PRS independently (typically a direct `pgsc_calc` run).
4. Record the expected values and behaviors in `expected_output/expected_output.md`.
5. Write `command.txt` with the agent prompt.
6. Run the agent.
7. Compare its output against expected and fill in `results.md`.

## Current status

Closed (passing):
- `case_01_hg00096_missing_data` — HG00096 + PGS000577 (GRCh38), missing variants imputed. **Passed.** PRS SUM 8.96587.
- `case_02_hg00096_build_mismatch` — GRCh37 / GRCh38 build mismatch refusal. **Passed.**
- `case_03_hg00096_ambiguous_build` — Stripped-header refusal. **Passed.**
- `case_04_hg00096_t2d_full_coverage` — HG00096 + PGS000330 (T2D, 6.4M variants), end-to-end on a large scoring model. **Passed.** PRS SUM -0.338387.
- `case_06_hg00096_low_coverage_refusal` — coverage gate, failing direction (synthetic model, 101/151 = 66.9% covered). **Passed** (refused, no PRS).

Findings (ran, exposed a gap — drives V11):
- `case_08_hg00096_conflicting_build_signals` — GRCh37 data and contigs with a lying `##reference=GRCh38`. **Finding.** The agent trusted the false `##reference`, read the position mismatch as missing variants rather than a wrong build, and routed to imputation (which then crashed, so no wrong PRS was returned — by luck, not detection). The data-position-vs-declared-build check needs to become a refusal trigger.
- `case_09_hg00096_unsorted_unindexed` — operational transforms (sort/bgzip/index). **Invalid as written.** The operational corruption was absorbed by the standard imputation step before input repair was ever forced; motivated requiring a canonical input state (sort/bgzip/index) before any tool runs (V11 #8).

In progress:
- `case_07_hg00096_invalid_alleles` — invalid (non-ACGT) alleles in ~20% of records. Exploratory run to observe how the agent handles them before writing V11 rule #6.

Planned:
- `case_05_model_selection_by_ancestry` — agent picks the right scoring model when multiple are available for the same trait.

## AGENT_SPEC.md vs README.md vs CLAUDE.md

- **AGENT_SPEC.md** — the rules the agent must follow when calculating PRS. Source of truth for agent behavior. Should not be modified during an eval run.
- **README.md** — this file. How a human navigates the framework, runs cases, and adds new ones.
- **CLAUDE.md** — minimal pointer file so Claude Code automatically reads AGENT_SPEC.md at session start.

## Methodology reference

Cases are grounded in QC principles from Choi, Mak, O'Reilly (2018), "A guide to performing Polygenic Risk Score analyses" (bioRxiv 416545) — particularly the requirements around genome build matching, variant matching, ambiguous SNP handling, and treatment of missing data.