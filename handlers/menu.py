import html
from contextlib import suppress

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import content
import keyboards as kb
from keyboards import FaqCb, MenuCb

router = Router()


def services_text() -> str:
    lines = [f"• {title} — <b>{price}</b>" for title, price in content.SERVICES]
    return "💰 <b>Услуги и цены</b>\n\n" + "\n".join(lines)


async def show(callback: CallbackQuery, text: str, markup) -> None:
    # Редактируем сообщение вместо отправки нового, чтобы чат не засорялся
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(text, reply_markup=markup)
    await callback.answer()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    name = html.escape(message.from_user.first_name or "друг")
    await message.answer(content.WELCOME.format(name=name), reply_markup=kb.main_menu())


@router.callback_query(MenuCb.filter(F.section == "main"))
async def open_main(callback: CallbackQuery) -> None:
    name = html.escape(callback.from_user.first_name or "друг")
    await show(callback, content.WELCOME.format(name=name), kb.main_menu())


@router.callback_query(MenuCb.filter(F.section == "about"))
async def open_about(callback: CallbackQuery) -> None:
    await show(callback, content.ABOUT, kb.back_button())


@router.callback_query(MenuCb.filter(F.section == "services"))
async def open_services(callback: CallbackQuery) -> None:
    await show(callback, services_text(), kb.back_button())


@router.callback_query(MenuCb.filter(F.section == "portfolio"))
async def open_portfolio(callback: CallbackQuery) -> None:
    await show(callback, content.PORTFOLIO, kb.portfolio_menu())


@router.callback_query(MenuCb.filter(F.section == "contacts"))
async def open_contacts(callback: CallbackQuery) -> None:
    await show(callback, content.CONTACTS, kb.back_button())


@router.callback_query(MenuCb.filter(F.section == "faq"))
async def open_faq(callback: CallbackQuery) -> None:
    await show(callback, "❓ <b>Частые вопросы</b>\n\nВыбери вопрос:", kb.faq_menu())


@router.callback_query(FaqCb.filter())
async def open_faq_answer(callback: CallbackQuery, callback_data: FaqCb) -> None:
    if not 0 <= callback_data.index < len(content.FAQ):
        await callback.answer()
        return
    question, answer = content.FAQ[callback_data.index]
    await show(callback, f"❓ <b>{question}</b>\n\n{answer}", kb.faq_answer_menu())


@router.callback_query()
async def stale_button(callback: CallbackQuery) -> None:
    # Кнопки из старых сообщений (например, после перезапуска бота) — иначе у пользователя крутятся часики
    await callback.answer("Эта кнопка устарела. Нажми /start", show_alert=True)
