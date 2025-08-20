from aiogram import Router


def setup_routers() -> Router:
    from . import start

    router = Router()

    router.include_routers(start.router)

    return router
