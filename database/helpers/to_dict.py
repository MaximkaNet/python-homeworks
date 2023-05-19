def to_dict(
    tuples: list[tuple],
    schema: list[str] = ['id']
) -> list[dict] | None:
    """
    Return dict converted from tuple object 
    """
    res: list = []
    for tuple in tuples:
        obj = {}
        for i, row in enumerate(schema):
            obj[row] = tuple[i]
        res.append(obj)

    if len(res) == 0:
        return None
    return res
