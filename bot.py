"""Точка входа. Локально бот работает через polling, на Render — через вебхук."""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

import config
from handlers import get_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
# aiohttp пишет в лог полный URL запросов, а в URL Telegram API сидит токен — глушим его
logging.getLogger("aiohttp.access").setLevel(logging.WARNING)


def create_bot_and_dispatcher() -> tuple[Bot, Dispatcher]:
    bot = Bot(config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(get_router())
    return bot, dp


async def set_commands(bot: Bot) -> None:
    await bot.set_my_commands([
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="cancel", description="Отменить заявку"),
    ])


async def run_polling() -> None:
    bot, dp = create_bot_and_dispatcher()
    await set_commands(bot)
    # Если раньше стоял вебхук, polling не заработает, пока его не снять
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Бот запущен в режиме polling")
    await dp.start_polling(bot)


def run_webhook() -> None:
    bot, dp = create_bot_and_dispatcher()

    async def on_startup(bot: Bot) -> None:
        await set_commands(bot)
        await bot.set_webhook(
            config.WEBHOOK_BASE.rstrip("/") + config.WEBHOOK_PATH,
            secret_token=config.WEBHOOK_SECRET,
            drop_pending_updates=True,
        )
        logging.info("Вебхук установлен")

    dp.startup.register(on_startup)

    app = web.Application()
    # Главная страница нужна Render для проверки, что сервис живой
    app.router.add_get("/", lambda request: web.Response(text="Bot is running"))
    SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=config.WEBHOOK_SECRET).register(
        app, path=config.WEBHOOK_PATH
    )
    setup_application(app, dp, bot=bot)
    web.run_app(app, host="0.0.0.0", port=config.PORT)


if __name__ == "__main__":
    if config.WEBHOOK_BASE:
        run_webhook()
    else:
        asyncio.run(run_polling())
