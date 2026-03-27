from aiogram import Dispatcher, Router, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, WebAppInfo
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import get_user, create_user
from config import MINI_APP_URL

router = Router()


class Registration(StatesGroup):
    waiting_name = State()
    waiting_phone = State()


def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(
                text="🛍 Открыть каталог",
                web_app=WebAppInfo(url=MINI_APP_URL)
            )]
        ],
        resize_keyboard=True
    )


def phone_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if user:
        await message.answer(
            f"👋 С возвращением, {user['name']}!\n\nНажмите кнопку ниже, чтобы открыть каталог.",
            reply_markup=main_menu_keyboard()
        )
    else:
        await message.answer(
            "👋 Добро пожаловать!\n\nДля начала давайте познакомимся. Как вас зовут?",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(Registration.waiting_name)


@router.message(Registration.waiting_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("Пожалуйста, введите корректное имя (минимум 2 символа).")
        return

    await state.update_data(name=name)
    await message.answer(
        f"Приятно познакомиться, {name}! 📱\n\nТеперь поделитесь своим номером телефона:",
        reply_markup=phone_keyboard()
    )
    await state.set_state(Registration.waiting_phone)


@router.message(Registration.waiting_phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    await finish_registration(message, state, phone)


@router.message(Registration.waiting_phone, F.text)
async def process_phone_text(message: Message, state: FSMContext):
    phone = message.text.strip()
    # Basic phone validation
    cleaned = phone.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
    if not cleaned.isdigit() or len(cleaned) < 7:
        await message.answer("Пожалуйста, введите корректный номер телефона.")
        return
    await finish_registration(message, state, phone)


async def finish_registration(message: Message, state: FSMContext, phone: str):
    data = await state.get_data()
    name = data["name"]

    await create_user(
        telegram_id=message.from_user.id,
        name=name,
        phone=phone
    )
    await state.clear()

    await message.answer(
        f"✅ Вы успешно зарегистрированы!\n\n"
        f"👤 Имя: {name}\n"
        f"📱 Телефон: {phone}\n\n"
        f"Теперь вы можете просматривать наш каталог товаров.",
        reply_markup=main_menu_keyboard()
    )


def register_handlers(dp: Dispatcher):
    dp.include_router(router)
    from handlers_orders import orders_router
    dp.include_router(orders_router)
