# Lattice correlator plateau fits

Three two-point-correlator plateau fits from the published Sp(4) gauge theory
analysis (Bennett et al., [arXiv:2412.01170][paper]).

Each problem fits a periodic single-cosh model to the data over its published
plateau window: `C(t) = a²(exp(-E*t) + exp(-E*(Nt-t)))`.

## Problems

| Problem | Nt x Ns³ | Points | E (published) |
|---|---|---|---|
| ASB2M2_v   | 48×16³ | 12 | 0.784306 |
| ASB1M4_av  | 48×24³ |  9 | 0.703376 |
| ASB2M9_av  | 54×32³ |  4 | 0.502071 |

The published analysis uses the full covariance matrix. These problems include
full covariance matrices in `*_cov.txt` files, which are automatically loaded
by the lsqfit parser into `problem.additional_info['covariance']`. This allows
the `whitened_nlls` cost function to reproduce the correlated fit from the paper.

[paper]: https://arxiv.org/abs/2412.01170
[code]: https://github.com/telos-collaboration/antisymmetric_analysis_2024
[data]: https://doi.org/10.5281/zenodo.13819562
