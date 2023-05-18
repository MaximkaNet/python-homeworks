from .. import Attachment


def to_attachment(tuples: list[tuple]) -> list[Attachment] | None:
    if len(tuples) == 0:
        return None
    attachments: list[Attachment] = []
    for item in tuples:
        id = item[0]
        name = item[1]
        file_type = item[2]
        file = item[3]
        attachments.append(Attachment(id=id,
                                      name=name,
                                      blob=file,
                                      type=file_type))

    return attachments
