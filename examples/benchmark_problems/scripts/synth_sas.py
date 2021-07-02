"""This script is used to generate synthetic data representative of
neutron or x-ray small angle scattering (SAS) experiments by taking
models from SASView (sasmodels) and adding noise whose character is
determined by analysing real experimental datasets. These datasets
are in two folders, namely "example_sasmodel",
"experimental_xray_sas" and "experimental_neutron_sas" which must
both be accesible when running this script.

To see examples of the synthesis process, run the:

'example_xray_synth()' or 'example_neutron_synth()' functions

The main function is to be called as follows:

python -m sasmodel_data_synthesis.py -f <folder_path> -s <synth_style>

where the folder path directs to a folder in which some space delimited
.txt files, as output from sasview, are stored in a sub-folder called
'data_files'. All of the 'model' datasets in this location will have
synthetic datasets generated for them, also stored in the 'data_files'
subfolder. The synth style argument is used to declare whether to
generate the synthetic data in the x-ray, or neutron style, or both.
A PNG figure is generated with each synthetic dataset and placed in
'data_files' subdirectory so that users can visualise how the sasmodel
compares to the synthetic datasets.

This script also generates the accompanying problem definition files
and META file; all of which are placed directly in <folder_path> the
parent of the 'data_files' subdirectoy.

"""
import os
import time
import re
import argparse
import numpy as np
from numpy.random import default_rng

from scipy.optimize import curve_fit
import h5py
import matplotlib.pyplot as plt


parser = argparse.ArgumentParser()
parser.add_argument(
    "-f",
    "--folder",
    help="The folder containing the sasmodels"
    " from which to synthesise data")
parser.add_argument(
    "-s",
    "--synthtype",
    help="The classification of noise to" +
    " add to the data")
args = parser.parse_args()


def file_names(pathname):
    """Obtain all filenames in directory."""
    fnames = []
    for file in os.listdir(pathname):
        fnames.append(file)
    return fnames


def read_xray_data(pfolder, fname):
    """Read experimental data from a tab delimited file.

    Inputs: pfolder - string of folder path
            fname - string of filename of sasmodel data

    Outputs: x_vals - 1d np array of x values
             y_vals - 1d array of y values
             ydev_vals - 1d np array of y uncertainty values
    """
    data_array = np.loadtxt(pfolder + "\\" + fname, delimiter="\t")
    y_ids = data_array[:, 1] > 0  # filter out negative intensities
    x_vals = data_array[y_ids, 0]
    y_vals = data_array[y_ids, 1]
    ydev_vals = data_array[y_ids, 2]
    return x_vals, y_vals, ydev_vals


def read_neutron_data(pfolder, fname):
    """Read experimental neutron from a .h file.

    Inputs: pfolder - string of folder path
            fname - string of filename of sasmodel data

    Outputs: x_vals - 1d np array of x values
             y_vals - 1d array of y values
             ydev_vals - 1d np array of y uncertainty values
    """
    with h5py.File(pfolder + "\\" + fname, 'r') as file:
        datasetnames = list(file.keys())
        itemnames = list(file[datasetnames[0]].keys())
        datanames = list(file[datasetnames[0]][itemnames[2]].keys())
        # data are on the third layer of these .h5 files
        x_vals = np.array(file[datasetnames[0]][itemnames[2]][datanames[2]])
        y_vals = np.array(file[datasetnames[0]][itemnames[2]][datanames[0]])
        ydev_vals = np.array(file[datasetnames[0]][itemnames[2]][datanames[1]])
    return x_vals, y_vals, ydev_vals


def read_sasmodel_data(pfolder, fname):
    """Read sasmodel data from a 'double space' delimited txt file; the default
    format that is outputted by SASView.

    Inputs: pfolder - string of folder path
            fname - string of filename of sasmodel data

    Outputs: x_vals - 1d np array of x values
             y_vals - 1d array of y values
    """
    data_array = np.loadtxt(pfolder + "\\" + fname, delimiter="  ", skiprows=1)
    x_vals = data_array[:, 0]
    y_vals = data_array[:, 1]
    return x_vals, y_vals


