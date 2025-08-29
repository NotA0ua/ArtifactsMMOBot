from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const
from bot.states import StartSG
from src.bot.states.test import TestSG


async def to_test(
    callback: CallbackQuery, button: Button, manager: DialogManager
) -> None:
    await manager.switch_to(TestSG.main)


# TODO: Add emojis
start_window = Window(
    Const(" Main menu:"), Button(Const("test"), "test", to_test), state=StartSG.main
)
