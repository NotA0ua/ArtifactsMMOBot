from typing import Coroutine
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.methods import DeleteWebhook
from aiogram_dialog import setup_dialogs

from src.api.client import AsyncHTTPClientProtocol
from src.config import settings

# from app.database import Database
from src.bot.handlers import setup_routers

# from src.bot.middlewares.database import DatabaseMiddleware
from src.bot.middlewares import ThrottlingMiddleware, HTTPClientMiddleware

bot = Bot(
    token=settings.bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
)

storage = MemoryStorage()
# db = Database()
dp = Dispatcher(storage=storage)


def create_startup(http_client: AsyncHTTPClientProtocol) -> Coroutine:
    async def on_startup() -> None:
        await bot(DeleteWebhook(drop_pending_updates=True))

        # await db.init_db()

        router = setup_routers()
        dp.include_routers(router)

        setup_dialogs(dp)

        # dp.update.outer_middleware(DatabaseMiddleware(db))
        dp.update.outer_middleware(HTTPClientMiddleware(http_client=http_client))

        dp.message.middleware(ThrottlingMiddleware())
        dp.callback_query.middleware(ThrottlingMiddleware())

        await bot.set_my_commands(
            [types.BotCommand(command="start", description="↪️ Restart the bot")],
            types.BotCommandScopeDefault(),
        )

    return on_startup()


async def on_shutdown() -> None:
    ...
    # await db.dispose()


async def start_bot(http_client: AsyncHTTPClientProtocol) -> None:
    dp.startup.register(await create_startup(http_client))
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)
