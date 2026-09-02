import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, PreCheckoutQuery, LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiohttp import web

# =====================================================================
# ⚙️ НАСТРОЙКИ БОТА (ПОЛНОСТЬЮ ЗАПОЛНЕНЫ)
# =====================================================================
BOT_TOKEN = "8794720260:AAHW2mDu2ZNUuZJ5_ZO1Ie04H6HvBI22NrU"  
MY_MAIN_ID = 7280784652        
PREMIUM_GUESTS = [8689151856, 7812909821, 7280784652, 8971823517, 7286650435,7676948389] 

# 🔗 ССЫЛКА ДЛЯ УСЛУГИ 3 (Ваш закрытый премиум-канал)
URL_FOR_SERVICE_3 = "https://t.me/+KZgRwt-38bljNDMy"
# =====================================================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- ЛОГИКА БОТА ---
@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    user_id = message.from_user.id
    is_premium = user_id in PREMIUM_GUESTS
    
    # 📋 ТЕКСТ ПРАЙС-ЛИСТА С ВАШИМИ ОПИСАНИЯМИ
    if is_premium:
        text = (
            "✨ **Добро пожаловать, Премиум-гость!** ✨\n"
            "Для вас действуют особые цены и условия:\n\n"
            "🔹 **Услуга 1** — Личный поход по парковке со всеми тонкостями и скрытыми местами ✅ | 🎉 **БЕСПЛАТНО**\n"
            "🔹 **Услуга 2** — Кастомные карты/путеводитель по парковке со всеми самыми безопасными маршрутами ✅ | 🔥 **15 Stars**\n"
            "🔹 **Услуга 3** — Частный канал с самой важной и секретной информацией ✅ | 🎉 **БЕСПЛАТНО**\n"
            "🔹 **Вариант 4** — Проверить ваш статус в системе\n\n"
            "Пожалуйста, выберите нужный вариант ниже 👇"
        )
        btn1_text = "🎁 Получить Услугу 1 (Бесплатно)"
        btn2_text = "🎁 Купить Услугу 2 (15 ⭐)"
        btn3_text = "🎁 Получить Услугу 3 (Бесплатно)"
    else:
        text = (
            "👋 **Привет! Вот наш актуальный прайс-лист:**\n\n"
            "🔹 **Услуга 1** — Личный поход по парковке со всеми тонкостями и скрытыми местами ✅ | 💰 **15 Stars**\n"
            "🔹 **Услуга 2** — Кастомные карты/путеводитель по парковке со всеми самыми безопасными маршрутами ✅ | 💰 **25 Stars**\n"
            "🔹 **Услуга 3** — Частный канал с самой важной и секретной информацией ✅ | 💰 **15 Stars**\n"
            "🔹 **Вариант 4** — Проверить свой Премиум-статус\n\n"
            "Пожалуйста, выберите нужную услугу ниже 👇"
        )
        btn1_text = "🎁 Купить Услугу 1 (15 ⭐)"
        btn2_text = "🎁 Купить Услугу 2 (25 ⭐)"
        btn3_text = "🎁 Купить Услугу 3 (15 ⭐)"
    
    buttons = [
        [InlineKeyboardButton(text=btn1_text, callback_data="buy_1")],
        [InlineKeyboardButton(text=btn2_text, callback_data="buy_2")],
        [InlineKeyboardButton(text=btn3_text, callback_data="buy_3")],
        [InlineKeyboardButton(text="🔍 Проверить статус (Вариант 4)", callback_data="check_premium")]
    ]
        
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

@dp.callback_query(F.data.startswith("buy_"))
async def process_buy(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = callback.from_user
    service_id = callback.data.split("_")[-1]
    is_premium = user_id in PREMIUM_GUESTS

    # Названия для инвойсов оплаты
    service_names = {
        "1": "Личный поход по парковке",
        "2": "Кастомные карты/путеводитель",
        "3": "Частный секретный канал"
    }
    current_service_name = service_names.get(service_id, f"Услуга №{service_id}")

    if is_premium:
        if service_id == "1":
            await callback.message.answer("🎉 Вы активировали услугу «Личный поход по парковке» БЕСПЛАТНО!")
            notification_text = f"🎁 **БЕСПЛАТНАЯ АКТИВАЦИЯ!**\n👤 {user.full_name} (@{user.username})\n📦 Услуга 1 (Поход по парковке)"
            await bot.send_message(chat_id=MY_MAIN_ID, text=notification_text, parse_mode="Markdown")
            await callback.answer()
            return
        elif service_id == "3":
            await callback.message.answer(
                f"🎉 По вашей Премиум-подписке доступ к частному каналу предоставлен БЕСПЛАТНО!\n\n"
                f"🔗 **Ссылка для входа:** {URL_FOR_SERVICE_3}",
                disable_web_page_preview=True
            )
            notification_text = f"🎁 **БЕСПЛАТНАЯ ССЫЛКА!**\n👤 {user.full_name} (@{user.username})\n📦 Получил ссылку на Частный канал"
            await bot.send_message(chat_id=MY_MAIN_ID, text=notification_text, parse_mode="Markdown")
            await callback.answer()
            return
        elif service_id == "2":
            price = 15
    else:
        prices = {"1": 15, "2": 25, "3": 15}
        price = prices.get(service_id, 15)

    await callback.message.answer_invoice(
        title=current_service_name,
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
    status_text = "✨ Вы успешно внесены в список премиум гостей!" if user_id in PREMIUM_GUESTS else "❌ Вас нет в списке премиум гостей."
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

    if payload == "service_3":
        await message.answer(
            f"🎉 Спасибо за оплату!\n\n"
            f"🔗 **Ваша ссылка на Частный канал (Услуга №3):** {URL_FOR_SERVICE_3}",
            disable_web_page_preview=True
        )
    else:
        await message.answer("🎉 Спасибо за оплату! Ваша услуга успешно активирована.")

    is_premium = "Да ✅" if user.id in PREMIUM_GUESTS else "Нет ❌"
    notification_text = f"🚨 **НОВЫЙ ОПЛАЧЕННЫЙ ЗАКАЗ!**\n👤 {user.full_name}\n📦 {payload}\n🌟 Премиум: {is_premium}\n💰 {payment_info.total_amount} Stars"
    await bot.send_message(chat_id=MY_MAIN_ID, text=notification_text, parse_mode="Markdown")

# --- КОД ДЛЯ РАБОТЫ НА RENDER ---
async def handle_root(request):
    return web.Response(text="Бот запущен и работает!")

async def start_bot():
    asyncio.create_task(dp.start_polling(bot))
    app = web.Application()
    app.router.add_get("/", handle_root)
    port = int(os.environ.get("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(start_bot())
