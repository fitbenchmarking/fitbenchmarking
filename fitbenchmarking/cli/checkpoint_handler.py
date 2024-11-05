"""
This is a command line tool for handling checkpoint files for the
FitBenchmarking software package.
For more information on usage type fitbenchmarking --help
or for more general information, see the online docs at
docs.fitbenchmarking.com.
"""

import json
import os
import sys
import textwrap
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from fitbenchmarking.cli.exception_handler import exception_handler
from fitbenchmarking.core.results_output import (
    create_index_page,
    open_browser,
    save_results,
)
from fitbenchmarking.utils.checkpoint import Checkpoint
from fitbenchmarking.utils.options import find_options_file


def get_parser() -> ArgumentParser:
    """
    Creates and returns a parser for the args.

    :return: Configured argument parser
    :rtype: ArgumentParser
    """

    description = (
        "This is a tool for working with checkpoint files generated during a "
        "FitBenchmarking run."
    )

    parser = ArgumentParser(
        prog="fitbenchmarking-cp",
        add_help=True,
        description=description,
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-d",
        "--debug-mode",
        default=False,
        action="store_true",
        help="Enable debug mode (prints traceback).",
    )

    subparsers = parser.add_subparsers(
        metavar="ACTION",
        dest="subprog",
        help=(
            "Which action should be performed? "
            "For more information on options use "
            "`fitbenchmarking-cp ACTION -h`"
        ),
    )

    report_epilog = textwrap.dedent("""
    Usage Examples:

        $ fitbenchmarking-cp report
        $ fitbenchmarking-cp report -o examples/options_template.ini
        $ fitbenchmarking-cp report -f results/checkpoint
    """)
    report = subparsers.add_parser(
        "report",
        description="Generate a report from a checkpoint file",
        help="Generate a report from a checkpoint file",
        epilog=report_epilog,
    )
    report.add_argument(
        "-f",
        "--filename",
        metavar="CHECKPOINT_FILE",
        default="",
        help=(
            "The path to a fitbenchmarking checkpoint file. "
            "If omitted, this will be taken from the options file."
        ),
    )
    report.add_argument(
        "-o",
        "--options-file",
        metavar="OPTIONS_FILE",
        default="",
        help="The path to a fitbenchmarking options file",
    )

    merge_epilog = textwrap.dedent("""
    Usage Examples:

        $ fitbenchmarking-cp merge -f old_results/checkpoint.json \
to_add/checkpoint.json
        $ fitbenchmarking-cp merge -f cp1 cp2 cp3 cp4 -o \
new_results/checkpoint.json
    """)
    merge_parser = subparsers.add_parser(
        "merge",
        description="Merge multiple checkpoint files into one",
        help="Merge multiple checkpoint files into one",
        epilog=merge_epilog,
    )
    merge_parser.add_argument(
        "-f",
        "--files",
        metavar="FILES",
        nargs="+",
        help="The checkpoint files to merge",
    )
    merge_parser.add_argument(
        "-o",
        "--output-filename",
        metavar="OUTPUT",
        default="checkpoint.json",
        help="The name of the merged checkpoint file",
    )
    merge_parser.add_argument(
        "-s",
        "--strategy",
        metavar="STRATEGY",
        default="first",
        choices=["first", "last", "accuracy", "runtime", "emissions"],
        help=(
            "The merge strategy to use when dealing with conflicts. "
            "Selecting accuracy, emissions, or runtime will select for the "
            "lowest from conflicting runs."
        ),
    )
    return parser