def normalise_data(vals):
    """Normalise np array columnwise.

    Inputs: vals - 1d np array to be normalised

    Outputs: norm_vals - 1d np array
             norm_pars - 2 element list with max and min values
    """

    vals_max = max(vals)
    vals_min = min(vals)
    norm_pars = [vals_min, vals_max]

    norm_vals = (vals - norm_pars[0])/(norm_pars[1] - norm_pars[0])
    norm_vals[norm_vals == 0] = 1e-7

    return norm_vals, norm_pars


def denormalise_data(norm_vals, norm_pars):
    """Normalise np array columnwise.

    Inputs: vals - 1d np array to be normalised

    Outputs: norm_vals - 1d np array
             norm_pars - 2 element list with max and min values
    """

    vals = norm_pars[0] + norm_vals*(norm_pars[1]-norm_pars[0])

    return vals


def gaussian(y_vals, n_sigma):
    """Noise on intensity is sampled from a Gaussian distribution
    for each datum. The standard deviation used to sample noise
    for each datum is equal to the intensity of the datum multiplied
    by a chosen scaling factor.

    Inputs: y_vals - 1D numpy array of intensities
            n_sigma - std scaling factor
    Outputs: y_noise - 1D numpy array of intensities with noise
                            included
             noise - 1D numpy array of noise
    """
    y_noise = []
    noise = []
    rng = default_rng()
    for y_val in y_vals:
        noise_temp = rng.normal(loc=0.0, scale=n_sigma * y_val)
        noise.append(noise_temp)
        y_noise.append(noise_temp + y_val)
    y_noise = np.array(y_noise)
    return y_noise, noise


def poissonian(y_vals, **kwargs):
    """Noise on intensity is sampled from a Poissonian distribution
    for each datum. The poisson parameter 'lambda' for each datum
    is equal to the intensity of the datum.

    Inputs: y_vals - 1D numpy array of intensities

    Optional Keyword Inputs:
            count_scale - intensity scaling factor
            count_shift - intensity shift constant

    Outputs: y_noise - 1D numpy array of intensities with noise
                            included
             noise - 1D numpy array of noise
    """
    if 'count_scale' in kwargs:
        count_scale = kwargs.get('count_scale', 'None')
    else:
        count_scale = 1

    if 'count_shift' in kwargs:
        count_shift = kwargs.get('count_shift', 'None')
    else:
        count_shift = 0

    y_noise = []
    rng = default_rng()
    for item in y_vals:
        # samples from the Poisson distribution are the sythetic data,
        # unlike signal + Guassian noise
        if item * count_scale <= 0:
            item = 1
        y_noise.append(rng.poisson(item * count_scale + count_shift))
    y_noise = np.array(y_noise)
    y_vals = y_vals * count_scale + count_shift
    noise = y_noise - y_vals  # not strictly applicable to Poisson
    # noise[noise<0] = abs(noise[noise<0])
    return y_vals, y_noise, noise


def powerlaw(x, a, b, c):
    """Powerlaw function used by fitting software to characterise uncertainty."""
    return a * x**b + c


def errorbar_xy(x_vals, y_vals, ydev_vals, **kwargs):
    """ Plotting I vs Q with uncertainty in y errorbars.

    Inputs: x_vals - 1D np array of Q values
            y_vals - 1D np array of intensity values
            ydev_vals - 1D np array of uncertainty

    Optional Inputs:
            title - str defining figure title
            xunits - str defining x units
            yunits - str defining yunits

    Outputs: plt - plot handle
    """

    if "title" in kwargs:
        tit = kwargs.get("title", "None")
    else:
        tit = ""

    if 'xunits' in kwargs:
        xunits = kwargs.get("xunits", "None")
    else:
        xunits = ""

    if 'yunits' in kwargs:
        yunits = kwargs.get("yunits", "None")
    else:
        yunits = ""

    plt.plot(x_vals, y_vals)
    plt.errorbar(x_vals, y_vals, yerr=ydev_vals,
                 fmt="None", color="orange")
    plt.legend(["Data", "Uncertainty"])
    plt.xscale("log", nonpositive='clip')
    plt.yscale("log", nonpositive='clip')
    plt.xlabel("X " + xunits)
    plt.ylabel("Y " + yunits)
    plt.title(tit)

    return plt


