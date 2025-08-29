from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.text import Const
from bot.states import StartSG

from src.api.endpoints.my_characters import Mycharacters
from src.bot.states.test import TestSG

CHARACTER_NAME = "A0ua"

async def go_back(
    callback: CallbackQuery, button: Button, manager: DialogManager
) -> None:
    await manager.switch_to(StartSG.main)


async def move_up(
    callback: CallbackQuery, button: Button, manager: DialogManager
) -> None:
    character = Mycharacters(http_client=)


start_window = Window(
    Const("Test menu:"),
    Button(Const("⬆️"), "0", move_up),
    Row(
        Button(Const("⬅️"), "1", move_left),
        Button(Const("⬇️"), "2", move_down),
        Button(Const("➡️"), "3", move_right),
    ),
    Button(Const("Back"), "back", go_back),
    state=TestSG.main,
)
