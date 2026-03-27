import json
import logging
from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.types import Message
from database.db import get_user, get_product, create_order
from config import ADMIN_GROUP_ID

logger = logging.getLogger(__name__)
orders_router = Router()


@orders_router.message(F.web_app_data)
async def handle_web_app_data(message: Message, bot: Bot):
    """Handle data sent from the Mini App when user selects products."""
    try:
        data = json.loads(message.web_app_data.data)
        product_ids = data.get("selected_products", [])

        if not product_ids:
            await message.answer("⚠️ Вы не выбрали ни одного товара.")
            return

        user = await get_user(message.from_user.id)
        if not user:
            await message.answer("❌ Ошибка: пользователь не найден. Используйте /start для регистрации.")
            return

        # Fetch product details
        products = []
        for pid in product_ids:
            product = await get_product(int(pid))
            if product:
                products.append(product)

        if not products:
            await message.answer("⚠️ Выбранные товары не найдены.")
            return

        # Save order
        order_id = await create_order(user["id"], [p["id"] for p in products])

        # Confirmation to user
        products_text = "\n".join(
            [f"  • {p['name']}" + (f" — {p['price']} руб." if p['price'] else "") for p in products]
        )
        await message.answer(
            f"✅ Ваша заявка #{order_id} принята!\n\n"
            f"📦 Выбранные товары:\n{products_text}\n\n"
            f"Мы свяжемся с вами в ближайшее время."
        )

        # Notify admin group
        await notify_admins(bot, user, products, order_id)

    except json.JSONDecodeError:
        logger.error(f"Invalid JSON from web app: {message.web_app_data.data}")
        await message.answer("❌ Ошибка обработки данных. Попробуйте ещё раз.")
    except Exception as e:
        logger.exception(f"Error handling web app data: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")


async def notify_admins(bot: Bot, user, products: list, order_id: int):
    """Send order notification to admin group."""
    try:
        now = datetime.now().strftime("%d.%m.%Y %H:%M")
        products_text = "\n".join(
            [f"  • {p['name']}" + (f" ({p['article']})" if p['article'] else "") +
             (f" — {p['price']} руб." if p['price'] else "") for p in products]
        )

        text = (
            f"🛒 <b>Новая заявка #{order_id}</b>\n\n"
            f"👤 <b>Клиент:</b> {user['name']}\n"
            f"📱 <b>Телефон:</b> {user['phone']}\n"
            f"🆔 <b>Telegram ID:</b> {user['telegram_id']}\n\n"
            f"📦 <b>Товары:</b>\n{products_text}\n\n"
            f"🕐 <b>Дата/время:</b> {now}"
        )

        await bot.send_message(
            chat_id=ADMIN_GROUP_ID,
            text=text,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Failed to notify admins: {e}")
