from datetime import date
from config.formats import DATE_FORMAT


def show_selected_wrapper(_body: str, _date: date) -> str:
    WRAPP = f"""
    {_body}
_Selected date: {_date.strftime("%A")} ({_date.strftime(DATE_FORMAT)})_
    """
    return WRAPP


def show_add_wrapper(_body: str, _date: date) -> str:
    WRAPP = f"""
    {_body}
_Added: {_date.strftime("%A")} ({_date.strftime(DATE_FORMAT)})_
    """
    return WRAPP


def show_updated_wrapper(_body: str, _date: date) -> str:
    WRAPP = f"""
    {_body}
_Updated at: {_date.strftime("%A")} ({_date.strftime(DATE_FORMAT)})_
    """
    return WRAPP