@exception_handler
def generate_report(options_file="", additional_options=None, debug=False):
    """
    Generate the fitting reports and tables for a checkpoint file.

    :param options_file: Path to an options file, defaults to ''
    :type options_file: str, optional
    :param additional_options: Extra options for the reporting.
                               Available keys are:
                                   filename (str): The checkpoint file to use.
    :type additional_options: dict, optional
    """
    if additional_options is None:
        additional_options = {}

    options = find_options_file(
        options_file=options_file, additional_options=additional_options
    )

    checkpoint = Checkpoint(options=options)
    results, unselected_minimizers, failed_problems = checkpoint.load()

    all_dirs = []
    pp_dfs_all_prob_sets = {}
    for label in results:
        directory, pp_dfs = save_results(
            group_name=label,
            results=results[label],
            options=options,
            failed_problems=failed_problems[label],
            unselected_minimizers=unselected_minimizers[label],
        )

        pp_dfs_all_prob_sets[label] = pp_dfs

        directory = os.path.relpath(path=directory, start=options.results_dir)
        all_dirs.append(directory)

    index_page = create_index_page(options, list(results), all_dirs)
    open_browser(index_page, options, pp_dfs_all_prob_sets)


@exception_handler
def merge_data_sets(
    files: list[str],
    output: str,
    strategy: str = "first",
    debug: bool = False,
):
    """
    Combine multiple checkpoint files into one following these rules:
     1) The output will be the same as combining them one at a time in
        sequence. i.e. A + B + C = (A + B) + C
        The rules from here on will only reference A and B as the relation is
        recursive.
     2) Datasets
         2a) Datasets in A and B are identical if they agree on the label
         2b) If A and B contain identical datasets, the problems and results
             are combined as below.
             The remainder of these rules assume that A and B are identical
             datasets as the alternative is trivial.
     3) Problems
         3a) If problems in A and B agree on name, ini_params, ini_y, x, y,
             and e then these problems are considered identical.
         3b) If A and B share identical problems, the details not specified in
             3a are taken from A.
         3c) If problems in A and B are not identical but share a name, the
             name of the project in B should be updated to "<problem_name>*".
     4) Results
         4a) If results in A and B have identical problems and agree on name,
             software_tag, minimizer_tag, jacobian_tag, hessian_tag, and
             costfun_tag they are considered identical.
         4b) If A an B share identical results, the details not specified in 4a
             are taken from A if strategy is 'first', or B if strategy is
             'last'.
     5) As tables are grids of results, combining arbitrary results can lead to
        un-table-able checkpoint files.
        This occurs when the problems in A and B are not all identical and the
        set of combinations of software_tag, minimizer_tag, jacobian_tag,
        hessian_tag, and costfun_tag for which there are results in each of A
        and B are not identical.
        E.g. B has a problem not in A and uses a minimizer for which there are
             no results in A.
         5a) If the resulting checkpoint file would have the above issue, the
             checkpoints are incompatible.
         5b) Incompatible checkpoint files can be combined but should raise
             warnings and mark the dataset in the checkpoint file.
             Note: Some datasets may be incompatible where others can be
                   successfully combined.
     6) Unselected minimizers and failed problems will be discarded when
        combining.

    :param files: The files to combine.
    :type files: list[str]
    :param output: The name for the new checkpoint file.
    :type output: str
    :param strategy: The stategy for merging identical elements.
                     Options are 'first' or 'last'.
    :type strategy: str
    :param debug: Enable debugging output.
    :type debug: bool
    """
    if len(files) < 2:
        return

    print(f"Loading {files[0]}...")
    with open(files[0], encoding="utf-8") as f:
        A = json.load(f)
    for to_merge in files[1:]:
        print(f"Merging {to_merge}...")
        with open(to_merge, encoding="utf-8") as f:
            B = json.load(f)
        A = merge(A, B, strategy=strategy)

    print(f"Writing to {output}...")
    with open(output, "w", encoding="utf-8") as f:
        json.dump(A, f, indent=2)


