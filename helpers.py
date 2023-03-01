from aiogram.utils.callback_data import CallbackData
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import utils

week_days_callback = CallbackData("week_days", "act", "day")


class SelectWeekDays:
    week_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    def __init__(self, selected_days: list[int] = []) -> None:
        self.selected_days = selected_days

    def get_kb(self):
        ikb = InlineKeyboardMarkup(row_width=7)
        ikb.row()
        for name in self.week_days:
            ikb.insert(InlineKeyboardButton(
                name,
                callback_data=week_days_callback.new("SELECT", name)
            ))
        ikb.row()
        ikb.insert(InlineKeyboardButton(
            "Confirm",
            callback_data=week_days_callback.new("CONFIRM", -1)
        ))
        return ikb

    async def start(self):
        return self.get_kb()

    def print(self):
        self.selected_days.sort()
        converted_week = utils.convert_week(self.selected_days)
        string = "Selected days: "
        string += ", ".join(map(str, converted_week))
        return string

    async def process_select(self, query: CallbackQuery, data: CallbackData):
        return_data = (False, None)
        if data["act"] == "SELECT":
            if data["day"] == "Mon":
                if 0 in self.selected_days:
                    self.selected_days.remove(0)
                else:
                    self.selected_days.append(0)
                await query.message.edit_text(
                    self.print(), reply_markup=self.get_kb())
            if data["day"] == "Tue":
                if 1 in self.selected_days:
                    self.selected_days.remove(1)
                else:
                    self.selected_days.append(1)
                await query.message.edit_text(
                    self.print(), reply_markup=self.get_kb())
            if data["day"] == "Wed":
                if 2 in self.selected_days:
                    self.selected_days.remove(2)
                else:
                    self.selected_days.append(2)
                await query.message.edit_text(
                    self.print(), reply_markup=self.get_kb())
            if data["day"] == "Thu":
                if 3 in self.selected_days:
                    self.selected_days.remove(3)
                else:
                    self.selected_days.append(3)
                await query.message.edit_text(
                    self.print(), reply_markup=self.get_kb())
            if data["day"] == "Fri":
                if 4 in self.selected_days:
                    self.selected_days.remove(4)
                else:
                    self.selected_days.append(4)
                await query.message.edit_text(
                    self.print(), reply_markup=self.get_kb())
            if data["day"] == "Sat":
                if 5 in self.selected_days:
                    self.selected_days.remove(5)
                else:
                    self.selected_days.append(5)
                await query.message.edit_text(
                    self.print(), reply_markup=self.get_kb())
            if data["day"] == "Sun":
                if 6 in self.selected_days:
                    self.selected_days.remove(6)
                else:
                    self.selected_days.append(6)
                await query.message.edit_text(
                    self.print(), reply_markup=self.get_kb())
        elif data["act"] == "CONFIRM":
            await query.message.delete_reply_markup()
            return_data = (True, self.selected_days)
        return return_data
