"""
Functions that create the tables, support pages, figures, and indexes.
"""
import inspect
import os
import re
from shutil import copy2

import docutils
from jinja2 import Environment, FileSystemLoader

import fitbenchmarking
from fitbenchmarking.results_processing import (performance_profiler, plots,
                                                problem_summary_page,
                                                support_page, tables)
from fitbenchmarking.utils import create_dirs
from fitbenchmarking.utils.exceptions import PlottingError
from fitbenchmarking.utils.misc import get_css, get_js


def save_results(options, results, group_name, failed_problems,
                 unselected_minimzers):
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
    :params unselected_minimzers: Dictionary containing unselected minimizers
                                  based on the algorithm_type option
    :type unselected_minimzers: dict

    :return: Path to directory of group results
    :rtype: str
    """
    group_dir, supp_dir, fig_dir, local_css_dir = \
        create_directories(options, group_name)

    # copy the template css files into a subfolder of results
    root = os.path.dirname(inspect.getfile(fitbenchmarking))
    template_dir = os.path.join(root, 'templates')
    local_css_dir = os.path.join(options.results_dir, 'css')
    for css_file in ["main_style", "custom_style", "table_style"]:
        copy2(os.path.join(template_dir, css_file + ".css"), local_css_dir)

    best_results, results_dict = preprocess_data(results)

    pp_locations = performance_profiler.profile(results_dict, fig_dir)

    if options.make_plots:
        create_plots(options, results_dict, best_results, fig_dir)

    support_page.create(options=options,
                        results_per_test=results,
                        group_name=group_name,
                        support_pages_dir=supp_dir)
    problem_summary_page.create(options=options,
                                results=results_dict,
                                best=best_results,
                                group_name=group_name,
                                support_pages_dir=supp_dir,
                                figures_dir=fig_dir)

    table_names, table_descriptions = \
        tables.create_results_tables(options,
                                     results_dict,
                                     best_results,
                                     group_name,
                                     group_dir,
                                     fig_dir,
                                     pp_locations,
                                     failed_problems,
                                     unselected_minimzers)

    create_problem_level_index(options,
                               table_names,
                               group_name,
                               group_dir,
                               table_descriptions)

    return group_dir


def create_directories(options, group_name):
    """
    Create the directory structure ready to store the results

    :param options: The options used in the fitting problem and plotting
    :type options: fitbenchmarking.utils.options.Options
    :param group_name: name of the problem group
    :type group_name: str
    :return: paths to the top level results, group results, support pages,
             and figures directories
    :rtype: (str, str, str, str)
    """
    results_dir = create_dirs.results(options.results_dir)
    group_dir = create_dirs.group_results(results_dir, group_name)
    support_dir = create_dirs.support_pages(group_dir)
    figures_dir = create_dirs.figures(support_dir)
    local_css_dir = create_dirs.css(options.results_dir)
    return group_dir, support_dir, figures_dir, local_css_dir


def preprocess_data(results):
    """
    Generate a dictionary of results lists sorted into the correct order
    with rows and columns as the key and list elements respectively.

    This is used to create HTML and txt tables.
    This is stored in self.sorted_results

    :param results: Theresults to process
    :type results: list[fitbenchmarking.utils.fitbm_result.FittingResult]

    :return: The best result grouped by row and category (cost function),
             The sorted results grouped by row and category
    :rtype: dict[str, dict[str, utils.fitbm_result.FittingResult]],
            dict[str, dict[str, list[utils.fitbm_result.FittingResult]]]
    """

    # Might be worth breaking out into an option in future.
    # sort_order[0] is the order of sorting for rows
    # sort_order[1] is the order of sorting for columns
    sort_order = (['problem'],
                  ['software', 'minimizer', 'jacobian', 'hessian'])

    # Additional separation for categories within columns
    col_sections = ['costfun']

    # Generate the columns and row tags and sort
    rows = set()
    columns = {}
    for r in results:
        # Error 4 means none of the jacobians ran so can't infer the
        # jacobian names from this.
        if r.error_flag == 4:
            continue
        result_tags = {
            'row': '',
            'col': '',
            'cat': ''
        }
        for tag, order in [('row', sort_order[0]),
                           ('col', sort_order[1]),
                           ('cat', col_sections)]:
            for sort_pos in order:
                result_tags[tag] += f':{getattr(r, sort_pos + "_tag")}'
            result_tags[tag] = result_tags[tag].strip(':')

        rows.add(result_tags['row'])
        cat = result_tags['cat']
        if cat not in columns:
            columns[cat] = set()
        columns[cat].add(result_tags['col'])

    rows = sorted(rows, key=str.lower)
    # Reorder keys and assign columns to indexes within them
    columns = {k: {col: i for i, col in enumerate(sorted(columns[k],
                                                         key=str.lower))}
               for k in sorted(iter(columns.keys()), key=str.lower)}

    # Build the sorted results dictionary
    sorted_results = {r.strip(':'): {k: [None for _ in category]
                                     for k, category in columns.items()}
                      for r in rows}

    for r in results:
        result_tags = {
            'row': '',
            'col': '',
            'cat': ''
        }
        for tag, order in [('row', sort_order[0]),
                           ('col', sort_order[1]),
                           ('cat', col_sections)]:
            for sort_pos in order:
                if sort_pos in ['jacobian', 'hessian'] and r.error_flag == 4:
                    result_tags[tag] += ':.+'
                else:
                    result_tags[tag] += f':{getattr(r, sort_pos + "_tag")}'
            result_tags[tag] = result_tags[tag].strip(':')

        # Fix up cells where error flag = 4
        if r.error_flag == 4:
            match_rows = [match
                          for match in rows
                          if re.fullmatch(result_tags['row'], match)]
            match_cats = [match
                          for match in columns.keys()
                          if re.fullmatch(result_tags['cat'], match)]
            for row in match_rows:
                for cat in match_cats:
                    match_cols = [match for match in columns[cat]
                                  if re.fullmatch(result_tags['col'], match)]
                    for col in match_cols:
                        col = columns[col]
                        sorted_results[row][col] = r
        else:
            col = columns[result_tags['cat']][result_tags['col']]
            sorted_results[result_tags['row']][result_tags['cat']][col] = r

    # Find best results
    best_results = {}
    for r, row in sorted_results.items():
        best_results[r] = {}
        for c, cat in row.items():
            best = cat[0]
            fastest = cat[0]
            for result in cat[1:]:
                if best.chi_sq > result.chi_sq:
                    best = result
                if fastest.runtime > result.runtime:
                    fastest = result

            best.is_best_fit = True
            best_results[r][c] = best

            for result in cat:
                result.min_chi_sq = best.chi_sq
                result.min_runtime = fastest.runtime

    return best_results, sorted_results


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
        for cf, best_in_cf in best_dict.items():
            try:
                plot = plots.Plot(best_result=best_in_cf,
                                  options=options,
                                  figures_dir=figures_dir)
            except PlottingError as e:
                for result in prob_result:
                    result.figure_error = str(e)
                continue

            # Create a plot showing the initial guess and get filename
            initial_guess_path[cf] = plot.plot_initial_guess()

            # Setup best plot first
            # If none of the fits succeeded, params could be None
            # Otherwise, add the best fit to the plot
            if best_in_cf.params is not None:
                plot_path = plot.plot_best(best_in_cf.sanitised_min_name,
                                           best_in_cf.params)
                best_in_cf.figure_link = plot_path
            else:
                best_in_cf.figure_error = 'Minimizer failed to produce any ' \
                    'parameters'
            best_in_cf.start_figure_link = initial_guess_path[cf]
            plot_dict[cf] = plot

        # For each result, if it succeeded, create a plot and add plot links to
        # the resuts object
        for cf, cat_results in prob_result.items():
            for result in cat_results:
                # Don't plot best again
                if not result.is_best_fit:
                    if result.params is not None:
                        cf = result.cost_func.__class__.__name__
                        plot_path = plot_dict[cf].plot_fit(
                            result.sanitised_min_name, result.params)
                        result.figure_link = plot_path
                    else:
                        result.figure_error = 'Minimizer failed to produce any ' \
                            'parameters'
                    result.start_figure_link = initial_guess_path[cf]


def create_problem_level_index(options, table_names, group_name,
                               group_dir, table_descriptions):
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
    """
    js = get_js(options, group_dir)

    root = os.path.dirname(inspect.getfile(fitbenchmarking))
    template_dir = os.path.join(root, 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    css = get_css(options, group_dir)
    template = env.get_template("problem_index_page.html")
    output_file = os.path.join(group_dir, '{}_index.html'.format(group_name))
    links = [v + "html" for v in table_names.values()]
    names = table_names.keys()
    description = [table_descriptions[n] for n in names]
    index = table_descriptions[options.comparison_mode]
    with open(output_file, 'w', encoding="utf-8") as fh:
        fh.write(template.render(
            css_style_sheet=css['main'],
            custom_style=css['custom'],
            mathjax=js['mathjax'],
            group_name=group_name,
            index=index,
            table_type=names,
            links=links,
            description=description,
            zip=zip))
