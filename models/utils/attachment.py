from .. import Attachment


def to_attachment(objs: list[dict] | None) -> list[Attachment] | None:
    if objs == None:
        return None

    attachments: list[Attachment] = []
    for attachment in objs:
        id = attachment['id']
        name = attachment['file_name']
        file_type = attachment['file_type']
        file = attachment['file_blob']
        attachments.append(Attachment(id=id,
                                      name=name,
                                      blob=file,
                                      type=file_type))

    return attachments
