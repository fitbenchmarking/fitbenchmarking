#!/usr/bin/env python3

from pathlib import Path
import sys

INVALID_WORDS = frozenset({"minimiser", "solver"})
VALID_SPELLING = "minimizer"


def find_invalid_word(line: str) -> tuple[int, str] | None:
    lowercase_text = line.lower()

    for word in INVALID_WORDS:
        index = lowercase_text.find(word)
        if index != -1:
            return index, word

    return None

def process_file(file_contents: str, filename: str) -> str | None:
    for line_num, line_text in enumerate(file_contents.splitlines(), start=1):
        match = find_invalid_word(line_text)

        if match is not None:
            word_start, invalid_word = match

            return (
                f"Error while checking: {filename}\n\n"
                f"The following line was not valid because it contained "
                f"'{invalid_word}', the preferred spelling is "
                f"'{VALID_SPELLING}'.\n\n"
                f"{line_num}: {line_text}\n"
                f"{' ' * (len(str(line_num)) + 2 + word_start)}"
                f"{'^' * len(invalid_word)}\n"
            )

    return None

def main() -> None:
    """
    Search each file provided on the command line for text containing words
    listed in INVALID_WORDS.

    Exits with status code 1 if an invalid word is found, otherwise 0.

    Examples that should trigger the check:

        //minimiser
        my_var = self.get_minimiser()
    """
    for filename in sys.argv[1:]:
        try:
            file_contents = Path(filename).read_text()
        except OSError as exc:
            raise RuntimeError(f"could not open file: {exc}") from exc

        error = process_file(file_contents, filename)
        if error is not None:
            print(error, file=sys.stderr)
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()