import asyncio
import os
import aiosqlite
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
)

# ----------------- CONFIGURATION -----------------
BOT_TOKEN = "8910817023:AAHVrNz-QQVibCBpe_1Qeb2mn_9qqR2H6w0"
ADMIN_IDS = [8886164132]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
DB_FILE = "bot_database.db"

# ----------------- DATABASE SETUP -----------------
async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                name TEXT,
                username TEXT,
                phone TEXT,
                lang TEXT DEFAULT 'en'
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                title TEXT,
                file_id TEXT,
                file_type TEXT,
                caption TEXT,
                price TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        await db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('owner', '@lv_oxyg3n')")
        await db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('admin', '@Ts_hunter')")
        await db.commit()

async def get_setting(key: str, default="@lv_oxyg3n"):
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT value FROM settings WHERE key = ?", (key,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else default

async def set_setting(key: str, value: str):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        await db.commit()

# ----------------- MULTI-LANGUAGE TEXTS -----------------
TEXTS = {
    "en": {
        "choose_lang": "👋 Welcome! Please select your preferred language:",
        "contact_req": "🔐 **Security Verification**\n\nSharing your contact is **100% safe & required** for account protection and instant key generation.\n\nPlease tap the button below to share:",
        "btn_share_contact": "📱 Share Phone Number",
        "verified": "✅ Verification Successful! Welcome to the VIP Portal.",
        "menu_title": "👑 **PREMIUM PANEL DASHBOARD** 👑\nSelect an option below to proceed:",
        "cat_main": "🛡️ Main ID Safe",
        "cat_second": "⚡ Second ID Safe",
        "cat_free": "🎁 Free Panel",
        "cat_support": "💬 Support",
        "empty": "⚠️ **Currently Unavailable**\nNo active panels in this section right now.\nPlease contact owner {owner} for urgent access.",
        "support_title": "🎧 **CUSTOMER SUPPORT CENTER**\nNeed assistance or instant key activation? Reach out:",
        "btn_admin": "👨‍💻 Contact Admin",
        "btn_owner": "👑 Contact Owner",
        "btn_buy": "🛒 Buy / Get Key",
        "btn_back": "⬅️ Back",
        "anim_loading": "⚡ [■□□□□] Accessing Cloud Server...",
        "anim_loading2": "⚡ [■■■□□] Authenticating Session...",
        "anim_loading3": "⚡ [■■■■■] Decrypting Asset...",
        "anim_vap": "✨ Vaporizing previous state...",
    },
    "hi": {
        "choose_lang": "👋 Namaste! Kripya apni bhasha chunein:",
        "contact_req": "🔐 **Suraksha Satyaapan**\n\nApna contact share karna **100% safe aur zaroori hai** security aur instant setup ke liye.\n\nNeeche diye button par click karke verify karein:",
        "btn_share_contact": "📱 Phone Number Share Karein",
        "verified": "✅ Satyaapan Safal! VIP Portal me aapka swagat hai.",
        "menu_title": "👑 **PREMIUM PANEL DASHBOARD** 👑\nKripya ek option chunein:",
        "cat_main": "🛡️ Main ID Safe",
        "cat_second": "⚡ Second ID Safe",
        "cat_free": "🎁 Free Panel",
        "cat_support": "💬 Support",
        "empty": "⚠️ **Abhi Uplabdh Nahi Hai**\nIs section me koi active panel nahi hai.\nTurant help ke liye Owner {owner} se contact karein.",
        "support_title": "🎧 **CUSTOMER SUPPORT CENTER**\nKoi sawal ya purchase ke liye sampark karein:",
        "btn_admin": "👨‍💻 Contact Admin",
        "btn_owner": "👑 Contact Owner",
        "btn_buy": "🛒 Buy Karein",
        "btn_back": "⬅️ Wapas Jayein",
        "anim_loading": "⚡ [■□□□□] Cloud Server Se Connect Ho Raha Hai...",
        "anim_loading2": "⚡ [■■■□□] Session Verify Ho Raha Hai...",
        "anim_loading3": "⚡ [■■■■■] File Prepare Ho Rahi Hai...",
        "anim_vap": "✨ Interface Refresh Ho Raha Hai...",
    },
    "ru": {
        "choose_lang": "👋 Добро пожаловать! Пожалуйста, выберите язык:",
        "contact_req": "🔐 **Проверка безопасности**\n\nПредоставление контакта **на 100% безопасно и необходимо** для защиты аккаунта.\n\nНажмите кнопку ниже для подтверждения:",
        "btn_share_contact": "📱 Поделиться контактом",
        "verified": "✅ Проверка прошла успешно! Добро пожаловать в VIP-портал.",
        "menu_title": "👑 **ГЛАВНАЯ ПАНЕЛЬ VIP** 👑\nВыберите нужный раздел:",
        "cat_main": "🛡️ Для Основного ID",
        "cat_second": "⚡ Для Второго ID",
        "cat_free": "🎁 Бесплатная Панель",
        "cat_support": "💬 Поддержка",
        "empty": "⚠️ **Временно недоступно**\nВ этом разделе пока нет активных товаров.\nСвяжитесь с владельцем {owner}.",
        "support_title": "🎧 **ЦЕНТР ПОДДЕРЖКИ**\nНужна помощь или покупка ключа? Свяжитесь с нами:",
        "btn_admin": "👨‍💻 Администратор",
        "btn_owner": "👑 Владелец",
        "btn_buy": "🛒 Купить / Ключ",
        "btn_back": "⬅️ Назад",
        "anim_loading": "⚡ [■□□□□] Подключение к серверу...",
        "anim_loading2": "⚡ [■■■□□] Авторизация сессии...",
        "anim_loading3": "⚡ [■■■■■] Расшифровка файла...",
        "anim_vap": "✨ Очистка интерфейса...",
    }
}

