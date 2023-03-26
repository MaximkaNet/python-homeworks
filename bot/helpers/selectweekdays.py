from aiogram.utils.callback_data import CallbackData
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.callbacks.selectweekdays import week_days_callback
from bot.utils import convert_week


class SelectWeekDays:
    week_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    def __init__(self, selected_days: list[int] = []) -> None:
        self.selected = selected_days

    async def _get_kb(self, callback_data: CallbackData):
        ikb = InlineKeyboardMarkup(row_width=7)
        ikb.row()
        for name in self.week_days:
            days = self.get_callback_days(callback_data)
            ikb.insert(InlineKeyboardButton(
                name,
                callback_data=week_days_callback.new(
                    "SELECT", name, *days)
            ))
        days = self.get_callback_days(callback_data)
        ikb.row()
        ikb.insert(InlineKeyboardButton(
            "Confirm",
            callback_data=week_days_callback.new(
                "CONFIRM", -1, *days)
        ))
        return ikb

    async def start(self, work_days: list[int] = []) -> InlineKeyboardMarkup:
        init_days = [False, False, False, False, False, False, False]
        # init work days
        if len(work_days):
            current = 0
            for i, item in enumerate(init_days):
                if i == work_days[current]:
                    init_days[i] ^= True
                    if current < len(work_days)-1:
                        current += 1

        ikb = InlineKeyboardMarkup(row_width=7)
        ikb.row()
        for name in self.week_days:
            ikb.insert(InlineKeyboardButton(
                name,
                callback_data=week_days_callback.new(
                    "SELECT", name, *init_days)
            ))
        ikb.row()
        ikb.insert(InlineKeyboardButton(
            "Confirm",
            callback_data=week_days_callback.new(
                "CONFIRM", -1, False, False, False, False, False, False, False)
        ))
        return ikb

    def print(self, selected: list[int]) -> str:
        converted_week = convert_week(selected)
        string = "Selected days: "
        string += ", ".join(map(str, converted_week))
        return string

    def toggle_day(self, callback_data: CallbackData, day: str) -> CallbackData:
        callback_data[day.lower()] = 'True' if callback_data[day.lower()
                                                             ] == 'False' else 'False'
        return callback_data

    def get_callback_days(self, callback_data: CallbackData) -> list[bool]:
        return [callback_data["mon"], callback_data["tue"], callback_data["wed"],
                callback_data["thu"], callback_data["fri"], callback_data["sat"], callback_data["sun"]]

    def to_int(self, arr: list[bool]) -> list[str]:
        return [i for i, item in enumerate(arr) if item == 'True']

    async def process_select(self, query: CallbackQuery, data: CallbackData) -> tuple[bool, list]:
        return_data = (False, None)
        if data["act"] == "SELECT":
            toggled_days = self.toggle_day(data, data["day"])
            await query.message.edit_text(
                self.print(self.to_int(self.get_callback_days(toggled_days))),
                reply_markup=await self._get_kb(toggled_days))
        elif data["act"] == "CONFIRM":
            await query.message.delete_reply_markup()
            return_data = (True,  self.to_int(self.get_callback_days(data)))
        return return_data
