def validate_message(str: str, separators: list[str], source_separator: str = ":") -> bool:
    start = str.find(source_separator, 0)
    # find source
    if start != -1:
        # find objects (strings of task or sentence)
        for sp in separators:
            if str.find(sp, start) != -1:
                return True
    return False
