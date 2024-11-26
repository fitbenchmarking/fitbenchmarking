"""
Functions that create the tables, support pages, figures, and indexes.
"""

import inspect
import logging
import os
import platform
import re
import webbrowser
from shutil import copytree
from typing import Optional, Union

import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from jinja2 import Environment, FileSystemLoader

import fitbenchmarking
from fitbenchmarking.results_processing import (
    fitting_report,
    performance_profiler,
    plots,
    problem_summary_page,
    tables,
)
from fitbenchmarking.results_processing.performance_profiler import (
    DashPerfProfile,
)
from fitbenchmarking.utils import create_dirs
from fitbenchmarking.utils.exceptions import PlottingError
from fitbenchmarking.utils.fitbm_result import FittingResult
from fitbenchmarking.utils.log import get_logger
from fitbenchmarking.utils.misc import get_css, get_js
from fitbenchmarking.utils.options import Options
from fitbenchmarking.utils.write_files import write_file

LOGGER = get_logger()
os.environ["QT_QPA_PLATFORM"] = "offscreen"


@write_file
def save_results(
    options,
    results,
    group_name,
    failed_problems,
    unselected_minimizers,
    config,
):
    """
    Create all results files and store them.
    Result files are plots, support pages, tables, and index pages.

    :param options: The options used in the fitting problem and plotting
    :type options: fitbenchmarking.utils.options.Options
    :param results: The results from fitting
    :type results: list[fitbenchmarking.utils.fitbm_result.FittingResult]
    :param group_name: name of the problem group
    :type group_name: str
    :param failed_problems: list of failed problems to be reported in the
                            html output
    :type failed_problems: list
    :params unselected_minimizers: Dictionary containing unselected minimizers
                                   based on the algorithm_type option
    :type unselected_minimizers: dict
    :params config: Dictionary containing env config
    :type config: dict

    :return: Path to directory of group results, data for building the
             performance profile plots
    :rtype: str, dict[str, pandas.DataFrame]
    """
    group_dir, supp_dir, fig_dir = create_directories(options, group_name)

    for r in results:
        setattr(r, "runtime_metric", options.runtime_metric)

    best_results, results_dict = preprocess_data(results)

    pp_locations, pp_dfs = performance_profiler.profile(
        results_dict, fig_dir, options
    )

    if options.make_plots:
        create_plots(options, results_dict, best_results, fig_dir)

    fitting_report.create(
        options=options, results=results, support_pages_dir=supp_dir
    )
    problem_summary_page.create(
        options=options,
        results=results_dict,
        best_results=best_results,
        support_pages_dir=supp_dir,
        figures_dir=fig_dir,
    )

    table_names, table_descriptions = tables.create_results_tables(
        options=options,
        results=results_dict,
        best_results=best_results,
        group_dir=group_dir,
        fig_dir=fig_dir,
        pp_locations=pp_locations,
        failed_problems=failed_problems,
        unselected_minimzers=unselected_minimizers,
    )

    create_problem_level_index(
        options=options,
        table_names=table_names,
        group_name=group_name,
        group_dir=group_dir,
        table_descriptions=table_descriptions,
        config=config,
    )

    return group_dir, pp_dfs


def create_directories(options, group_name):
    """
    Create the directory structure ready to store the results

    :param options: The options used in the fitting problem and plotting
    :type options: fitbenchmarking.utils.options.Options
    :param group_name: name of the problem group
    :type group_name: str
    :return: paths to the top level group results, support pages,
             and figures directories
    :rtype: (str, str, str)
    """
    results_dir = create_dirs.results(options.results_dir)
    group_dir = create_dirs.group_results(results_dir, group_name)
    support_dir = create_dirs.support_pages(group_dir)
    figures_dir = create_dirs.figures(support_dir)
    return group_dir, support_dir, figures_dir


