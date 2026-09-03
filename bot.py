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

# База премиум-гостей без дубликатов
PREMIUM_GUESTS = [8689151856, 7812909821, 7280784652, 8971823517, 7286650435]

# Ссылка для автовыдачи в Услуге 3
URL_FOR_SERVICE_3 = "https://t.me"
# =====================================================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

DB_USERS = "users.txt"
DB_USERNAMES = "usernames.txt"

def save_user(user_id, username):
    """Безопасное сохранение пользователя в текстовую базу данных"""
    for file in [DB_USERS, DB_USERNAMES]:
        if not os.path.exists(file):
            with open(file, "w") as f: pass

    with open(DB_USERS, "r") as f:
        ids = f.read().splitlines()
    if str(user_id) not in ids:
        with open(DB_USERS, "a") as f:
            f.write(f"{user_id}\n")
            
    if username:
        username = username.lower().replace("@", "").strip()
        with open(DB_USERNAMES, "r") as f:
            lines = f.read().splitlines()
        if not any(line.startswith(f"{username}:") for line in lines):
            with open(DB_USERNAMES, "a") as f:
                f.write(f"{username}:{user_id}\n")

def get_id_by_username(username):
    """Поиск ID пользователя по его юзернейму"""
    username = username.lower().replace("@", "").strip()
    if os.path.exists(DB_USERNAMES):
        with open(DB_USERNAMES, "r") as f:
            for line in f:
                if line.startswith(f"{username}:"):
                    return int(line.split(":")[1].strip())
    return None

# --- АДМИН-КОМАНДА: Рассылка всем (/all текст) ---
@dp.message(F.from_user.id == MY_MAIN_ID, F.text.startswith("/all"))
async def admin_broadcast(message: Message):
    text_to_send = message.text.replace("/all", "").strip()
    if not text_to_send:
        await message.answer("❌ Вы не ввели текст. Пример: `/all Всем привет!`")
        return
    if not os.path.exists(DB_USERS):
        await message.answer("❌ База пользователей пуста.")
        return
    with open(DB_USERS, "r") as f:
        user_ids = f.read().splitlines()
        
    success = 0
    for u_id in user_ids:
        try:
            await bot.send_message(chat_id=int(u_id), text=text_to_send)
            success += 1
            await asyncio.sleep(0.05)
        except: pass
    await message.answer(f"📢 Успешно отправлено: {success} из {len(user_ids)}")

# --- АДМИН-КОМАНДА: Ответ конкретному человеку (/юз @username текст) ---
@dp.message(F.from_user.id == MY_MAIN_ID, F.text.startswith("/юз"))
async def admin_reply_by_username(message: Message):
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("❌ Неверный формат. Пример: `/юз @username Текст`")
        return
    target_id = get_id_by_username(parts[1])
    if not target_id:
        await message.answer(f"❌ Пользователь {parts[1]} не найден в базе бота.")
        return
    try:
        await bot.send_message(chat_id=target_id, text=parts[2])
        await message.answer(f"✅ Отправлено для {parts[1]}!")
    except Exception as e:
        await message.answer(f"❌ Ошибка отправки: {e}")

# --- КЛИЕНТСКАЯ ЧАСТЬ: Меню и прайс ---
@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    user_id = message.from_user.id
    is_premium = user_id in PREMIUM_GUESTS
    save_user(user_id, message.from_user.username)
    
    if is_premium:
        text = (
            "✨ **Добро пожаловать, Премиум-гость!** ✨\n\n"
            "🔹 **Услуга 1** — Личный поход по парковке ✅ | 🎉 **БЕСПЛАТНО**\n"
            "🔹 **Услуга 2** — Кастомные карты/путеводитель ✅ | 🔥 **15 Stars**\n"
            "🔹 **Услуга 3** — Частный канал ✅ | 🎉 **БЕСПЛАТНО**\n"
            "🔹 **Вариант 4** — Проверить статус\n\n"
            "Выберите вариант 👇"
        )
        buttons = [
            [InlineKeyboardButton(text="🎁 Услуга 1 (Бесплатно)", callback_data="buy_1")],
            [InlineKeyboardButton(text="🎁 Купить Услугу 2 (15 ⭐)", callback_data="buy_2")],
            [InlineKeyboardButton(text="🎁 Услуга 3 (Бесплатно)", callback_data="buy_3")]
        ]
    else:
        text = (
            "👋 **Привет! Наш актуальный прайс-лист:**\n\n"
            "🔹 **Услуга 1** — Личный поход по парковке ✅ | 💰 **15 Stars**\n"
            "🔹 **Услуга 2** — Кастомные карты/путеводитель ✅ | 💰 **25 Stars**\n"
            "🔹 **Услуга 3** — Частный канал ✅ | 💰 **15 Stars**\n"
            "🔹 **Вариант 4** — Проверить статус\n\n"
            "Выберите вариант 👇"
        )
        buttons = [
            [InlineKeyboardButton(text="🎁 Купить Услугу 1 (15 ⭐)", callback_data="buy_1")],
            [InlineKeyboardButton(text="🎁 Купить Услугу 2 (25 ⭐)", callback_data="buy_2")],
            [InlineKeyboardButton(text="🎁 Купить Услугу 3 (15 ⭐)", callback_data="buy_3")]
        ]
        
    buttons.append([InlineKeyboardButton(text="🔍 Проверить статус (Вариант 4)", callback_data="check_premium")])
    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("buy_"))
