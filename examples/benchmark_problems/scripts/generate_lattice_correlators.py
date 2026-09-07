#!/usr/bin/env python3
"""
Generate the Lattice_Correlators benchmark problems.

Reproduces the plateau fit from the published Sp(4) three-antisymmetric-fermion
meson spectroscopy analysis and writes each fit out as a NIST-format
FitBenchmarking problem, with the full bootstrap covariance alongside.

Inputs (download from https://doi.org/10.5281/zenodo.13819562):
    correlators_wall.h5     (207 MB)
    ensemble_metadata.csv
    ensemble_data.csv       (only used to verify the extraction)

Point RAW_DIR at wherever those live, then run from the repository root:

    python examples/benchmark_problems/scripts/generate_lattice_correlators.py

The extraction mirrors, function for function, the upstream analysis code at
https://github.com/telos-collaboration/antisymmetric_analysis_2024 --
src/bootstrap.py, src/read_hdf5.py, src/mass.py, src/mass_wall.py,
src/extract.py, src/fitting.py -- and the flow_analysis submodule pinned at
7b1224c.  It is verified against the published masses in ensemble_data.csv.

reference_fit() additionally needs corrfitter and lsqfit.  It is used only to
record reference values in the *_meta.json files and to check the extraction.
"""

import hashlib
import json
import os
import re

import h5py
import numpy as np

RAW_DIR = "/tmp/antisym/raw"  # <- edit me
OUT = "examples/benchmark_problems/Lattice_Correlators"

# (ensemble, channel) pairs to ship.  Chosen to span three ensembles, both
# channels, both values of Nt and window lengths from 12 points down to 4.
PROBLEMS = [("ASB2M2", "v"), ("ASB1M4", "av"), ("ASB2M9", "av")]
CHANNEL_NAME = {"v": "vector", "av": "axial vector"}

H5 = f"{RAW_DIR}/correlators_wall.h5"
META = f"{RAW_DIR}/ensemble_metadata.csv"
import hashlib, re, json

BOOTSTRAP_SAMPLE_COUNT = 200

CHANNEL_TAGS = {"ps":["g5"], "v":["g1","g2","g3"], "t":["g0g1","g0g2","g0g3"],
                "av":["g5g1","g5g2","g5g3"], "at":["g0g5g1","g0g5g2","g0g5g3"], "s":["id"]}

def get_rng(name):                                    # src/bootstrap.py:17
    h = hashlib.md5(name.strip("/").encode("utf8")).digest()
    return np.random.default_rng(abs(int.from_bytes(h, "big")))

def sample_bootstrap_1d(values, rng):                 # flow_analysis @7b1224c
    values = np.asarray(values)
    idx = rng.integers(values.shape[0], size=(BOOTSTRAP_SAMPLE_COUNT, values.shape[0]))
    out = np.empty((BOOTSTRAP_SAMPLE_COUNT, values.shape[1]))
    for t in range(values.shape[1]):
        out[:, t] = values[idx, t].mean(axis=1)
    return out

def filter_configurations(ens, lo, hi, step):         # src/read_hdf5.py:36
    idx = np.asarray([int(re.match(".*n([0-9]+)$", f.decode()).groups()[0])
                      for f in ens["configurations"]])
    return (idx >= lo) & (idx <= hi) & ((idx - lo) % step == 0)

def fold(C):                                          # src/mass.py:145
    return (C + np.roll(np.flip(C, axis=1), 1, axis=1)) / 2

def get_ensemble(data, beta, mAS, Nt, Ns):            # src/read_hdf5.py
    out = []
    for name, ens in data.items():
        if (ens["lattice"][()] == [Nt, Ns, Ns, Ns]).all() \
           and ens["beta"][()] == beta and ens["quarkmasses"][()][0] == mAS:
            out.append(ens)
    return out

