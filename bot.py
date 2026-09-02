import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, PreCheckoutQuery, LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# =====================================================================
# ⚙️ НАСТРОЙКИ БОТА (ЗАПОЛНИТЕ ИХ ПЕРЕД ЗАГРУЗКОЙ)
# =====================================================================
BOT_TOKEN = "8794720260:AAHW2mDu2ZNUuZJ5_ZO1Ie04H6HvBI22NrU"  # Токен от @BotFather
MY_MAIN_ID = 7280784652        # Ваш личный Telegram ID для уведомлений

# Список Telegram ID премиум-гостей через запятую (например:)
PREMIUM_GUESTS = [8689151856,7812909821,7280784652,7280784652,7280784652,8971823517,7280784652,7286650435] 
# =====================================================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    user_id = message.from_user.id
    is_premium = user_id in PREMIUM_GUESTS

    if is_premium:
        text = (
            "✨ **Добро пожаловать, Премиум-гость!** ✨\n"
            "Для вас действуют особые цены:\n\n"
            "🔹 Услуга 1 — личный поход по парковке со всеми тонкостями и скрытми местами✅  🎉 БЕСПЛАТНО\n"
            "🔹 Услуга 2 — Кастомные карты/путеводитель по парковке со всеми самыми безопасными маршрутами✅ 15 Stars (вместо 25)\n"
            "🔹 Услуга 3 —Частный канал с самой важной и секретной информацией✅ 🎉 БЕСПЛАТНО\n"
            "🔹 Услуга 4 — Проверить мой Премиум-статус\n\n"
            "Пожалуйста, выберите нужный вариант ниже 👇"
        )
        buttons = [
            [InlineKeyboardButton(text="🎁 Получить Услугу 1 (Бесплатно)", callback_data="buy_1")],
            [InlineKeyboardButton(text="🎁 Купить Услугу 2 (15 ⭐)", callback_data="buy_2")],
            [InlineKeyboardButton(text="🎁 Получить Услугу 3 (Бесплатно)", callback_data="buy_3")],
            [InlineKeyboardButton(text="🔍 Проверить статус (Вариант 4)", callback_data="check_premium")]
        ]
    else:
        text = (
            "👋 Привет! Вот наш актуальный прайс-лист:\n\n"
            "🔹 Услуга 1 — личный поход по парковке со всеми тонкостями и скрытми местами✅ (15 Stars)\n"
            "🔹 Услуга 2 — Кастомные карты/путеводитель по парковке со всеми самыми безопасными маршрутами✅ (25 Stars)\n"
            "🔹 Услуга 3 — Частный канал с самой важной и секретной информацией✅ (15 Stars)\n"
            "🔹 Услуга 4 — Проверить мой Премиум-статус\n\n"
            "Пожалуйста, выберите нужный вариант ниже 👇"
        )
        buttons = [
            [InlineKeyboardButton(text="🎁 Купить Услугу 1 (15 ⭐)", callback_data="buy_1")],
            [InlineKeyboardButton(text="🎁 Купить Услугу 2 (25 ⭐)", callback_data="buy_2")],
            [InlineKeyboardButton(text="🎁 Купить Услугу 3 (15 ⭐)", callback_data="buy_3")],
            [InlineKeyboardButton(text="🔍 Проверить статус (Вариант 4)", callback_data="check_premium")]
        ]
        
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

@dp.callback_query(F.data.startswith("buy_"))
async def process_buy(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = callback.from_user
    service_id = callback.data.split("_")[1]
    is_premium = user_id in PREMIUM_GUESTS

    if is_premium:
        if service_id in ["1", "3"]:
            await callback.message.answer(f"🎉 Вы активировали Услугу №{service_id} БЕСПЛАТНО по вашей Премиум-подписке!")
            notification_text = (
                "🎁 **БЕСПЛАТНАЯ АКТИВАЦИЯ (ПРЕМИУМ)!** 🎁\n\n"
                f"👤 **Пользователь:** {user.full_name} (@{user.username})\n"
                f"🆔 **ID:** `{user.id}`\n"
                f"📦 **Выбрано:** Услуга {service_id}\n"
                f"💰 **Стоимость:** 0 Stars"
            )
            await bot.send_message(chat_id=MY_MAIN_ID, text=notification_text, parse_mode="Markdown")
            await callback.answer()
            return
        elif service_id == "2":
            price = 15
    else:
        prices = {"1": 15, "2": 25, "3": 15}
        price = prices.get(service_id, 15)

    await callback.message.answer_invoice(
        title=f"Оплата Услуги №{service_id}",
        description=f"Оплата цифровой услуги через Telegram Stars",
        payload=f"service_{service_id}",
        provider_token="", 
        currency="XTR",    
        prices=[LabeledPrice(label="Цена", amount=price)]
    )
    await callback.answer()

@dp.callback_query(F.data == "check_premium")
async def process_check_premium(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id in PREMIUM_GUESTS:
        status_text = "✨ Вы успешно внесены в список премиум гостей!"
    else:
        status_text = "❌ Вас нет в списке премиум гостей."
    await callback.message.answer(status_text)
    await callback.answer()

@dp.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def success_payment_handler(message: Message):
    payment_info = message.successful_payment
    payload = payment_info.invoice_payload
    user = message.from_user

    await message.answer("🎉 Спасибо за оплату! Ваша услуга активирована.")
    is_premium = "Да ✅" if user.id in PREMIUM_GUESTS else "Нет ❌"

    notification_text = (
        "🚨 **НОВЫЙ ОПЛАЧЕННЫЙ ЗАКАЗ!** 🚨\n\n"
        f"👤 **Покупатель:** {user.full_name} (@{user.username})\n"
        f"🆔 **ID:** `{user.id}`\n"
        f"🌟 **Премиум гость:** {is_premium}\n"
        f"📦 **Товар:** {payload}\n"
        f"💰 **Сумма:** {payment_info.total_amount} Telegram Stars"
    )
    await bot.send_message(chat_id=MY_MAIN_ID, text=notification_text, parse_mode="Markdown")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