def power_fit(x_vals, y_vals):
    """ Perform powerlaw fit using the scipy optimize library.
    """
    pars, conv = curve_fit(f=powerlaw, xdata=x_vals, ydata=y_vals,
                           p0=[0, 0, 0], bounds=(-np.inf, np.inf))

    plt.plot(x_vals, y_vals, '+')
    plt.plot(np.sort(x_vals), powerlaw(np.sort(x_vals), *pars))
    plt.legend(["Experimental Uncertainty" "Powerlaw"])
    plt.xscale("log", nonpositive='clip')
    plt.xlabel("Intensity")
    plt.ylabel("Relative Uncertainty")
    plt.title("Relative Uncertainty vs Intensity Relationship")

    return plt, pars, conv


def norm_ydep_pwr_synth(x_vals, y_vals, pwr_pars):
    """Generate synthetic data based on an impirical power law relationship
    between relative uncertainty and normalised intensity. This approach will synthesise data in
    the fashion of an x-ray SAS experiment.

    Inputs: x_vals - 1d np array of sasmodel Q data
            y_vals - 1d np array of sasmodel intensity data
            pwr_pars - 1d array of power law parameters from power law fit
                       between ydev/y against y

    Outputs: y_syn - 1d array of synthesised intensity data
             ydev_syn - 1d np array of synthesised uncertainty data
    """

    y_norm, norm_pars = normalise_data(y_vals)

    y_syn = []
    ydev_syn = []
    rng = default_rng()
    for y_datum in y_norm:
        ydev_rel_temp = powerlaw(y_datum, *pwr_pars)
        ydev_temp = ydev_rel_temp*y_datum # include scalar multiple here to amplify noise
        ydev_syn.append(ydev_temp)
        noise_temp = rng.normal(loc=0.0,
                                scale=ydev_temp) + rng.normal(loc=0.0,
                                                              scale=0.05 * y_datum)
        y_syn.append(y_datum + noise_temp)
    ydev_syn = np.array(ydev_syn)
    y_syn = np.array(y_syn)

    y_syn = denormalise_data(y_syn, norm_pars)
    ydev_syn = denormalise_data(ydev_syn, norm_pars)

    plt.plot(x_vals, y_vals, "--", color="red", zorder=3)
    plt.plot(x_vals, y_syn, zorder=2)
    plt.errorbar(x_vals, y_syn, yerr=ydev_syn,
                 fmt="None", color="orange", zorder=1)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.xscale("log", nonpositive='clip')
    plt.yscale("log", nonpositive='clip')
    plt.legend(["sasmodel", "synthetic data", "synthetic uncertainty"])
    return plt, y_syn, ydev_syn


def norm_xdep_linterp_synth(x_mdl, y_mdl, x_xp, ydev_rel_xp):
    """Generate synthetic data based on a linear interpolation of the experimental
    relationship between uncertainty and normalised Q.

    Inputs: x_mdl - 1d np array of sasmodel Q data
            y_mdl - 1d np array of sasmodel I data
            x_xp - 1d np array of experimental Q data
            ydev_xp - 1d np array of experimental uncertainty in I data

    Outputs: plt - plot handle
             y_syn - 1d array of synthesised intensity data
             ydev_syn - 1d np array of synthesised uncertainty data
    """

    x_mdl_norm, _ = normalise_data(x_mdl)
    x_xp_norm, _ = normalise_data(x_xp)

    y_syn = []
    ydev_syn = []
    x_syn = []
    rng = default_rng()
    for x_datum, y_datum in zip(x_mdl_norm, y_mdl):
        ydev_temp = np.interp(x_datum, x_xp_norm, ydev_rel_xp) * y_datum
        noise_temp = rng.normal(
            loc=0.0,
            scale=ydev_temp
            )
        ydev_syn.append(ydev_temp)
        y_syn.append(y_datum + noise_temp)
        x_syn.append(x_datum)

    ydev_syn = np.array(ydev_syn)
    y_syn = np.array(y_syn)

    plt.plot(x_mdl, y_mdl, "--", color="red", zorder=3)
    plt.plot(x_mdl, y_syn, zorder=2)
    plt.errorbar(x_mdl, y_syn, yerr=ydev_syn,
                 fmt="None", color="orange", zorder=1)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.xscale("log", nonpositive='clip')
    plt.yscale("log", nonpositive='clip')
    plt.legend(["sasmodel", "synthetic data", "synthetic uncertainty"])

    return plt, y_syn, ydev_syn