def extract(row, channel):
    """Returns (t, C_mean_folded, cov, samples) exactly as fit_cosh_bootstrap sees them."""
    data = h5py.File(H5, "r")
    (ens,) = get_ensemble(data, row.beta, row.mAS, int(row.Nt), int(row.Ns))
    keep = filter_configurations(ens, row.init_conf, row.final_conf, row.delta_conf_spectrum)

    bin_mean, bin_samples = [], []
    for tag in CHANNEL_TAGS[channel]:                 # src/mass_wall.py ch_extraction
        C = ens[f"TRIPLET/{tag}"][:, keep]
        s = sample_bootstrap_1d(C.T, get_rng(ens.name))
        bin_mean.append(C.T.mean(axis=0) * row.Ns**3)
        bin_samples.append(s * row.Ns**3)

    mean = np.zeros((1, int(row.Nt)))
    mean[0] = np.array(bin_mean).mean(axis=0)
    mean = fold(mean)
    samples = fold(np.array(bin_samples).mean(axis=0))
    cov = np.cov(samples.T)                           # src/fitting.py:168
    return mean[0], cov, samples, int(keep.sum())

def reference_fit(mean, cov, Nt, tmin, tmax):
    """Their exact fit: corrfitter Corr2 + lsqfit, infinite-width priors."""
    import corrfitter as cf, gvar as gv, lsqfit
    from scipy.optimize import curve_fit
    def func(t, a, M):
        return a*a*M*(np.exp(-M*t) + np.exp(-M*(Nt-t)))/2
    x0, _ = curve_fit(func, np.arange(tmin, tmax), mean[tmin:tmax])
    p0 = {"log(a)": np.array([np.log(abs(x0[0]))]), "log(dE)": np.array([np.log(x0[1])])}
    prior = gv.BufferDict()
    prior["log(a)"]  = gv.log(gv.gvar([0.1], [np.inf]))
    prior["log(dE)"] = gv.log(gv.gvar([0.1], [np.inf]))
    fitter = cf.CorrFitter(models=[cf.Corr2(datatag="Gab", tp=Nt, tmin=tmin, tmax=tmax,
                                            a="a", b="a", dE="dE")])
    fit = fitter.lsqfit(data={"Gab": gv.gvar(mean, cov)}, prior=prior, p0=p0)
    E = np.cumsum(fit.p["dE"])[0]
    return gv.mean(E), gv.sdev(E), gv.mean(fit.p["a"][0]), fit.chi2, fit.dof, fit.nit, x0





PROBLEM_TEMPLATE = """NIST-format problem file (not a NIST StRD dataset)
Lattice correlator fit, Sp(4) with three antisymmetric fermions

Dataset Name:  {stem}    ({stem}.dat)

File Format:   ASCII

Procedure:     Nonlinear Least Squares Regression

Description:   Zero-momentum {channel_name}-channel meson two-point
               correlation function from ensemble {ensemble} of the Sp(4) gauge
               theory with three antisymmetric Dirac fermions, measured with
               wall sources on a {Nt}x{Ns}^3 lattice.

               y is the folded, bootstrap-averaged correlator C(t) summed over
               the channel's gamma-matrix tags and scaled by Ns^3; x is the
               Euclidean time separation t in lattice units.  The fit window
               [{tmin}, {tmax}] is the published plateau range for this
               ensemble and channel.

               Extracting the ground-state mass E from the plateau is the
               inner loop of the published analysis: the fit below is repeated
               for each of 200 bootstrap samples plus the sample mean.

               Errors e are the square roots of the diagonal of the bootstrap
               covariance matrix.  The published analysis uses the FULL
               {npt}x{npt} covariance, which is supplied alongside this
               file as {stem}_cov.txt; fitting against the diagonal errors
               here is therefore an approximation to the published objective.

Reference:     Bennett et al., "Meson spectroscopy in the Sp(4) gauge theory
               with three antisymmetric fermions", arXiv:2412.01170.
               Data release: https://doi.org/10.5281/zenodo.13819562
               Analysis code: https://github.com/telos-collaboration/antisymmetric_analysis_2024

Data:          1 Response Variable  (y = correlator C(t))
               1 Predictor Variable (x = Euclidean time t)
               {npt} Observations

Model:         Periodic single-cosh, 2 Parameters (a and E)

               y = a**2 * (exp[-E*x] + exp[-E*({Nt}-x)])  +  e


          Starting values                  Certified Values

        Start 1     Start 2           Parameter     Standard Deviation
  a =   {a_cold:<11.6g} {a_warm:<17.9g} {a_ref:.10E}  {a_sdev:.10E}
  E =   {E_cold:<11.6g} {E_warm:<17.9g} {E_ref:.10E}  {dE_ref:.10E}

Residual Sum of Squares:                    {chi2_ref:.10E}
Degrees of Freedom:                                {dof_ref}
Number of Observations:                            {npt}


Data:   y               x               e
"""


