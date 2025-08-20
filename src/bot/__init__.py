from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.methods import DeleteWebhook
from aiogram_dialog import setup_dialogs

from src.config import settings

# from app.database import Database
from src.bot.handlers import setup_routers

# from src.bot.middlewares.database import DatabaseMiddleware
from src.bot.middlewares.throttling import ThrottlingMiddleware

bot = Bot(
    token=settings.bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
)

storage = MemoryStorage()
# db = Database()
dp = Dispatcher(storage=storage)


async def on_startup() -> None:
    await bot(DeleteWebhook(drop_pending_updates=True))

    await db.init_db()

    router = setup_routers()
    dp.include_routers(router)

    setup_dialogs(dp)

    dp.update.outer_middleware(DatabaseMiddleware(db))

    dp.message.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware())

    await bot.set_my_commands(
        [types.BotCommand(command="start", description="↪️ Restart the bot")],
        types.BotCommandScopeDefault(),
    )


async def on_shutdown() -> None:
    await db.dispose()


async def main() -> None:
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)
