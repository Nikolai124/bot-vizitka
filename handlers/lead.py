"""Заявка на запись: имя → телефон → описание задачи → подтверждение → сообщение админу."""

import html
import logging
import re

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

import content
import keyboards as kb
from config import ADMIN_ID
from keyboards import LeadCb, MenuCb

router = Router()
log = logging.getLogger(__name__)


class Lead(StatesGroup):
    name = State()
    phone = State()
    task = State()
    confirm = State()


def normalize_phone(raw: str) -> str | None:
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 11 and digits[0] in "78":
        digits = "7" + digits[1:]
    elif len(digits) == 10:
        digits = "7" + digits
    else:
        return None
    return f"+{digits}"


@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(content.LEAD_CANCELLED, reply_markup=ReplyKeyboardRemove())


@router.callback_query(MenuCb.filter(F.section == "lead"))
async def start_lead(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(Lead.name)
    await callback.message.answer(content.LEAD_ASK_NAME + "\n\n<i>Отменить: /cancel</i>")
    await callback.answer()


@router.message(Lead.name, F.text)
async def get_name(message: Message, state: FSMContext) -> None:
    name = message.text.strip()
    if not 2 <= len(name) <= 60:
        await message.answer("Имя должно быть от 2 до 60 символов. Попробуй ещё раз.")
        return
    await state.update_data(name=name)
    await state.set_state(Lead.phone)
    await message.answer(content.LEAD_ASK_PHONE, reply_markup=kb.phone_keyboard())


@router.message(Lead.phone, F.contact)
async def get_phone_contact(message: Message, state: FSMContext) -> None:
    # Принимаем только свой контакт, а не пересланный чужой
    if message.contact.user_id != message.from_user.id:
        await message.answer("Отправь, пожалуйста, свой номер кнопкой ниже.")
        return
    await save_phone(message, state, message.contact.phone_number)


@router.message(Lead.phone, F.text)
async def get_phone_text(message: Message, state: FSMContext) -> None:
    await save_phone(message, state, message.text)


async def save_phone(message: Message, state: FSMContext, raw: str) -> None:
    phone = normalize_phone(raw)
    if not phone:
        await message.answer("Не похоже на номер. Пример: +7 900 123-45-67")
        return
    await state.update_data(phone=phone)
    await state.set_state(Lead.task)
    await message.answer(content.LEAD_ASK_TASK, reply_markup=ReplyKeyboardRemove())


@router.message(Lead.task, F.text)
async def get_task(message: Message, state: FSMContext) -> None:
    task = message.text.strip()[:1000]
    await state.update_data(task=task)
    await state.set_state(Lead.confirm)
    data = await state.get_data()
    text = content.LEAD_CONFIRM.format(
        name=html.escape(data["name"]), phone=data["phone"], task=html.escape(task)
    )
    await message.answer(text, reply_markup=kb.lead_confirm())


@router.callback_query(Lead.confirm, LeadCb.filter(F.action == "restart"))
async def restart_lead(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(Lead.name)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(content.LEAD_ASK_NAME)
    await callback.answer()


@router.callback_query(Lead.confirm, LeadCb.filter(F.action == "send"))
async def send_lead(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)

    user = callback.from_user
    username = f"@{user.username}" if user.username else "нет"
    admin_text = (
        "🔔 <b>Новая заявка из бота</b>\n\n"
        f"<b>Имя:</b> {html.escape(data['name'])}\n"
        f"<b>Телефон:</b> {data['phone']}\n"
        f"<b>Задача:</b> {html.escape(data['task'])}\n\n"
        f"<b>Telegram:</b> {username} (<a href=\"tg://user?id={user.id}\">написать</a>)"
    )
    try:
        await bot.send_message(ADMIN_ID, admin_text)
    except Exception:
        log.exception("Не удалось отправить заявку админу")
        await callback.message.answer("Что-то пошло не так. Позвони нам: контакты в /start")
        await callback.answer()
        return

    await callback.message.answer(content.LEAD_DONE, reply_markup=kb.main_menu())
    await callback.answer()


@router.message(Lead.name)
@router.message(Lead.phone)
@router.message(Lead.task)
async def wrong_input(message: Message) -> None:
    await message.answer("Напиши ответ текстом, пожалуйста. Отменить заявку: /cancel")