async def process_buy(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = callback.from_user
    service_id = callback.data.split("_")[-1]
    is_premium = user_id in PREMIUM_GUESTS

    names = {"1": "Личный поход по парковке", "2": "Кастомные карты/путеводитель", "3": "Частный секретный канал"}
    current_name = names.get(service_id, "Услуга")

    if is_premium and service_id == "1":
        await callback.message.answer("🎉 Вы активировали Услугу №1 БЕСПЛАТНО!")
        await bot.send_message(MY_MAIN_ID, f"🎁 **БЕСПЛАТНАЯ АКТИВАЦИЯ!**\n👤 {user.full_name} (@{user.username})\n📦 Услуга 1")
        await callback.answer()
        return
    elif is_premium and service_id == "3":
        await callback.message.answer(f"🎉 Доступ к каналу предоставлен бесплатно!\n🔗 **Ссылка:** {URL_FOR_SERVICE_3}", disable_web_page_preview=True)
        await bot.send_message(MY_MAIN_ID, f"🎁 **БЕСПЛАТНАЯ ССЫЛКА!**\n👤 {user.full_name} (@{user.username})\n📦 Получил доступ к каналу")
        await callback.answer()
        return

    price = 15 if is_premium else (25 if service_id == "2" else 15)
    await callback.message.answer_invoice(
        title=current_name, description="Оплата через Telegram Stars", payload=f"service_{service_id}",
        provider_token="", currency="XTR", prices=[LabeledPrice(label="Цена", amount=price)]
    )
    await callback.answer()

@dp.callback_query(F.data == "check_premium")
async def process_check_premium(callback: CallbackQuery):
    status = "✨ Вы в списке премиум гостей!" if callback.from_user.id in PREMIUM_GUESTS else "❌ Вас нет в списке премиум гостей."
    await callback.message.answer(status)
    await callback.answer()

@dp.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def success_payment_handler(message: Message):
    payload = message.successful_payment.invoice_payload
    user = message.from_user

    if payload == "service_3":
        await message.answer(f"🎉 Спасибо за оплату!\n🔗 **Ваша ссылка на канал:** {URL_FOR_SERVICE_3}", disable_web_page_preview=True)
    else:
        await message.answer("🎉 Спасибо за оплату! Ваша услуга успешно активирована.")

    prem_label = "Да ✅" if user.id in PREMIUM_GUESTS else "Нет ❌"
    await bot.send_message(MY_MAIN_ID, f"🚨 **НОВЫЙ ЗАКАЗ!**\n👤 {user.full_name} (@{user.username})\n📦 {payload}\n🌟 Премиум: {prem_label}\n💰 {message.successful_payment.total_amount} Stars")

# --- ПЕРЕСЫЛКА СООБЩЕНИЙ КЛИЕНТОВ ВАМ ---
@dp.message(F.from_user.id != MY_MAIN_ID, F.text, ~F.text.startswith("/"))
async def forward_to_admin(message: Message):
    user = message.from_user
    save_user(user.id, user.username)
    await bot.send_message(MY_MAIN_ID, f"📩 **Новое сообщение от клиента!**\n👤 {user.full_name} (@{user.username})\n🆔 `{user.id}`\n\n💬 {message.text}")

# --- КОД ДЛЯ ВЕБ-СЕРВЕРА RENDER ---
async def handle_root(request):
    return web.Response(text="Бот запущен и работает!")

async def start_bot():
    asyncio.create_task(dp.start_polling(bot))
    app = web.Application()
    app.router.add_get("/", handle_root)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 8080))).start()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(start_bot())
