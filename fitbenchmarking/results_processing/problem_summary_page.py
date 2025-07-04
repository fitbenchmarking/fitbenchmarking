"""
Create the summary pages for the best minimizers.
"""

import inspect
from pathlib import Path

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
    multistart = create_multistart_plots(results)
    for problem_key in results:
        categorised = []
        problem_results = results[problem_key]
        problem_best = best_results[problem_key]
        for cf, result in problem_best.items():
            categorised.append(
                (
                    cf,
                    result,
                    "This is the best fit of the minimizers used "
                    f"under the {cf} cost function.",
                )
            )

        # Create the plots and set the paths
        if options.make_plots:
            common_args = {
                "categories": problem_results,
                "title": categorised[0][1].name,
                "options": options,
                "figures_dir": figures_dir,
            }
            summary = Plot.plot_summary(**common_args)
            residuals = Plot.plot_residuals(**common_args)
            two_d = Plot.plot_2d_data(**common_args)
        else:
            summary = residuals = two_d = ""

        _create_summary_page(
            categorised_best_results=categorised,
            summary_plot=summary,
            residuals_plot=residuals,
            two_d_plot=two_d,
            multistart_plot=multistart,
            support_pages_dir=support_pages_dir,
            options=options,
        )


def create_multistart_plots(results):
    """
    Create the plots for different starting conditions.

    :param results: The results to create summary pages for
    :type results: dict[str, dict[str, list[FittingResult]]]
    """
    # Sort the result based on the cost function,
    # software and minimizers for plotting
    sorted_results = {}
    for problem in results:
        for cost_function in results[problem]:
            for result in results[problem][cost_function]:
                sorted_results.setdefault(result.costfun_tag, {}).setdefault(
                    result.software, {}
                ).setdefault(result.minimizer, []).append(result)
    return ""


def _create_summary_page(
    categorised_best_results,
    summary_plot,
    residuals_plot,
    two_d_plot,
    multistart_plot,
    support_pages_dir,
    options,
):
    """
    Create a summary page for a problem from given categories.

    :param categorised_best_results: A tag, best result, and description for
                                     each category
    :type categorised_best_results: list[tuple[str, FittingResult, str]]
    :param summary_plot: Path to the summary plot
    :type summary_plot: str
    :param residuals_plot: Path to the residuals plot
    :type residuals_plot: str
    :param two_d_plot: Path to the 2d data plot, if available, or
                         empty string otherwise
    :type two_d_plot: str
    :param multistart_plot: Path to the multistart comparison plot.
    :type multistart_plot: str
    :param support_pages_dir: Directory to save suport page to
    :type support_pages_dir: str
    :param options: The chosen fitbenchmaring options
    :type options: utils.optons.Options
    """
    categories, results, descriptions = zip(*categorised_best_results)

    prob_name = results[0].sanitised_name

    file_name = f"{prob_name}_summary.html".lower()
    file_path = Path(support_pages_dir) / file_name

    # Bool for print message/insert image
    init_success = options.make_plots

    best_plot_available = []
    best_fits = []
    fig_start = None
    summary_plot = Path("figures") / summary_plot
    residuals_plot = Path("figures") / residuals_plot

    rerun_make_plots_msg = ""

    if two_d_plot_available := bool(two_d_plot):
        two_d_plot = Path("figures") / two_d_plot
    if multistart_plot_avaliable := bool(multistart_plot):
        multistart_plot = Path("figures") / multistart_plot

    if options.make_plots:
        summary_plot_available = True
        for result in results:
            fig_fit = (
                str(Path("figures") / result.figure_link)
                if result.figure_link
                else ""
            )
            best_plot_available.append(bool(fig_fit))
            if not best_plot_available[-1]:
                fig_fit = result.figure_error

            if init_success and fig_start == "":
                fig_start = result.figure_error
                init_success = False
            best_fits.append(fig_fit)
    else:
        summary_plot_available = False
        best_plot_available = [False] * len(results)
        rerun_make_plots_msg = (
            "Re-run with make_plots set to yes "
            "in the ini file to generate plots."
        )
        best_fits = [rerun_make_plots_msg] * len(results)

    root = Path(inspect.getfile(fitbenchmarking)).parent
    template_dir = root / "templates"
    env = Environment(loader=FileSystemLoader(template_dir))
    css = get_css(options, support_pages_dir)
    template = env.get_template("problem_summary_page_template.html")

    run_name = f"{options.run_name}: " if options.run_name else ""

    n_params = results[0].get_n_parameters()
    list_params = n_params < 100

    with open(file_path, "w", encoding="utf-8") as fh:
        fh.write(
            template.render(
                css_style_sheet=css["main"],
                table_style=css["table"],
                custom_style=css["custom"],
                summary_plot_available=summary_plot_available,
                summary_plot=summary_plot,
                residuals_plot=residuals_plot,
                two_d_plot_available=two_d_plot_available,
                two_d_plot=two_d_plot,
                multistart_plot_avaliable=multistart_plot_avaliable,
                multistart_plot=multistart_plot,
                title=results[0].name,
                description=results[0].problem_desc,
                equation=results[0].equation,
                initial_guess=results[0].ini_function_params,
                min_params=results[0].fin_function_params,
                categories=categories,
                best_results=results,
                best_plots_available=best_plot_available,
                plot_descriptions=descriptions,
                run_name=run_name,
                best_plots=best_fits,
                n_params=n_params,
                list_params=list_params,
                n_data_points=results[0].get_n_data_points(),
                rerun_make_plots_msg=rerun_make_plots_msg,
            )
        )

    for r in results:
        r.problem_summary_page_link = file_path
