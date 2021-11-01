"""
Create the summary pages for the best minimizers.
"""
import inspect
import os

from jinja2 import Environment, FileSystemLoader

import fitbenchmarking
from fitbenchmarking.results_processing.plots import Plot
from fitbenchmarking.utils.misc import get_css


def create(results, best_results, support_pages_dir, figures_dir, options):
    """
    Create the problem summary pages.

    :param results: The results to create summary pages for
    :type results: dict[str, dict[str, list[FittingResult]]]
    :param best_results: The best result from each row and category
    :type best_results: dict[str, dict[str, FittingResult]]
    :param support_pages_dir: directory in which the results are to be saved
    :type support_pages_dir: str
    :param figures_dir: The directory where figures are stored.
    :type figures_dir: str
    :param options: The options used in the fitting problem and plotting
    :type options: fitbenchmarking.utils.options.Options
    """
    for problem_key in results:
        categorised = []
        problem_results = results[problem_key]
        problem_best = best_results[problem_key]
        for cf, result in problem_best.items():
            categorised.append((cf, result,
                                'This is the best fit of the minimizers used '
                                f'under the {cf} cost function.'))

        summary_plot_path = ''
        if options.make_plots:
            summary_plot_path = Plot.plot_summary(categories=problem_results,
                                                  title=categorised[0][1].name,
                                                  options=options,
                                                  figures_dir=figures_dir)

        _create_summary_page(categorised_best_results=categorised,
                             summary_plot_path=summary_plot_path,
                             support_pages_dir=support_pages_dir,
                             options=options)


def _create_summary_page(categorised_best_results, summary_plot_path,
                         support_pages_dir, options):
    """
    Create a summary page for a problem from given categories.

    :param categorised_best_results: A tag, best result, and description for
                                     each category
    :type categorised_best_results: list[tuple[str, FittingResult, str]]
    :param summary_plot_path: Path to the summary plot
    :type summary_plot_path: str
    :param support_pages_dir: Directory to save suport page to
    :type support_pages_dir: str
    :param options: The chosen fitbenchmaring options
    :type options: utils.optons.Options
    """
    categories, results, descriptions = zip(*categorised_best_results)

    prob_name = results[0].sanitised_name

    file_name = f'{prob_name}_summary.html'.lower()
    file_path = os.path.join(support_pages_dir, file_name)

    # Bool for print message/insert image
    init_success = options.make_plots

    best_plot_available = []
    best_fits = []
    summary_plot_available = True
    summary_plot_path = os.path.join("figures", summary_plot_path)

    if options.make_plots:
        for result in results:
            fig_fit, fig_start = _get_figure_paths(result)
            best_plot_available.append(fig_fit != '')
            if not best_plot_available[-1]:
                fig_fit = result.figure_error

            if init_success and fig_start == '':
                fig_start = result.figure_error
                init_success = False
            best_fits.append(fig_fit)
    else:
        best_plot_available = [False] * len(results)
        fig_start = 'Re-run with make_plots set to yes in the ' \
                    'ini file to generate plots.'
        best_fits = [fig_start] * len(results)

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
            summary_plot_available=summary_plot_available,
            summary_plot=summary_plot_path,
            title=results[0].name,
            description=results[0].problem.description,
            equation=results[0].problem.equation,
            initial_guess=results[0].ini_function_params,
            initial_plot_available=init_success,
            initial_plot=fig_start,
            categories=categories,
            best_results=results,
            best_plots_available=best_plot_available,
            plot_descriptions=descriptions,
            best_plots=best_fits))

    for r in results:
        r.problem_summary_page_link = file_path


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
        output.append(os.path.join(figures_dir, link) if link else '')

    return output[0], output[1]
