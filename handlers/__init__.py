from aiogram import Router

from . import lead, menu


def get_router() -> Router:
    router = Router()
    # lead идёт первым, чтобы /cancel и шаги заявки срабатывали раньше общих хендлеров
    router.include_routers(lead.router, menu.router)
    return router
