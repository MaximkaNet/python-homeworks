from .utils import trim


def string_parser(
    string: str,
    separators: list[str],
    source_separator: str = ":"
) -> tuple[str, dict[str, list]]:
    """
    return value:
    (source, data_vars)
    """
    string = trim(string)
    # find source
    end_source_index = string.find(source_separator)
    source = string[0:end_source_index]

    data_vars: dict[str, list] = {}
    for sp in separators:
        data_vars[f"{sp}"] = []

    # find records
    start_index = end_source_index
    str_length = len(string)
    start_pos, sp = find_closest_separator(
        string,
        separators, start_index)

    while start_index != str_length:
        # closest start separator
        end_pos, end_sp = find_closest_separator(
            string,
            separators,
            start_pos + len(sp))

        if end_pos == -1:
            data_vars[sp].append(
                string[start_pos + len(sp):str_length].strip())
            break

        # separators
        data_vars[sp].append(string[start_pos + len(sp):end_pos].strip())
        start_pos = end_pos
        sp = end_sp
        start_index = end_pos

    return (source, data_vars)


def find_closest_separator(
    string: str,
    separators: list[str],
    start_index: int = 0
) -> tuple[int, str]:
    """
    return value:
    (position, separator)
    """

    closest_sp = ""
    min_pos = len(string)

    for sp in separators:
        sp_pos = string.find(sp, start_index)
        if 0 < sp_pos < min_pos:
            min_pos = sp_pos
            closest_sp = sp

    return (min_pos, closest_sp) if closest_sp != "" else (-1, None)
