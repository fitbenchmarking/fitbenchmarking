# Lattice correlator plateau fits

Three two-point-correlator plateau fits taken from the published analysis of
the Sp(4) gauge theory with three antisymmetric Dirac fermions.

* Paper: Bennett et al., *Meson spectroscopy in the Sp(4) gauge theory with
  three antisymmetric fermions*, [arXiv:2412.01170][paper]
* Analysis code: [telos-collaboration/antisymmetric_analysis_2024][code]
* Data release: [10.5281/zenodo.13819562][data]

## The fit

Each problem fits a periodic single-cosh to a zero-momentum meson correlator
over its published plateau window:

```
C(t) = a^2 * ( exp(-E*t) + exp(-E*(Nt - t)) )
```

`E` is the ground-state meson mass in lattice units and is the quantity of
physical interest; `a` is the overlap amplitude. `Nt` is baked into each
problem file as a literal.

In the published workflow this fit is the inner loop of
`src/fitting.py:fit_cosh_bootstrap` — it runs once per bootstrap sample (200 of
them) plus once for the sample mean, for every ensemble and channel. The
minimiser is `lsqfit.nonlinear_fit` driven through `corrfitter.CorrFitter`.

## Provenance of the data

`x` is Euclidean time `t` in lattice units, restricted to the published
plateau window for that ensemble and channel.

`y` is the correlator: gauge configurations filtered to the published
trajectory range and step, bootstrap-resampled (200 samples, seeded from an
MD5 of the ensemble name), averaged over the channel's gamma-matrix tags,
scaled by `Ns^3`, and folded `t -> Nt - t`.

`e` is the square root of the diagonal of the bootstrap covariance.

The extraction reproduces the published masses in `ensemble_data.csv` on
Zenodo to all six published digits for all three problems, so the data here is
faithful to the paper.

## Important caveat: these are diagonal approximations

The published fit uses the **full covariance matrix** over the plateau window,
not just its diagonal. FitBenchmarking has no covariance support, so `data_e`
here carries only the diagonal and the shipped problems minimise

```
sum_t ( (C(t) - model(t)) / e(t) )^2
```

whereas the paper minimises `r^T Cov^-1 r`. These are not the same fit. The
full covariance for each problem is provided alongside as `<problem>_cov.txt`
so the correlated objective can be reconstructed.

How much it matters varies by problem. Fitting the diagonal objective with
`scipy.least_squares` recovers the published mass to within 0.5 bootstrap
sigma for the vector channel, but `ASB1M4_av` lands 1.8 sigma away.
Chi-squared values also come out far below the number of degrees of freedom
(e.g. 0.0095 for 10 dof on `ASB2M2_v`), which is the usual signature of
ignoring strong positive correlations between neighbouring timeslices.

Treat accuracy numbers from these problems as a comparison *between
minimisers on a common objective*, not as a reproduction of the paper.

## Starting values

* **Start 1** is a deliberately uninformed cold start (`a = 1`, `E = 0.5`).
* **Start 2** is the warm start the published workflow actually uses: a
  `scipy.optimize.curve_fit` pass over the plateau window
  (`src/fitting.py:154`). Note that the published warm start uses
  `np.arange(plateau_start, plateau_end)`, which is exclusive of the last
  point, while the corrfitter window that follows is inclusive — so the warm
  start sees one fewer point than the fit does. That is reproduced here.

## Reference values

`<problem>_meta.json` records, for each problem, the ensemble parameters, the
plateau window, and the published mass together with its bootstrap error and
the chi-squared and dof that lsqfit reports.

One caveat on the reported chi-squared. `corrfitter.Corr2.builddata` combines
the data at `t` and `Nt - t` with `lsqfit.wavg`, but this pipeline has already
folded the correlator, so the two inputs to that weighted average are the
identical random variable. That is a degenerate correlated average, and the
SVD regularisation lsqfit applies to it shifts the reported chi-squared by
about 0.2% relative to a direct correlated chi-squared on the same data
(7.8723 vs 7.8859 for `ASB2M2_v`). The fitted mass moves by only 3e-5
relative, far inside the bootstrap error, so this does not affect the physics
— but it does mean lsqfit's reported chi-squared is not an exactly
reproducible target and should not be used as the accuracy metric.

## Problems

| Problem | Ensemble | Channel | Nt x Ns^3 | Window | Points | Published E |
|---|---|---|---|---|---|---|
| ASB2M2_v   | ASB2M2 | vector       | 48x16^3 | 13-24 | 12 | 0.784306 |
| ASB1M4_av  | ASB1M4 | axial vector | 48x24^3 | 12-20 |  9 | 0.703376 |
| ASB2M9_av  | ASB2M9 | axial vector | 54x32^3 | 14-17 |  4 | 0.502071 |

These three are a subset of the eight ensemble/channel combinations the
published analysis fits, chosen to span three ensembles, both channels, both
lattice time extents and a wide range of window lengths. `ASB2M9_av` has a
very short window (4 points for a 2-parameter model) and is correspondingly
harder and less well constrained than `ASB2M2_v`. To regenerate a different
subset, edit `PROBLEMS` in
`examples/benchmark_problems/scripts/generate_lattice_correlators.py`.

[paper]: https://arxiv.org/abs/2412.01170
[code]: https://github.com/telos-collaboration/antisymmetric_analysis_2024
[data]: https://doi.org/10.5281/zenodo.13819562