def example_xray_synth():
    """Method to run for a graphical demonstration of the x-ray-style
    synthesis approach.
    """
    # find the folder and file containing the experimental x-ray data
    pfolder = "experimental_xray_sas"
    fnames = file_names(pfolder)
    fname = fnames[0]

    # read the x-ray experimental data (x, y and y-uncertainty)
    x_xp, y_xp, ydev_xp = read_xray_data(pfolder, fname)
    ydev_rel_xp = ydev_xp / y_xp

    fig = errorbar_xy(
        x_xp,
        y_xp,
        ydev_xp,
        title="Example X-Ray SAS Synthesis Process - " +
        "Experimental Data (" +
        fname +
        ")")
    fig.show()

    # plot what are considered the dependent and independent variables
    # for this particular case
    plt.plot(y_xp, ydev_rel_xp, '+')
    plt.xlabel("Y (Independent)")
    plt.ylabel("Relative Y-Uncertainty (Dependent)")
    plt.xscale("log", nonpositive='clip')
    plt.show()

    # normalise the dependent and independent variables then perform
    # power law fit to characterise their relationship
    ydev_rel_norm_xp, _ = normalise_data(ydev_rel_xp)
    y_norm_xp, _ = normalise_data(y_xp)
    fig, pwr_pars, _ = power_fit(y_norm_xp, ydev_rel_norm_xp)
    fig.legend(["Experimental Uncertainty", "Powerlaw Fit Used for Sampling"])
    fig.xscale("log", nonpositive='clip')
    fig.xlabel("Intensity")
    fig.ylabel("Relative Uncertainty")
    fig.title("Example X-Ray SAS Synthesis Process -"
              + " Relative Uncertainty vs Intensity for Experimental Data")
    fig.show()

    # reading sasmodel data for example synthesis
    modelf = "example_sasmodel"
    mdlname = "1D_core_shell_cylinder_20_20_400_nosmearing.txt"
    x_mdl, y_mdl = read_sasmodel_data(modelf, mdlname)

    # plotting example synthesis case
    fig, _, _ = norm_ydep_pwr_synth(x_mdl, y_mdl, pwr_pars)
    fig.title(
        "Example X-Ray SAS Synthesis Process - Synthetic Data from sasmodel (" +
        mdlname +
        ")")
    fig.show()


def example_neutron_synth():
    """Method to run for a graphical demonstration of the neutron-style
    synthesis approach.
    """
    # find the folder and file containing the experimental neutron data
    pfolder = "experimental_neutron_sas"
    fnames = file_names(pfolder)
    fname = fnames[0]

    # read the neutron experimental data (x, y and y-uncertainty)
    x_xp, y_xp, ydev_xp = read_neutron_data(pfolder, fname)
    # determine relative uncertainty
    ydev_rel_xp = ydev_xp / y_xp

    fig = errorbar_xy(
        x_xp,
        y_xp,
        ydev_xp,
        title="Example Neutron SAS Synthesis Process - " +
        "Experimental Data (" +
        fname +
        ")")
    fig.show()

    # For neutron data, a curve fit was not appropriate for either x or
    # y dependent y-uncertainty so a linear interpolant of the x dependent
    # case was used.

    plt.plot(x_xp, ydev_rel_xp)
    plt.xlabel("X (Independent)")
    plt.ylabel("Relative Y_Uncertainty (Dependent)")
    plt.title("Example Neutron SAS Synthesis Process - " +
                "No Suitable Curve Fit")
    plt.show()

    # reading sasmodel data for example synthesis
    modelf = "example_sasmodel"
    mdlname = "1D_core_shell_cylinder_20_20_400_nosmearing.txt"
    x_mdl, y_mdl = read_sasmodel_data(modelf, mdlname)

    # plotting example synthesis case
    fig, _, _ = norm_xdep_linterp_synth(x_mdl, y_mdl, x_xp, ydev_rel_xp)
    fig.title(
        "Example Neutron SAS Synthesis Process - Synthetic Data from sasmodel (" +
        mdlname +
        ")")
    fig.show()