def preprocess_data(results: list[FittingResult]):
    """
    Generate a dictionary of results lists sorted into the correct order
    with rows and columns as the key and list elements respectively.

    This is used to create HTML and txt tables.
    This is stored in self.sorted_results

    :param results: The results to process
    :type results: list[fitbenchmarking.utils.fitbm_result.FittingResult]

    :return: The best result grouped by row and category (cost function),
             The sorted results grouped by row and category
    :rtype: dict[str, dict[str, utils.fitbm_result.FittingResult]],
            dict[str, dict[str, list[utils.fitbm_result.FittingResult]]]
    """

    # Might be worth breaking out into an option in future.
    # sort_order[0] is the order of sorting for rows
    # sort_order[1] is the order of sorting for columns
    sort_order = (
        ["problem"],
        ["software", "minimizer", "jacobian", "hessian"],
    )

    # Additional separation for categories within columns
    col_sections = ["costfun"]

    # Generate the columns, category, and row tags and sort
    rows: Union[list[str], set[str]] = set()
    columns = {}
    for r in results:
        # Error 4 means none of the jacobians ran so can't infer the
        # jacobian names from this.
        if r.error_flag == 4:
            continue
        result_tags = _extract_tags(
            r,
            row_sorting=sort_order[0],
            col_sorting=sort_order[1],
            cat_sorting=col_sections,
        )
        rows.add(result_tags["row"])
        cat = result_tags["cat"]
        if cat not in columns:
            columns[cat] = set()
        columns[cat].add(result_tags["col"])

    rows = sorted(rows, key=str.lower)

    # Reorder keys and assign columns to indexes within them
    columns = {
        k: {col: i for i, col in enumerate(sorted(columns[k], key=str.lower))}
        for k in sorted(iter(columns.keys()), key=str.lower)
    }

    # Build the sorted results dictionary
    sorted_results: dict[str, dict[str, list[Optional[FittingResult]]]] = {
        r.strip(":"): {
            k: [None for _ in category] for k, category in columns.items()
        }
        for r in rows
    }

    for r in results:
        result_tags = _extract_tags(
            r,
            row_sorting=sort_order[0],
            col_sorting=sort_order[1],
            cat_sorting=col_sections,
        )
        # Fix up cells where error flag = 4
        if r.error_flag == 4:
            match_rows = _find_matching_tags(result_tags["row"], rows)
            match_cats = _find_matching_tags(
                result_tags["cat"], columns.keys()
            )
            for row in match_rows:
                for cat in match_cats:
                    match_cols = _find_matching_tags(
                        result_tags["col"], columns[cat]
                    )
                    for col in match_cols:
                        col = columns[cat][col]
                        sorted_results[row][cat][col] = r
        else:
            col = columns[result_tags["cat"]][result_tags["col"]]
            sorted_results[result_tags["row"]][result_tags["cat"]][col] = r

    # Find best results
    best_results = {}
    for r, row in sorted_results.items():
        best_results[r] = {}
        for c, cat in row.items():
            best_results[r][c] = _process_best_results(cat)

    return best_results, sorted_results


def _extract_tags(
    result: FittingResult,
    row_sorting: list[str],
    col_sorting: list[str],
    cat_sorting: list[str],
) -> dict[str, str]:
    """
    Extract the row, column, and category tags from a result based on a given
    sorting order.

    :param result: The result to find the tags for
    :type result: FittingResult
    :param row_sorting: The components in order of importance that will be
                        used to generate the row tag.
    :type row_sorting: list[str]
    :param col_sorting: The components in order of importance that will be
                        used to generate the col tag.
    :type col_sorting: list[str]
    :param cat_sorting: The components in order of importance that will be
                        used to generate the cat tag.
    :type cat_sorting: list[str]

    :return: A set of tags that can be used to sort this result amongst a list
             of results
    :rtype: dict[str, str]
    """
    result_tags = {"row": "", "col": "", "cat": ""}
    for tag, order in [
        ("row", row_sorting),
        ("col", col_sorting),
        ("cat", cat_sorting),
    ]:
        for sort_pos in order:
            if sort_pos in ["jacobian", "hessian"] and result.error_flag == 4:
                result_tags[tag] += ":[^:]*"
            else:
                result_tags[tag] += f':{getattr(result, sort_pos + "_tag")}'
        result_tags[tag] = result_tags[tag].lstrip(":")

    return result_tags


