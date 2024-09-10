"""
Functions used for debugging and printing information in a readable format.
"""


def get_printable_table(class_name: str, class_info: dict) -> str:
    """
    Creates and returns a string displaying the class info in a
    format that is easily read in a table.

    :param class_name: The name of a class owning the data.
    :type class_name: str
    :param class_info: The data in the class to display.
    :type class_info: dict{str: variant}

    :return: The class info in a readable format.
    :rtype: str
    """
    max_key = max([len(k) for k in class_info.keys()])
    max_value = max([len(str(v)) for v in class_info.values()])

    header_separator = f"+{'=' * (max_key + max_value + 5)}+"
    row_separator = header_separator.replace("=", "-")

    rows = [header_separator,
            f"| {class_name}"
            f"{' ' * (max_key + max_value - len(class_name) + 4)}|",
            header_separator]

    for key, value in class_info.items():
        row = f"| {key}{' ' * (max_key - len(key))} | " \
              f"{value}{' ' * (max_value - len(str(value)))} |"
        rows.append(row)
        rows.append(row_separator)

    return "\n".join(rows)