def write_problems(extracted):
    """Write one NIST-format .dat, one covariance and one metadata file each."""
    os.makedirs(OUT, exist_ok=True)
    for (name, ch), d in extracted.items():
        Nt, tmin, tmax = d["Nt"], d["tmin"], d["tmax"]
        t = np.arange(tmin, tmax + 1)
        y = d["mean"][t]
        cov = d["cov"][np.ix_(t, t)]
        e = np.sqrt(np.diag(cov))
        stem = f"{name}_{ch}"

        # Start 1 is a deliberately uninformed cold start; Start 2 is the
        # scipy curve_fit warm start the published workflow actually uses.
        text = PROBLEM_TEMPLATE.format(
            stem=stem, ensemble=name, channel_name=CHANNEL_NAME[ch],
            Nt=Nt, Ns=d["Ns"], tmin=tmin, tmax=tmax, npt=len(t),
            a_cold=1.0, E_cold=0.5,
            a_warm=float(abs(d["p0_scipy"][0])), E_warm=float(d["p0_scipy"][1]),
            a_ref=d["a_ref"], a_sdev=0.0, E_ref=d["E_ref"], dE_ref=d["dE_ref"],
            chi2_ref=d["chi2_ref"], dof_ref=d["dof_ref"],
        )
        rows = "".join(
            f"  {yy: .12E}   {xx: .12E}   {ee: .12E}\n"
            for yy, xx, ee in zip(y, t.astype(float), e)
        )
        with open(f"{OUT}/{stem}.dat", "w") as f:
            f.write(text + rows)

        np.savetxt(
            f"{OUT}/{stem}_cov.txt", cov,
            header=f"Bootstrap covariance of C(t) for t = {tmin}..{tmax} "
                   f"({len(t)}x{len(t)}), ensemble {name}, channel {ch}",
        )
        with open(f"{OUT}/{stem}_meta.json", "w") as f:
            json.dump(
                dict(ensemble=name, channel=ch, Nt=Nt, Ns=d["Ns"],
                     tmin=tmin, tmax=tmax, n_bootstrap=200,
                     n_configurations=d["ncfg"],
                     reference_E=d["E_ref"],
                     reference_E_bootstrap_error=d["dE_ref"],
                     reference_a=d["a_ref"], lsqfit_chi2=d["chi2_ref"],
                     lsqfit_dof=d["dof_ref"]),
                f, indent=2,
            )
        print(f"wrote {stem}: {len(t)} pts, E_ref={d['E_ref']:.6f}")


if __name__ == "__main__":
    import pandas as pd

    meta_df = pd.read_csv(META)
    published = pd.read_csv(f"{RAW_DIR}/ensemble_data.csv").set_index("ensemble_name")

    extracted = {}
    for ens_name, channel in PROBLEMS:
        row = meta_df[meta_df.ensemble_name == ens_name].iloc[0]
        lo = int(row[f"{channel}_plateau_start"])
        hi = int(row[f"{channel}_plateau_end"])
        mean, cov, samples, ncfg = extract(row, channel)
        E, dE, a, chi2, dof, nit, x0 = reference_fit(mean, cov, int(row.Nt), lo, hi)
        want = published.loc[ens_name, f"{channel}_mass_value"]
        status = "OK      " if abs(E - want) < 5e-7 else "MISMATCH"
        print(f"{status} {ens_name:8s} {channel:3s} win=[{lo},{hi}] "
              f"E={E:.6f} published={want:.6f} chi2/dof={chi2 / dof:.3f}")
        extracted[(ens_name, channel)] = dict(
            mean=mean, cov=cov, Nt=int(row.Nt), Ns=int(row.Ns), tmin=lo,
            tmax=hi, ncfg=ncfg, E_ref=E, dE_ref=dE, a_ref=a,
            chi2_ref=chi2, dof_ref=int(dof), p0_scipy=x0)

    write_problems(extracted)