def _process_best_results(results: list[FittingResult]) -> FittingResult:
    """
    Process the best result from a list of FittingResults.
    This includes:
     - Setting the `is_best_fit` flag,
     - Setting the `min_accuracy` value,
     - Setting the `min_runtime` value, and
     - Setting the `min_energy` value

    :param results: The results to compare and update
    :type results: list[FittingResult]

    :return: The result with the lowest accuracy
    :rtype: FittingResult
    """
    best = results[0]
    fastest = results[0]
    lowest = results[0]
    for result in results[1:]:
        if best.accuracy > result.accuracy:
            best = result
        if fastest.runtime > result.runtime:
            fastest = result
        if lowest.energy > result.energy:
            lowest = result

    best.is_best_fit = True

    for result in results:
        result.min_accuracy = best.accuracy
        result.min_runtime = fastest.runtime
        result.min_energy = lowest.energy

    return best


def _find_matching_tags(tag: str, lst: list[str]):
    """
    Extract the full list of matches to the regex stored in tag.

    :param tag: A regex to search for
    :type tag: str
    :param lst: A set of tags to search
    :type lst: list[str]

    :return: The matching tags from lst
    :rtype: list[str]
    """
    return [match for match in lst if re.fullmatch(tag, match)]


def create_plots(options, results, best_results, figures_dir):
    """
    Create a plot for each result and store in the figures directory

    :param options: The options used in the fitting problem and plotting
    :type options: fitbenchmarking.utils.options.Options
    :param results: results nested array of objects
    :type results: list of list of
                   fitbenchmarking.utils.fitbm_result.FittingResult
    :param best_results: best result for each problem seperated by cost
                         function
    :type best_results:
        list[dict[str: fitbenchmarking.utils.fitbm_result.FittingResult]]

    :param figures_dir: Path to directory to store the figures in
    :type figures_dir: str
    """
    for best_dict, prob_result in zip(best_results.values(), results.values()):
        plot_dict = {}
        initial_guess_path = {}
        df = {}

        # Create a dataframe for each problem
        # Rows are datapoints in the fits
        for cf, cat_results in prob_result.items():
            # first, load with raw data
            df[cf] = pd.DataFrame(
                {
                    "x": cat_results[0].data_x,
                    "y": cat_results[0].data_y,
                    "e": cat_results[0].data_e,
                    "minimizer": "Data",
                    "cost_function": cf,
                    "best": False,
                }
            )
            # next the initial data
            tmp_df = pd.DataFrame(
                {
                    "x": cat_results[0].data_x,
                    "y": cat_results[0].ini_y,
                    "e": cat_results[0].data_e,
                    "minimizer": "Starting Guess",
                    "cost_function": cf,
                    "best": False,
                }
            )
            df[cf] = pd.concat([df[cf], tmp_df], ignore_index=True)

            # then get data for each minimizer
            for result in cat_results:
                tmp_df = pd.DataFrame(
                    {
                        "x": result.data_x,
                        "y": result.fin_y,
                        "e": result.data_e,
                        "minimizer": result.sanitised_min_name(True),
                        "cost_function": cf,
                        "best": result.is_best_fit,
                    }
                )
                df[cf] = pd.concat([df[cf], tmp_df], ignore_index=True)

        # For each result, if it succeeded, create a plot and add plot links to
        # the results object
        for cf, cat_results in prob_result.items():
            try:
                plot = plots.Plot(
                    best_result=best_dict[cf],
                    options=options,
                    figures_dir=figures_dir,
                )
            except PlottingError as e:
                for result in prob_result[cf]:
                    result.figure_error = str(e)
                continue

            # Create a plot showing the initial guess and get filename
            initial_guess_path[cf] = plot.plot_initial_guess(df[cf])

            # Get filenames of best plot first
            # If none of the fits succeeded, params could be None
            # Otherwise, add the best fit to the plot
            if best_dict[cf].params is not None:
                plot_path = plot.best_filename(best_dict[cf])
                best_dict[cf].figure_link = plot_path
            else:
                best_dict[
                    cf
                ].figure_error = "Minimizer failed to produce any parameters"
            best_dict[cf].start_figure_link = initial_guess_path[cf]
            plot_dict[cf] = plot

            plot_paths = plot.plotly_fit(df[cf])

            # Check if plot was successful
            if cf not in plot_dict:
                continue
            for result in cat_results:
                if result.params is not None:
                    result.figure_link = plot_paths[
                        result.sanitised_min_name(True)
                    ]
                else:
                    result.figure_error = (
                        "Minimizer failed to produce any parameters"
                    )
                result.start_figure_link = initial_guess_path[cf]

        # For each result, if it succeeded and produced posterior pdf estimates
        # for each parameter, create histogram plots and add plot links to the
        # results object
        for cf, cat_results in prob_result.items():
            for result in cat_results:
                if result.params_pdfs is not None:
                    plot_path = plot.plot_posteriors(result)
                    result.posterior_plots = plot_path


