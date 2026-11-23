# Third-party notices

`code/au02_repro.py` quotes two short excerpts of third-party code. They are quoted for scholarly analysis and criticism: they let a reader check line by line that the reward redistribution audited in the accompanying note is the one implemented by the authors.

**Source.** Aditya Kapoor (2024), *MARL_Agent_Temporal_Credit_Assignment*, https://github.com/AdityaKapoor74/MARL_Agent_Temporal_Credit_Assignment, commit `883173c04df31c06530d92aace647a5d5e11f7a9`, dated 16 October 2024. This is the code accompanying Kapoor et al., arXiv:2412.14779 and arXiv:2502.04864.

**License.** The repository carries no license. The excerpts remain the property of their authors and are not relicensed by this archive: the MIT license in `LICENSE` covers only the code written for this archive.

| Excerpt in `code/au02_repro.py` | Original location | Extent |
|---|---|---|
| Function `torch_nanmin` (lines 45–47) | `MAPPO/utils.py`, lines 15–18 | 4 lines |
| Body of `redistribute` (lines 107–118): min-shift normalization of temporal and agent weights | `MAPPO/agent.py`, method `reward_model_output`, branch `TAR^2_v2`, lines 651–671 (of 1139) | about 20 lines, with variable names kept and diagnostic `print` calls omitted |

**What is not included.** No other file of that repository is redistributed. The reward model (`MAPPO/TARR_v2/TARR_v2.py`, `MAPPO/TARR_v2/modules.py`) is imported at run time from a local clone; see `README.md`. The SHA-256 of the three original files used are recorded in `provenance/FREEZE_AU02.txt`.
