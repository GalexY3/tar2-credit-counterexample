# Per-Agent Reward Redistribution Does Not Preserve the Optimal Team Policy

**Contents.** This archive contains a machine-checked counterexample to the policy-invariance guarantee of TAR² (Kapoor et al., arXiv:2502.04864v2), together with the code, preregistrations and results.

**Author.** Alejandro Panera Pascual (Universidad de Salamanca), ORCID 0009-0008-5194-7399.

**Scope.** TAR², its construction and its empirical results are the work of Kapoor, Tessera, Khadilkar, Baranwal, Peters, Albrecht and Sun. This archive examines only the stated optimal-policy-preservation guarantee.

## Contents

| Path | What it is |
|---|---|
| `paper/main.pdf`, `paper/main.tex` | The note |
| `lean/CreditAudit.lean` | Lean 4 + Mathlib proofs (Theorem 1 both directions, normalization properties, counterexample for every ε > 0) |
| `lean/LEAN_AXIOMS_AU01.txt` | `#print axioms` output: only `propext`, `Classical.choice`, `Quot.sound`; no `sorry` |
| `code/au01_core.py`, `code/au01_confirm.py`, `code/au01_pilot.py` | Exact counterexample, natural-score robustness sweep, gradient and tie checks (numpy/scipy) |
| `code/au02_repro.py`, `code/au02_analyze.py` | Reproduction with the authors' public credit model (requires their repository, see below) |
| `results/` | Frozen outputs: `au01_confirm.json`, `au02_repro.json`, `au02_analysis.json` and logs |
| `THIRD_PARTY_NOTICES.md` | Exact source, location and extent of the two quoted third-party excerpts |
| `provenance/` | Preregistrations and SHA-256 freezes written before each run (Spanish). AU01 commit c064b4c3; AU02 commits eeee447f and 3af67bb0 of the author's private research repository |

## Reproduce

### 1. Lean

The file imports only Mathlib. With the toolchain `leanprover/lean4:v4.36.0` and Mathlib for that version:

```
lake env lean CreditAudit.lean
```

The file ends with `#print axioms` for each declaration.

### 2. Counterexample and checks (AU01)

Python ≥ 3.10 with numpy and scipy:

```
python au01_confirm.py results/au01_confirm.json
```

The run is deterministic, with seed 20261125.

### 3. Reproduction with the authors' code (AU02)

- **Requirements:** Python with `torch` (CPU is enough) and `numpy`.
- **Get their code:** clone https://github.com/AdityaKapoor74/MARL_Agent_Temporal_Credit_Assignment at commit `883173c04df31c06530d92aace647a5d5e11f7a9`.
- **Licensing:** that repository carries no license, so it is not redistributed here. `au02_repro.py` imports the authors' `TARR_v2` module from the clone. It quotes, with attribution, the 20-line normalization block of their `MAPPO/agent.py` (branch `TAR^2_v2`, lines 651–671) and the 4-line helper `torch_nanmin` of `MAPPO/utils.py`, so that the redistribution can be checked line by line.

Then run:

```
python au02_repro.py <clone>/MAPPO results/au02_repro.json 20 2,4
python au02_analyze.py results/au02_repro.json results/au02_analysis.json
```

**Checksums.** The SHA-256 of the three original files used are listed in `provenance/FREEZE_AU02.txt`.

## Main numbers

**Counterexample.** The team optimum is not an equilibrium of the game induced by TAR², for every ε > 0. With exact policy gradient, TAR² rewards end at a suboptimal profile in 200/200 initializations; with the team reward, 93% reach the optimum.

**Authors' credit model, enabler–finisher task (T = 2):**
- the learned enabler share at the optimal trajectory is 0.000 in 20/20 seeds;
- the enabler abandons enabling in 20/20 seeds, against 0/20 with the team reward;
- the final team value is 0.41 against 0.99.

## License

- Text, figures and data: CC BY 4.0.
- Code written for this archive: MIT.
- Quoted excerpts of third-party code remain the property of their authors and are included only for verification.