def xray_synth(pfolder):
    """Create synthetic xray data for all sasmodel data files
    in folder and then write them to the folder with supporting figures."""

    # experimental dataset on which to base noise and uncertainty
    xp_folder = "experimental_xray_sas"
    xp_fname = "100 and 200 nm Polystyrene NPs in Water.dat"
    # read the x-ray experimental data (y and y-uncertainty)
    _, y_xp, ydev_xp = read_xray_data(xp_folder, xp_fname)

    # normalising data
    y_xp_norm, _ = normalise_data(y_xp)
    ydev_rel_xp_norm, _ = normalise_data(ydev_xp/y_xp)

    # characterising the relationship between normalised y and normalised
    # relative uncertainty
    fig, pwr_pars, _ = power_fit(y_xp_norm, ydev_rel_xp_norm)
    fig.close()

    # model data from which synthetic data will be generated
    mdl_fnames = []
    ext = "_xray_synth.txt"
    for file in os.listdir(pfolder):
        if file.endswith(".txt") and (not file.endswith("_synth.txt")):
            if not file[:-4] + ext in os.listdir(pfolder):
                mdl_fnames.append(file)

    if mdl_fnames == []:
        print("No outstanding sasmodel datasets for xray"
              + " synthesis found in directory.")

    for mdl in mdl_fnames:
        syn_fname = mdl[:-4] + "_" + "xray_synth"
        fig_name = pfolder + "\\" + syn_fname + ".png"
        x_mdl, y_mdl = read_sasmodel_data(pfolder, mdl)
        fig, y_syn, ydev_syn = norm_ydep_pwr_synth(x_mdl, y_mdl, pwr_pars)
        fig.title(fig_name)
        fig_h = fig.gcf()
        fig_h.set_size_inches(24, 13.5)
        fig.savefig(fig_name, bbox_inches='tight')
        fig.close()

        # Writing to text file
        syn_dat = np.column_stack((x_mdl, y_syn, ydev_syn))
        np.savetxt(
            pfolder +
            "\\" +
            syn_fname +
            ".txt",
            syn_dat,
            header='<X>\t<Y>\t<devY>',
            fmt='%.5f %.5f %.5f',
            delimiter='\t')


def neutron_synth(pfolder):
    """ Create synthetic neutron data for all sasmodel data files
    in folder and then write them to the folder with supporting figures."""

    # experimental dataset on which to base noise and uncertainty
    xp_folder = "experimental_neutron_sas"
    xp_fname = "33837rear_1D_1.75_16.5_NXcanSAS.h5"


    # read the neutron experimental data (x, y and y-uncertainty)
    x_xp, y_xp, ydev_xp = read_neutron_data(xp_folder, xp_fname)
    # determine relative uncertainty
    ydev_rel_xp = ydev_xp / y_xp


    # model data from which synthetic data will be generated
    mdl_fnames = []
    ext = "_neutron_synth.txt"
    for file in os.listdir(pfolder):
        if file.endswith(".txt") and (not file.endswith("_synth.txt")):
            if not file[:-4] + ext in os.listdir(pfolder):
                mdl_fnames.append(file)

    if mdl_fnames == []:
        print("No outstanding sasmodel datasets for neutron"
              + " synthesis found in directory.")

    for mdl in mdl_fnames:
        syn_fname = mdl[:-4] + "_neutron_synth"
        fig_name = pfolder + "\\" + syn_fname + ".png"
        x_mdl, y_mdl = read_sasmodel_data(pfolder, mdl)
        fig, y_syn, ydev_syn = norm_xdep_linterp_synth(
            x_mdl, y_mdl, x_xp, ydev_rel_xp)
        fig.title(fig_name)
        fig_h = fig.gcf()
        fig_h.set_size_inches(24, 13.5)
        fig.savefig(fig_name, bbox_inches='tight')
        fig.close()

        # Writing to text file
        syn_dat = np.column_stack((x_mdl, y_syn, ydev_syn))
        np.savetxt(
            pfolder +
            "\\" +
            syn_fname +
            ".txt",
            syn_dat,
            header='<X>\t<Y>\t<devY>',
            fmt='%.5f %.5f %.5f',
            delimiter='\t')