def create_problem_level_index(
    options, table_names, group_name, group_dir, table_descriptions, config
):
    """
    Generates problem level index page.

    :param options: The options used in the fitting problem and plotting
    :type options: fitbenchmarking.utils.options.Options
    :param table_names: list of table names
    :type table_names: list
    :param group_name: name of the problem group
    :type group_name: str
    :param group_dir: Path to the directory where the index should be stored
    :type group_dir: str
    :param table_descriptions: dictionary containing descriptions of the
                               tables and the comparison mode
    :type table_descriptions: dict
    :params config: Dictionary containing env config
    :type config: dict
    """
    js = get_js(options, group_dir)

    root = os.path.dirname(inspect.getfile(fitbenchmarking))
    template_dir = os.path.join(root, "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    css = get_css(options, group_dir)
    template = env.get_template("problem_index_page.html")
    output_file = os.path.join(group_dir, f"{group_name}_index.html")
    links = [v + "html" for v in table_names.values()]
    names = table_names.keys()
    description = [table_descriptions[n] for n in names]
    run_name = f"{options.run_name}: " if options.run_name else ""

    with open(output_file, "w", encoding="utf-8") as fh:
        fh.write(
            template.render(
                css_style_sheet=css["main"],
                custom_style=css["custom"],
                mathjax=js["mathjax"],
                group_name=group_name,
                table_type=names,
                links=links,
                description=description,
                run_name=run_name,
                python_version=config["python_version"],
                numpy_version=config["numpy_version"],
                zip=zip,
            )
        )


def create_index_page(
    options: Options, groups: list[str], result_directories: list[str]
) -> str:
    """
    Creates the results index page for the benchmark, and copies
    the fonts and js directories to the correct location.

    :param options: The user options for the benchmark.
    :type options: fitbenchmarking.utils.options.Options
    :param groups: Names for each of the problem set groups.
    :type groups: A list of strings.
    :param result_directories: Result directory paths for each
    problem set group.
    :type result_directories: A list of strings.
    :return: The filepath of the `results_index.html` file.
    :rtype: str
    """
    root = os.path.dirname(inspect.getfile(fitbenchmarking))
    template_dir = os.path.join(root, "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    css = get_css(options, options.results_dir)
    template = env.get_template("index_page.html")
    group_links = [
        os.path.join(d, f"{g}_index.html")
        for g, d in zip(groups, result_directories)
    ]
    output_file = os.path.join(options.results_dir, "results_index.html")

    # Copying directories into results directory
    for dir in ["fonts", "js", "css", "images"]:
        path = root if dir == "fonts" else template_dir
        copytree(
            os.path.join(path, dir),
            os.path.join(options.results_dir, dir),
            dirs_exist_ok=True,
        )

    run_name = f"{options.run_name}: " if options.run_name else ""

    with open(output_file, "w", encoding="utf-8") as fh:
        fh.write(
            template.render(
                css_style_sheet=css["main"],
                custom_style=css["custom"],
                groups=groups,
                group_link=group_links,
                run_name=run_name,
                zip=zip,
            )
        )

    return output_file


def open_browser(output_file: str, options, pp_dfs_all_prob_sets) -> None:
    """
    Opens a browser window to show the results of a fit benchmark.

    :param output_file: The absolute path to the results index file.
    :type output_file: str
    :param options: The user options for the benchmark.
    :type options: fitbenchmarking.utils.options.Options
    :param pp_dfs_all_prob_sets: For each problem set, data to create
                                 dash plots.
    :type pp_dfs_all_prob_sets: dict[str, dict[str, pandas.DataFrame]]
    """
    use_url = False
    # On Mac, need prefix for webbrowser
    if platform.system() == "Darwin":
        url = "file://" + output_file
        use_url = True
    else:
        url = output_file
    # On windows can have drive clashes so need to use absolute path
    if platform.system() == "Windows":
        use_url = True

    if options.results_browser:
        # Uses the relative path so that the browser can open on WSL
        to_open = url if use_url else os.path.relpath(output_file)
        if webbrowser.open_new(to_open):
            LOGGER.info(
                "\nINFO:\nThe FitBenchmarking results have been opened"
                " in your browser from this url:\n\n   %s",
                url,
            )
        else:
            LOGGER.warning(
                "\nWARNING:\nThe browser failed to open "
                "automatically. Copy and paste the following url "
                "into your browser:\n\n   %s",
                url,
            )
    else:
        LOGGER.info(
            "\nINFO:\nYou have chosen not to open FitBenchmarking "
            "results in your browser. You can use this link to see the"
            "results: \n\n   %s",
            url,
        )

    if options.run_dash:
        run_dash_app(options, pp_dfs_all_prob_sets)


def update_warning(solvers, max_solvers):
    """
    Give a warning if the number of solvers is above the maximum
    that can be displayed.

    :param solvers: The solvers to be plotted
    :type solvers: list[str]
    :param max_solvers: Maximum number of solvers that can be plotted
    :type max_solvers: int

    :return: The warning
    :rtype: str
    """
    return (
        (
            "The plot is showing the max number of minimizers "
            f"allowed ({max_solvers}). Deselect some to select others."
        )
        if len(solvers) >= max_solvers
        else ""
    )


def check_max_solvers(opts, solvers, max_solvers):
    """
    Check number of solvers and update the options to display in the
    dropdown.

    :param opts: The options for the dropdown to be updated
    :type opts: dict[str]
    :param solvers: The solvers to be plotted
    :type solvers: list[str]
    :param max_solvers: Maximum number of solvers that can be plotted
    :type max_solvers: int

    :return: Options to display in the dropdown
    :rtype: dict[str]
    """
    for opt in opts:
        opt["disabled"] = len(solvers) >= max_solvers
    return opts


def display_page(
    pathname: str,
    profile_instances_all_groups: "dict[str, dict[str, DashPerfProfile]]",
    layout: "list",
    max_solvers: int,
    run_id: str,
):
    """
    Update the layout of the dash app.

    :param pathname: The link to the page with the Dash plot
    :type pathname: str
    :param profile_instances_all_groups: The data to be plotted
    :type profile_instances_all_groups: dict[str[dict]]
    :param layout: Layout of the Dash app
    :type layout: list of dcc or html components
    :param max_solvers: Maximum number of solvers that can be plotted
    :type max_solvers: int
    :param run_id: The id for the run that is plotted in dash
    :type run_id: str

    :return: The updated layout
    :rtype: html.Div
    """

    try:
        _, plot_id, group, plot, metric_str = pathname.split("/")
    except ValueError:
        return (
            "404 Page Error! Path does not have the expected format. "
            "Please provide it in the following form:  \n"
            "ip-address:port/run_id/problem_set/plot/performance_profile."
        )

    if run_id != plot_id:
        return (
            "404 Page Error! Dash plots are not available for these results."
            "You can use `fitbenchmarking --load-checkpoint` to fix this."
        )
    if plot != "pp":
        return f"404 Page Error! Plot type '{plot}' not available."

    group_profiles = profile_instances_all_groups[group]

    new_layout = layout

    try:
        first_metric = True
        current_styles = {}
        avail_styles = []
        for metric in metric_str.split("+"):
            if first_metric:
                current_styles = group_profiles[metric].current_styles
                avail_styles = group_profiles[metric].avail_styles
                first_metric = False
            else:
                group_profiles[metric].current_styles = current_styles
                group_profiles[metric].avail_styles = avail_styles

            new_layout = [*new_layout, group_profiles[metric].layout()]
    except KeyError:
        return (
            "404 Page Error! The path was not recognized. \n"
            "The path needs to end in a list of table names "
            "separated by '+'."
        )

    opts = group_profiles["acc"].default_opt

    layout[1].options = opts
    layout[1].value = [i["label"] for i in opts[:max_solvers]]
    return html.Div(new_layout)


def run_dash_app(options, pp_dfs_all_prob_sets) -> None:
    """
    Runs the Dash app to produce the interactive performance profile
    plots.

    :param options: The user options for the benchmark.
    :type options: fitbenchmarking.utils.options.Options
    :param pp_dfs_all_prob_sets: For each problem set, data to create
                                 dash plots.
    :type pp_dfs_all_prob_sets: dict[str, dict[str, pandas.DataFrame]]
    """

    layout = [
        dcc.RadioItems(
            id="Log axis toggle",
            options=["Log x-axis", "Linear x-axis"],
            value="Log x-axis",
            labelStyle={
                "margin-top": "1.5rem",
                "margin-left": "1rem",
                "margin-right": "1rem",
                "margin-bottom": "0.8rem",
            },
            style={
                "display": "flex",
                "font-family": "verdana",
                "color": "#454545",
                "font-size": "14px",
            },
        ),
        dcc.Dropdown(
            id="dropdown",
            multi=True,
            style={
                "font-family": "verdana",
                "color": "#454545",
                "font-size": "14px",
                "margin-bottom": "1rem",
                "margin-top": "1rem",
            },
        ),
        html.Div(
            id="warning",
            style={
                "white-space": "pre-wrap",
                "font-family": "verdana",
                "color": "red",
                "text-align": "center",
                "font-size": "13px",
                "margin-bottom": "1rem",
                "margin-top": "1rem",
            },
        ),
    ]

    profile_instances_all_groups = {}
    for group, pp_dfs in pp_dfs_all_prob_sets.items():
        inst = {
            "acc": DashPerfProfile(
                profile_name="Accuracy", pp_df=pp_dfs["acc"], group_label=group
            ),
            "runtime": DashPerfProfile(
                profile_name="Runtime",
                pp_df=pp_dfs["runtime"],
                group_label=group,
            ),
            "energy": DashPerfProfile(
                profile_name="Energy Usage",
                pp_df=pp_dfs["energy_usage"],
                group_label=group,
            ),
        }
        profile_instances_all_groups[group] = inst

    # Needed to prevent unnecessary warning in the terminal
    # 'werkzeug' is the name of the logger used by dash
    log = logging.getLogger("werkzeug")
    log.disabled = True

    app = Dash(__name__, suppress_callback_exceptions=True)

    app.layout = html.Div(
        [
            dcc.Location(id="url", refresh=False),
            html.Div(id="page-content", children=[]),
        ]
    )

    max_solvers = 15

    app.callback(Output("warning", "children"), [Input("dropdown", "value")])(
        lambda x: update_warning(x, max_solvers=max_solvers)
    )

    app.callback(
        Output("dropdown", "options"),
        [Input("dropdown", "options"), Input("dropdown", "value")],
    )(lambda x, y: check_max_solvers(x, y, max_solvers=max_solvers))

    # Create the callback to handle multiple pages
    app.callback(
        Output("page-content", "children"), [Input("url", "pathname")]
    )(
        lambda x: display_page(
            x,
            profile_instances_all_groups=profile_instances_all_groups,
            layout=layout,
            max_solvers=max_solvers,
            run_id=options.run_id,
        )
    )

    app.run(port=options.port)