async def get_user_lang(user_id: int):
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT lang FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row and row[0] in TEXTS else "en"

async def run_vaporize_animation(message: types.Message, lang: str):
    t = TEXTS[lang]
    try:
        await message.edit_text(t["anim_loading"])
        await asyncio.sleep(0.3)
        await message.edit_text(t["anim_loading3"])
        await asyncio.sleep(0.3)
    except Exception:
        pass

# ----------------- KEYBOARD BUILDERS -----------------
def lang_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton(text="🇮🇳 Hinglish", callback_data="lang_hi")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")]
    ])

def contact_keyboard(lang: str):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=TEXTS[lang]["btn_share_contact"], request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def main_dashboard_keyboard(lang: str):
    t = TEXTS[lang]
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t["cat_main"], callback_data="cat_main_id")],
        [InlineKeyboardButton(text=t["cat_second"], callback_data="cat_second_id")],
        [InlineKeyboardButton(text=t["cat_free"], callback_data="cat_free_panel")],
        [InlineKeyboardButton(text=t["cat_support"], callback_data="cat_support")]
    ])

# ----------------- USER FLOW -----------------
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "✨ Welcome / Swagat / Добро пожаловать!\n\nChoose language / Bhasha chunein / Выберите язык:",
        reply_markup=lang_keyboard()
    )

