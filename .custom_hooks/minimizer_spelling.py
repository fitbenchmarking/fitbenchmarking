#!/usr/bin/env python3

import re
import sys
from pathlib import Path

INVALID_WORDS = frozenset({"minimiser", "solver"})  # ignore: spelling
VALID_SPELLING = "minimizer"
IGNORE_STRING = "# ignore: spelling"

#: Names which contain an invalid word but cannot be renamed, either because
#: they belong to a third party API or because they are part of the public
#: FitBenchmarking interface.
ALLOWED_NAMES = re.compile(
    # FitBenchmarking controller attributes, documented in
    # docs/source/extending/controllers.rst and set by external controllers.
    r"_enabled_solvers"
    # The Ceres Solver library, and its python bindings.
    r"|[Cc]eres[- ]?[Ss]olver"
    r"|Solver(Options|Summary)"  # ignore: spelling
    r"|[Ll]inear[_]?[Ss]olver[_]?[Tt]ype",  # ignore: spelling
)
MASK_CHAR = "-"


def mask_allowed_names(line: str) -> str:
    """
    Blank out any allowed names so that the invalid words they contain are
    not reported. The length of the line is preserved so that the position of
    any remaining invalid word still lines up with the original text.

    :param line: The line of text to mask
    :type line: str

    :return: The line with allowed names replaced by MASK_CHAR
    :rtype: str
    """
    return ALLOWED_NAMES.sub(lambda m: MASK_CHAR * len(m.group()), line)


def find_invalid_word(line: str) -> tuple[int, str] | None:
    if IGNORE_STRING.casefold() in line.casefold():
        return None

    lowercase_text = mask_allowed_names(line).lower()

    for word in INVALID_WORDS:
        index = lowercase_text.find(word)
        if index != -1:
            return index, word

    return None


def process_file(file_contents: str, filename: str) -> str | None:

    matches = []
    for line_num, line_text in enumerate(file_contents.splitlines(), start=1):
        match = find_invalid_word(line_text)

        if match is not None:
            word_start, invalid_word = match
            matches.append((invalid_word, line_num, line_text, word_start))

    if len(matches) > 0:
        error_text = (
            f"Error while checking: {filename}\n\n"
            f"The following text contains invalid word(s):\n"
            f"the preferred spelling is '{VALID_SPELLING}'.\n\n"
        )

        error_text += "\n".join(
            [
                (
                    f"{line_num}: {line_text}\n"
                    f"{' ' * (len(str(line_num)) + 2 + word_start)}"
                    f"{'^' * len(invalid_word)}\n"
                )
                for invalid_word, line_num, line_text, word_start in matches
            ]
        )

        error_text += f"Add '{IGNORE_STRING}' to skip this check"

        return error_text

    return None


def main() -> None:
    """
    Search each file provided on the command line for text containing words
    listed in INVALID_WORDS.

    Exits with status code 1 if an invalid word is found, otherwise 0.
    """
    has_errors = False
    for filename in sys.argv[1:]:
        try:
            file_contents = Path(filename).read_text()
        except OSError as exc:
            raise RuntimeError(f"could not open file: {exc}") from exc

        error = process_file(file_contents, filename)
        if error is not None:
            print(error, file=sys.stderr)
            has_errors = True

    if has_errors:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
