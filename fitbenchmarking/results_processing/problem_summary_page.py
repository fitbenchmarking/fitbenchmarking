"""
Create the summary pages for the best minimizers.
"""
import inspect
import os

from jinja2 import Environment, FileSystemLoader

import fitbenchmarking
from fitbenchmarking.results_processing.plots import Plot
from fitbenchmarking.utils.misc import get_css


def create(results_per_test, group_name, support_pages_dir, figures_dir, options):
    """
    Create the problem summary pages.

    :param results_per_test: results object
    :type results_per_test: list[list[FittingResult]]
    :param group_name: name of the problem group
    :type group_name: str
    :param support_pages_dir: directory in which the results are to be saved
    :type support_pages_dir: str
    :param options: The options used in the fitting problem and plotting
    :type options: fitbenchmarking.utils.options.Options
    """
    for problem_results in results_per_test:
        categorised = []
        categories = {}
        best_in_category = {}
        for result in problem_results:
            cf_name = result.cost_func.__class__.__name__
            if cf_name.endswith('CostFunc'):
                cf_name = cf_name[:-len('CostFunc')]
            categories[cf_name].append(result)
            if cf_name not in best_in_category or \
                    result.chi_sq > best_in_category[cf_name].chi_sq:
                best_in_category[cf_name] = result

        for cf, result in best_in_category.items():
            categorised.append((cf, result,
                                'This is the best fit of the minimizers used '
                                f'under the {cf} cost function.'))

        summary_plot_path = Plot.plot_summary(categories, options, figures_dir)

        _create_summary_page(categorised, group_name, summary_plot_path,
                             support_pages_dir, options)


def _create_summary_page(categorised_best_results, group_name, support_pages_dir, options):
    """
    Create a summary page for a best result grouping.
    """
    categories, results, descriptions = zip(*categorised_best_results)

    prob_name = results[0].sanitised_name

    file_name = '{}_{}_best.html'.format(
        group_name, prob_name)
    file_name = file_name.lower()
    file_path = os.path.join(support_pages_dir, file_name)

    # Bool for print message/insert image
    init_success = options.make_plots

    best_plot_available = []
    best_fits = []

    if options.make_plots:
        for result in enumerate(results):
            fig_fit, fig_start = _get_figure_paths(result)
            if fig_fit == '':
                fig_fit = result.figure_error
                best_plot_available.append(False)
            else:
                best_plot_available.append(True)
            if init_success and fig_start == '':
                fig_start = result.figure_error
                init_success = False
    else:
        best_plot_available = [False for _ in results]
        fig_start = 'Re-run with make_plots set to yes in the ' \
                    'ini file to generate plots.'
        best_fits = [fig_start for _ in results]

    root = os.path.dirname(inspect.getfile(fitbenchmarking))
    template_dir = os.path.join(root, "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    css = get_css(options, support_pages_dir)
    template = env.get_template("problem_summary_page_template.html")

    with open(file_path, 'w') as fh:
        fh.write(template.render(
            css_style_sheet=css['main'],
            table_style=css['table'],
            custom_style=css['custom'],
            title=result.name,
            description=result.problem.description,
            equation=result.problem.equation,
            initial_guess=result.ini_function_params,
            initial_plot_available=init_success,
            initial_plot=fig_start,
            categories=categories,
            best_results=results,
            best_plots_available=best_plot_available,
            best_plots=best_fits))

    result.support_page_link = os.path.relpath(file_path)


def _get_figure_paths(result):
    """
    Get the paths to the figures used in the support page.

    :param result: The result to get the figures for
    :type result: fitbenchmarking.utils.fitbm_result.FittingProblem

    :return: the paths to the required figures
    :rtype: tuple(str, str)
    """

    figures_dir = "figures"

    output = []
    for link in [result.figure_link, result.start_figure_link]:
        if link == '':
            output.append('')
        else:
            path = os.path.join(figures_dir, link)
            output.append(path)

    return output[0], output[1]