@dp.callback_query(F.data.startswith("lang_"))
async def set_user_language(callback: types.CallbackQuery):
    lang_code = callback.data.split("_")[1]
    user_id = callback.from_user.id
    name = callback.from_user.full_name
    username = callback.from_user.username or "None"

    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
            INSERT INTO users (user_id, name, username, lang)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET lang = ?
        """, (user_id, name, username, lang_code, lang_code))
        await db.commit()

    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT phone FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            has_phone = row and row[0]

    try:
        await callback.message.delete()
    except Exception:
        pass

    if not has_phone:
        await callback.message.answer(
            TEXTS[lang_code]["contact_req"],
            reply_markup=contact_keyboard(lang_code)
        )
    else:
        await callback.message.answer(
            TEXTS[lang_code]["menu_title"],
            reply_markup=main_dashboard_keyboard(lang_code)
        )

@dp.message(F.contact)
async def handle_contact(message: types.Message):
    user_id = message.from_user.id
    phone = message.contact.phone_number
    lang = await get_user_lang(user_id)

    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("UPDATE users SET phone = ? WHERE user_id = ?", (phone, user_id))
        await db.commit()

    await message.answer(TEXTS[lang]["verified"], reply_markup=ReplyKeyboardRemove())
    await message.answer(TEXTS[lang]["menu_title"], reply_markup=main_dashboard_keyboard(lang))

@dp.callback_query(F.data.in_(["cat_main_id", "cat_second_id", "cat_free_panel"]))
async def show_category_products(callback: types.CallbackQuery):
    lang = await get_user_lang(callback.from_user.id)
    cat_name = callback.data.replace("cat_", "")
    
    await run_vaporize_animation(callback.message, lang)

    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT id, title FROM products WHERE category = ?", (cat_name,)) as cursor:
            items = await cursor.fetchall()

    if not items:
        owner = await get_setting("owner")
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=TEXTS[lang]["btn_back"], callback_data="back_to_menu")]
        ])
        await callback.message.edit_text(
            TEXTS[lang]["empty"].format(owner=owner),
            reply_markup=kb
        )
        return

    buttons = [[InlineKeyboardButton(text=f"📦 {item[1]}", callback_data=f"item_{item[0]}")] for item in items]
    buttons.append([InlineKeyboardButton(text=TEXTS[lang]["btn_back"], callback_data="back_to_menu")])
    
    await callback.message.edit_text(
        "💎 Available Options\nSelect an option to view details:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

@dp.callback_query(F.data.startswith("item_"))
async def display_item(callback: types.CallbackQuery):
    item_id = int(callback.data.split("_")[1])
    lang = await get_user_lang(callback.from_user.id)

    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT category, title, file_id, file_type, caption, price FROM products WHERE id = ?", (item_id,)) as cursor:
            product = await cursor.fetchone()

    if not product:
        await callback.answer("Item not found!", show_alert=True)
        return

    cat, title, file_id, file_type, caption, price = product
    owner = await get_setting("owner")
    clean_owner = owner.replace("@", "")

    try:
        await callback.message.delete()
    except Exception:
        pass

    action_buttons = []
    if cat != "free_panel":
        action_buttons.append([InlineKeyboardButton(text=TEXTS[lang]["btn_buy"], url=f"https://t.me/{clean_owner}")])
    action_buttons.append([InlineKeyboardButton(text=TEXTS[lang]["btn_back"], callback_data=f"cat_{cat}")])
    kb = InlineKeyboardMarkup(inline_keyboard=action_buttons)

    full_caption = f"🔥 {title}\n\n{caption}\n\n"
    if price and price != "None" and cat != "free_panel":
        full_caption += f"💰 Price: {price}\n"

    sent = False
    if file_id and file_id != "None":
        try:
            if file_type == "video":
                await bot.send_video(callback.from_user.id, video=file_id, caption=full_caption, reply_markup=kb)
                sent = True
            elif file_type == "animation":
                await bot.send_animation(callback.from_user.id, animation=file_id, caption=full_caption, reply_markup=kb)
                sent = True
            elif file_type == "document":
                await bot.send_document(callback.from_user.id, document=file_id, caption=full_caption, reply_markup=kb)
                sent = True
        except Exception:
            sent = False

    if not sent:
        await bot.send_message(callback.from_user.id, text=full_caption, reply_markup=kb)

@dp.callback_query(F.data == "cat_support")
async def show_support(callback: types.CallbackQuery):
    lang = await get_user_lang(callback.from_user.id)
    admin = (await get_setting("admin")).replace("@", "")
    owner = (await get_setting("owner")).replace("@", "")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=TEXTS[lang]["btn_admin"], url=f"https://t.me/{admin}")],
        [InlineKeyboardButton(text=TEXTS[lang]["btn_owner"], url=f"https://t.me/{owner}")],
        [InlineKeyboardButton(text=TEXTS[lang]["btn_back"], callback_data="back_to_menu")]
    ])
    await callback.message.edit_text(TEXTS[lang]["support_title"], reply_markup=kb)

@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    lang = await get_user_lang(callback.from_user.id)
    await callback.message.edit_text(TEXTS[lang]["menu_title"], reply_markup=main_dashboard_keyboard(lang))

# ----------------- ADMIN PANEL -----------------
class AdminAddProduct(StatesGroup):
    category = State()
    title = State()
    file = State()
    caption = State()
    price = State()

class AdminSetHandle(StatesGroup):
    role = State()
    handle = State()

class AdminBroadcast(StatesGroup):
    text = State()

def admin_dashboard_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Add Product/Panel", callback_data="admin_add_prod")],
        [InlineKeyboardButton(text="🗑️ Delete Product", callback_data="admin_del_prod")],
        [InlineKeyboardButton(text="👥 View User Logs", callback_data="admin_users")],
        [InlineKeyboardButton(text="⚙️ Edit Owner/Admin Handles", callback_data="admin_handles")],
        [InlineKeyboardButton(text="📢 Broadcast Message", callback_data="admin_broadcast")]
    ])

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    user_id = message.from_user.id
    if user_id in ADMIN_IDS or str(user_id) == "8886164132":
        await message.answer(
            f"🛠️ **SUPER ADMIN CONTROL PANEL**\nWelcome Boss! (ID: `{user_id}`)\nManage entire bot operations:",
            reply_markup=admin_dashboard_kb(),
            parse_mode="Markdown"
        )
    else:
        await message.answer(f"⛔ Access Denied! Your ID: `{user_id}`")

@dp.callback_query(F.data == "admin_handles")
async def admin_set_handles_prompt(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS and str(callback.from_user.id) != "8886164132":
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👑 Set Owner Handle", callback_data="set_handle_owner")],
        [InlineKeyboardButton(text="👨‍💻 Set Admin Handle", callback_data="set_handle_admin")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="admin_home")]
    ])
    await callback.message.edit_text("Select handle to update:", reply_markup=kb)

@dp.callback_query(F.data.startswith("set_handle_"))
async def set_handle_step(callback: types.CallbackQuery, state: FSMContext):
    role = callback.data.replace("set_handle_", "")
    await state.update_data(role=role)
    await state.set_state(AdminSetHandle.handle)
    await callback.message.answer(f"Enter new Telegram username for `{role}` (e.g. `@lv_oxyg3n`):")

@dp.message(AdminSetHandle.handle)
async def save_handle(message: types.Message, state: FSMContext):
    data = await state.get_data()
    role = data["role"]
    handle = message.text.strip()
    if not handle.startswith("@"):
        handle = "@" + handle
    await set_setting(role, handle)
    await state.clear()
    await message.answer(f"✅ Success! `{role}` updated to {handle}")

@dp.callback_query(F.data == "admin_users")
async def show_user_logs(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS and str(callback.from_user.id) != "8886164132":
        return
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT user_id, name, username, phone, lang FROM users") as cursor:
            users = await cursor.fetchall()

    if not users:
        await callback.answer("No users logged yet.", show_alert=True)
        return

    text = f"👥 **TOTAL REGISTERED USERS:** {len(users)}\n\n"
    for u in users[-15:]:
        text += f"👤 {u[1]} (@{u[2]})\n🆔 `{u[0]}` | 📞 `{u[3] or 'Not Shared'}` | 🌐 `{u[4]}`\n" + "—"*20 + "\n"

    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Back", callback_data="admin_home")]])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "admin_add_prod")
async def add_prod_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS and str(callback.from_user.id) != "8886164132":
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Main ID", callback_data="addcat_main_id")],
        [InlineKeyboardButton(text="Second ID", callback_data="addcat_second_id")],
        [InlineKeyboardButton(text="Free Panel", callback_data="addcat_free_panel")]
    ])
    await callback.message.edit_text("Select category to add item:", reply_markup=kb)

@dp.callback_query(F.data.startswith("addcat_"))
async def add_prod_cat(callback: types.CallbackQuery, state: FSMContext):
    cat = callback.data.replace("addcat_", "")
    await state.update_data(category=cat)
    await state.set_state(AdminAddProduct.title)
    await callback.message.answer("Enter Product / Panel Title:")

@dp.message(AdminAddProduct.title)
async def add_prod_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(AdminAddProduct.file)
    await message.answer("Send the Video or Document/APK file for this product (or send /skip if text only):")

@dp.message(AdminAddProduct.file)
async def add_prod_file(message: types.Message, state: FSMContext):
    if message.video:
        await state.update_data(file_id=message.video.file_id, file_type="video")
    elif message.animation:
        await state.update_data(file_id=message.animation.file_id, file_type="animation")
    elif message.document:
        await state.update_data(file_id=message.document.file_id, file_type="document")
    else:
        await state.update_data(file_id=None, file_type="none")
    
    await state.set_state(AdminAddProduct.caption)
    await message.answer("Enter Panel Description / Caption:")

@dp.message(AdminAddProduct.caption)
async def add_prod_caption(message: types.Message, state: FSMContext):
    await state.update_data(caption=message.text)
    data = await state.get_data()
    if data["category"] == "free_panel":
        async with aiosqlite.connect(DB_FILE) as db:
            await db.execute(
                "INSERT INTO products (category, title, file_id, file_type, caption, price) VALUES (?, ?, ?, ?, ?, ?)",
                (data["category"], data["title"], data.get("file_id"), data.get("file_type"), data["caption"], "FREE")
            )
            await db.commit()
        await state.clear()
        await message.answer("✅ Free Panel uploaded successfully!")
    else:
        await state.set_state(AdminAddProduct.price)
        await message.answer("Enter Pricing details (e.g. `7 Days: ₹200 | 30 Days: ₹500`):")

@dp.message(AdminAddProduct.price)
async def add_prod_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "INSERT INTO products (category, title, file_id, file_type, caption, price) VALUES (?, ?, ?, ?, ?, ?)",
            (data["category"], data["title"], data.get("file_id"), data.get("file_type"), data["caption"], message.text)
        )
        await db.commit()
    await state.clear()
    await message.answer("✅ Product uploaded successfully with media and pricing!")

@dp.callback_query(F.data == "admin_del_prod")
async def del_prod_list(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS and str(callback.from_user.id) != "8886164132":
        return
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT id, title, category FROM products") as cursor:
            items = await cursor.fetchall()
    if not items:
        await callback.answer("No products found to delete!", show_alert=True)
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"❌ {i[1]} ({i[2]})", callback_data=f"del_{i[0]}")] for i in items
    ] + [[InlineKeyboardButton(text="⬅️ Back", callback_data="admin_home")]])
    await callback.message.edit_text("Tap any item to delete it permanently:", reply_markup=kb)

@dp.callback_query(F.data.startswith("del_"))
async def del_prod_confirm(callback: types.CallbackQuery):
    item_id = int(callback.data.split("_")[1])
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("DELETE FROM products WHERE id = ?", (item_id,))
        await db.commit()
    await callback.answer("Deleted successfully!", show_alert=True)
    await del_prod_list(callback)

@dp.callback_query(F.data == "admin_broadcast")
async def start_broadcast(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS and str(callback.from_user.id) != "8886164132":
        return
    await state.set_state(AdminBroadcast.text)
    await callback.message.answer("Enter broadcast message to send to ALL users:")

@dp.message(AdminBroadcast.text)
async def execute_broadcast(message: types.Message, state: FSMContext):
    text = message.text
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT user_id FROM users") as cursor:
            rows = await cursor.fetchall()
    count = 0
    for r in rows:
        try:
            await bot.send_message(r[0], f"📢 **ANNOUNCEMENT**\n\n{text}", parse_mode="Markdown")
            count += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass
    await state.clear()
    await message.answer(f"✅ Broadcast sent to {count} users!")

@dp.callback_query(F.data == "admin_home")
async def admin_home(callback: types.CallbackQuery):
    await callback.message.edit_text("🛠️ **SUPER ADMIN CONTROL PANEL**", reply_markup=admin_dashboard_kb(), parse_mode="Markdown")

# ----------------- WEB SERVER (RENDER KEEP-ALIVE) -----------------
async def handle_ping(request):
    return web.Response(text="Bot is running smoothly 24/7!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

# ----------------- MAIN RUNNER -----------------
async def main():
    await init_db()
    await start_web_server()
    print("Bot is started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
