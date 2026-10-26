from aiogram.filters.callback_data import CallbackData
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import content


class MenuCb(CallbackData, prefix="menu"):
    section: str


class FaqCb(CallbackData, prefix="faq"):
    index: int


class LeadCb(CallbackData, prefix="lead"):
    action: str  # send | restart


def main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="📸 О нас", callback_data=MenuCb(section="about"))
    kb.button(text="💰 Услуги и цены", callback_data=MenuCb(section="services"))
    kb.button(text="🖼 Наши работы", callback_data=MenuCb(section="portfolio"))
    kb.button(text="❓ Частые вопросы", callback_data=MenuCb(section="faq"))
    kb.button(text="📍 Контакты", callback_data=MenuCb(section="contacts"))
    kb.button(text="✍️ Записаться", callback_data=MenuCb(section="lead"))
    kb.adjust(2, 2, 1, 1)
    return kb.as_markup()


def back_button(kb: InlineKeyboardBuilder | None = None):
    kb = kb or InlineKeyboardBuilder()
    kb.button(text="✍️ Записаться", callback_data=MenuCb(section="lead"))
    kb.button(text="⬅️ В меню", callback_data=MenuCb(section="main"))
    kb.adjust(1)
    return kb.as_markup()


def portfolio_menu():
    kb = InlineKeyboardBuilder()
    for title, url in content.PORTFOLIO_LINKS:
        kb.button(text=title, url=url)
    return back_button(kb)


def faq_menu():
    kb = InlineKeyboardBuilder()
    for index, (question, _) in enumerate(content.FAQ):
        kb.button(text=question, callback_data=FaqCb(index=index))
    kb.button(text="⬅️ В меню", callback_data=MenuCb(section="main"))
    kb.adjust(1)
    return kb.as_markup()


def faq_answer_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ К вопросам", callback_data=MenuCb(section="faq"))
    kb.button(text="🏠 В меню", callback_data=MenuCb(section="main"))
    kb.adjust(2)
    return kb.as_markup()


def phone_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Отправить мой номер", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def lead_confirm():
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Отправить", callback_data=LeadCb(action="send"))
    kb.button(text="🔄 Заново", callback_data=LeadCb(action="restart"))
    kb.adjust(2)
    return kb.as_markup()
