# Lattice correlator plateau fits

Three two-point-correlator plateau fits from the published Sp(4) gauge theory
analysis (Bennett et al., [arXiv:2412.01170][paper]).

Each problem fits a periodic single-cosh `C(t) = a^2(exp(-E*t) + exp(-E*(Nt-t)))`
to the data over its published plateau window. `E` is the ground-state meson mass
(the fit target); `a` is the overlap amplitude.

* References: [Paper][paper] | [Code][code] | [Data][data]

## Data format and covariance

The published fit uses the **full covariance matrix**; these problems provide
diagonal errors (`data_e`) by default, so they minimise

```
sum_t ( (C(t) - model(t)) / e(t) )^2
```

instead of the published `r^T Cov^-1 r`. The full covariance is available as
`<problem>_cov.txt` and its Cholesky decomposition via the LSQfit parser, which
stores them in `problem.additional_info` for use by future cost functions.

Diagonal vs. published fits differ significantly:

| Problem | E (diagonal) | E (published) | Deviation |
|---|---|---|---|
| ASB2M2_v   | 0.782959 | 0.784306 | -0.65σ |
| ASB1M4_av  | 0.671085 | 0.703376 | -1.83σ |
| ASB2M9_v   | 0.342025 | 0.341631 | +0.19σ |

## Parser integration

Problems use `software = 'lsqfit'` to trigger `LSQfitParser`, which reads
`*_meta.json`, `*_cov.txt`, and extracts priors (when available) and covariance
data. All controllers (scipy, minuit, dfo, lsqfit) work with these problems;
non-lsqfit controllers simply ignore priors and use diagonal errors.

## Problems

| Problem | Ensemble | Channel | Nt x Ns³ | Window | Points | E (published) |
|---|---|---|---|---|---|---|
| ASB2M2_v   | ASB2M2 | vector       | 48×16³ | 13–24 | 12 | 0.784306 |
| ASB1M4_av  | ASB1M4 | axial vector | 48×24³ | 12–20 |  9 | 0.703376 |
| ASB2M9_v   | ASB2M9 | vector       | 54×32³ | 23–27 |  5 | 0.341631 |

Starting values from metadata (`reference_E` for `E`, `a=0.1`). To regenerate
with a different subset, edit `PROBLEMS` in
`examples/benchmark_problems/scripts/generate_lattice_correlators.py`.

[paper]: https://arxiv.org/abs/2412.01170
[code]: https://github.com/telos-collaboration/antisymmetric_analysis_2024
[data]: https://doi.org/10.5281/zenodo.13819562