def merge(A, B, strategy):
    """
    Merge the results from A and B
    This function can corrupt A and B, they should be discarded after calling.

    :param A: The first set of results to merge
    :type A: dict[str, list[FittingResult]]
    :param B: The set to merge into A
    :type B: dict[str, list[FittingResult]]
    :param strategy: The strategy to use to merge the results
    :type strategy: str

    :return: The merged checkpoint data.
    :rtype: dict[str, any]
    """
    if strategy == "last":
        A, B = B, A
    for k in B:
        if k not in A:
            A[k] = B[k]
            continue
        A[k]["problems"], update_names = merge_problems(
            A[k]["problems"], B[k]["problems"]
        )
        if update_names:
            for r in B[k]["results"]:
                if r["name"] in update_names:
                    r["name"] = update_names[r["name"]]
        A[k]["results"] = merge_results(
            A[k]["results"], B[k]["results"], strategy=strategy
        )
        A[k]["failed_problems"] = []
        A[k]["unselected_minimisers"] = {
            r["software_tag"]: [] for r in A[k]["results"]
        }

    return A


def merge_problems(A: dict[str, dict], B: dict[str, dict]):
    """
    Merge the problem sections of 2 checkpoint files.
    If problems have matching names but different values, the problem from
    B will be suffixed with a "*".

    In some cases this could lead to problems with several "*"s although this
    seems unlikely for most use cases.

    :param A: The first checkpoint problems dict to merge
    :type A: dict[str, dict]
    :param B: The second checkpoint problems dict to merge
    :type B: dict[str, dict]

    :return: The merged checkpoint problems and a list of problems that have
             been renamed
    :rtype: tuple[dict[str, dict[str, any]], list[str]]
    """
    update_keys = {}
    for k, prob in B.items():
        # Handle case where A/B contains k, k*, k**, ... from previous merges
        orig_k = k
        k = k.rstrip("*")
        prob["name"] = prob["name"].rstrip("*")
        prob["problem_tag"] = prob["problem_tag"].rstrip("*")
        while k in A:
            A_prob = A[k]
            # Identical - take problem from A
            if (
                A_prob["ini_params"] == prob["ini_params"]
                and A_prob["ini_y"] == prob["ini_y"]
                and A_prob["x"] == prob["x"]
                and A_prob["y"] == prob["y"]
                and A_prob["e"] == prob["e"]
            ):
                if orig_k != k:
                    update_keys[orig_k] = k
                break

            # Agree on name but aren't identical
            name_change = "{}*"
            k = name_change.format(k)
            prob["name"] = name_change.format(prob["name"])
            prob["problem_tag"] = name_change.format(prob["problem_tag"])

        else:  # k not in A (no break called)
            A[k] = prob
            if orig_k != k:
                update_keys[orig_k] = k
            continue

    return A, update_keys


def merge_results(A: list[dict], B: list[dict], strategy: str):
    """
    Merge the results sections of 2 checkpoint files.

    :param A: The first checkpoint results list to merge
    :type A: list[dict[str, any]]
    :param B: The second checkpoint results list to merge
    :type B: list[dict[str, any]]
    :param strategy: The merge strategy (which one to take in the case of
                     conflicts)
    :type strategy: str

    :return: Merged results list
    :rtype: list[dict[str, any]]
    """

    def key_gen(k: dict):
        """
        Get a uid for a result entry in cp file.
        """
        return (
            k["name"],
            k["software_tag"],
            k["minimizer_tag"],
            k["jacobian_tag"],
            k["hessian_tag"],
            k["costfun_tag"],
        )

    A_key = {key_gen(r): i for i, r in enumerate(A)}

    for res in B:
        key = key_gen(res)
        if key in A_key:
            if (
                strategy in ["accuracy", "emissions", "runtime"]
                and A[A_key[key]][strategy] > res[strategy]
            ):
                A[A_key[key]] = res
        else:
            A_key[key] = len(A)
            A.append(res)

    return A


def main():
    """
    Entry point exposed as the `fitbenchmarking-cp` command.
    """
    parser = get_parser()

    args = parser.parse_args(sys.argv[1:])

    additional_options = {}

    if args.subprog == "report":
        if args.filename:
            additional_options["checkpoint_filename"] = args.filename
        generate_report(
            args.options_file, additional_options, debug=args.debug_mode
        )
    elif args.subprog == "merge":
        merge_data_sets(
            files=args.files,
            output=args.output_filename,
            strategy=args.strategy,
            debug=args.debug_mode,
        )


if __name__ == "__main__":
    main()