def problem_def_txt(rfolder, wfolder):
    """Generate the problem files and META file to accompany the synthetic datasets for
    use in fitbenchmarking."""

    titstr = "# FitBenchmark Problem"
    sftstr = "software = 'SASView'"
    fncstr = ["function = 'name=FUNCTION_NAME,PAR1=0.0,PARn=0.0,...'" +
              "background=0.0,scale=1.0,sld=4.0,sld_solvent=1.0'"]

    mdl_fnames = []
    neutronext = "_neutron_synth.txt"
    xrayext = "_xray_synth.txt"
    for file in os.listdir(rfolder):
        if file.endswith(neutronext) or file.endswith(xrayext):
            mdl_fnames.append(file)

    prob_fnames = []
    base_prob_fname = ["MODEL_NAME", "EXPERIMENT_TYPE", "_def.txt"]
    prob_names = []
    base_prob_name = ["name = '", "MODEL_NAME",
                      "(synthetic ", "EXPERIMENT_TYPE", ")'"]
    descs = []
    base_desc = [
        "description = 'A first iteration synthetic dataset generated for the ",
        "MODEL_NAME",
        "SASView model in the fashion of ",
        "EXPERIMENT_TYPE",
        " small angle scattering experiments. Generated on ",
        time.asctime(),
        ".'"]
    input_files = []
    base_input_files = ["input_file = '", "INPUT_FILENAME", "'"]
    for fname in mdl_fnames:
        digs = re.findall(r'\d+', fname)
        mdl_name = fname[0:fname.find(digs[1])]
        base_prob_fname[0] = mdl_name
        mdl_name = mdl_name.replace("_", " ")
        if fname.endswith(neutronext):
            base_prob_name[1] = mdl_name
            base_desc[1] = mdl_name
            base_prob_fname[1] = "neutron"
            base_prob_name[3] = "neutron"
            base_desc[3] = "neutron"
            prob_fnames.append("".join(base_prob_fname))
            base_input_files[1] = fname
            prob_names.append("".join(base_prob_name))
            descs.append("".join(base_desc))
            input_files.append("".join(base_input_files))
        elif fname.endswith(xrayext):
            base_prob_name[1] = mdl_name
            base_desc[1] = mdl_name
            base_prob_fname[1] = "x-ray"
            base_prob_name[3] = "x-ray"
            base_desc[3] = "x-ray"
            prob_fnames.append("".join(base_prob_fname))
            base_input_files[1] = fname
            prob_names.append("".join(base_prob_name))
            descs.append("".join(base_desc))
            input_files.append("".join(base_input_files))

    for fname, input_file, prob, desc in zip(
            prob_fnames, input_files, prob_names, descs):
        text_body = "\n".join([titstr, sftstr, prob, desc, input_file, fncstr[0]])
        if fname not in os.listdir(wfolder):
            with open(wfolder + "//" + fname, "w") as prob_def_file:
                prob_def_file.write(text_body)

    if "META.txt" not in os.listdir(wfolder):
        with open(wfolder + "//" + "META.txt", "w") as meta_file:
            meta_file.write(wfolder + "\n")
            meta_file.write("\n")
            meta_file.write("%s problems synthesised from the SASView models"
                            "on %s. See table below for details.\n"
                            % (len(prob_fnames), time.asctime()))
            meta_file.write("\n")
            col_width = 25
            header = [
                "SASmodel Name",
                "Dimension",
                "Data Format",
                "Synthesis Style"]
            meta_file.write("".join(item.ljust(col_width) for item in header))
            meta_file.write("\n\n")
            for fname in prob_fnames:
                n_split = fname.split("_")
                dtype = n_split[0]
                if dtype == "1D":
                    dfmt = "<Q> <I> <Idev>"
                syn_style = n_split[-2]
                mname = " ".join(n_split[1:-2])
                tab_line = [mname, dtype, dfmt, syn_style]
                meta_file.write("".join(item.ljust(col_width)
                                for item in tab_line))
                meta_file.write("\n")


def main():
    """ Main function to run on sasmodel datasets."""
    pfolder = args.folder
    synthtype = args.synthtype
    dfolder = pfolder + "\\data_files"

    if synthtype == "all":
        xray_synth(dfolder)
        neutron_synth(dfolder)
    elif synthtype == "xray":
        xray_synth(dfolder)
    elif synthtype == "neutron":
        neutron_synth(dfolder)

    problem_def_txt(dfolder, pfolder)


if __name__ == "__main__":
    main()
