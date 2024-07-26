"""
Set up and build the fitting reports for various types of problems.
"""


import inspect
import os

import numpy as np
from jinja2 import Environment, FileSystemLoader

import fitbenchmarking
from fitbenchmarking.utils.misc import get_css


def create(results, support_pages_dir, options):
    """
    Iterate through problem results and create a fitting report html page for
    each.

    :param results: results object
    :type results: list[FittingResult]
    :param support_pages_dir: directory in which the results are saved
    :type support_pages_dir: str
    :param options: The options used in the fitting problem and plotting
    :type options: fitbenchmarking.utils.options.Options
    """

    for prob_result in results:
        if np.isinf(prob_result.accuracy) and np.isinf(prob_result.runtime):
            continue
        create_prob_group(prob_result,
                          support_pages_dir,
                          options)


def create_prob_group(result, support_pages_dir, options):
    """
    Creates a fitting report containing figures and other details about the fit
    for a problem.
    A link to the fitting report is stored in the results object.

    :param result: The result for a specific benchmark problem-minimizer-etc
                   combination
    :type result: fitbenchmarking.utils.fitbm_result.FittingResult
    :param support_pages_dir: directory to store the support pages in
    :type support_pages_dir: str
    :param options: The options used in the fitting problem and plotting
    :type options: fitbenchmarking.utils.options.Options
    """
    prob_name = result.sanitised_name

    file_name = f'{prob_name}_{result.costfun_tag}_' \
                f'{result.sanitised_min_name(with_software=True)}.html'
    file_name = file_name.lower()
    file_path = os.path.join(support_pages_dir, file_name)

    # Bool for print message/insert image
    fit_success = init_success = pdf_success = options.make_plots

    if options.make_plots:
        fig_fit, fig_start, fig_pdf = get_figure_paths(result)
        fit_success = fig_fit != ''
        init_success = fig_start != ''
        pdf_success = fig_pdf != ''
        if not fit_success:
            fig_fit = result.figure_error
        if not init_success:
            fig_start = result.figure_error
        if not pdf_success:
            fig_pdf = result.figure_error
    else:
        fig_fit = fig_start = fig_pdf = 'Re-run with make_plots ' \
            'set to yes in the ini file to generate plots.'

    run_name = f"{options.run_name}: " if options.run_name else ''

    root = os.path.dirname(inspect.getfile(fitbenchmarking))
    template_dir = os.path.join(root, "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    css = get_css(options, support_pages_dir)
    template = env.get_template("fitting_report_template.html")
    n_params = result.get_n_parameters()
    list_params = True if n_params < 100 else False

    if np.isnan(result.emissions):
        emission_disp = 'N/A'
    else:
        emission_disp = f"{result.emissions:.4g} kg CO\u2082 eq"

    with open(file_path, 'w', encoding='utf-8') as fh:
        fh.write(template.render(
            css_style_sheet=css['main'],
            table_style=css['table'],
            custom_style=css['custom'],
            title=result.name,
            run_name=run_name,
            description=result.problem_desc,
            equation=result.equation,
            initial_guess=result.ini_function_params,
            minimizer=result.modified_minimizer_name(),
            accuracy=f"{result.accuracy:.4g}",
            runtime=f"{result.runtime:.4g}",
            emissions=emission_disp,
            is_best_fit=result.is_best_fit,
            initial_plot_available=init_success,
            initial_plot=fig_start,
            min_params=result.fin_function_params,
            fitted_plot_available=fit_success,
            fitted_plot=fig_fit,
            pdf_plot_available=pdf_success,
            pdf_plot=fig_pdf,
            n_params=n_params,
            list_params=list_params,
            n_data_points=result.get_n_data_points()))

    result.fitting_report_link = os.path.abspath(file_path)


def get_figure_paths(result):
    """
    Get the paths to the figures used in the support page.

    :param result: The result to get the figures for
    :type result: fitbenchmarking.utils.fitbm_result.FittingProblem

    :return: the paths to the required figures
    :rtype: tuple(str, str)
    """

    figures_dir = "figures"

    output = []
    for link in [result.figure_link, result.start_figure_link,
                 result.posterior_plots]:
        output.append(os.path.join(figures_dir, link) if link else '')

    return output[0], output[1], output[2]
