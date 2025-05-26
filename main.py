import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
)
import random
from datetime import datetime
import csv
import io

# Настройка логгирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Константы для состояний
CHOOSING, TYPING_WISH, HOLIDAY_NAME, HOLIDAY_STYLE = range(4)

# Данные для ответов
RESPONSES = {
    'adventure': {
        'text': "Приготовься к приключениям в ближайшие выходные!",
        'image': 'https://example.com/adventure_time.jpg'  # Заменить реальной ссылкой
    },
    'something_new': "Будь готова испытать что-то новое!",
    'breakfast': "Ожидай сюрприз-завтрак совсем скоро!",
    'handmade': "Сделаем что-то своими руками — готовься к творчеству!",
    'snacks': {
        'drink': "Жди, я уже в пути с напитком!",
        'food': "Вкусняшки уже в пути!",
        'order': "Напиши, что бы ты хотела — будет исполнено!"
    },
    'surprise': "Запрос принят. Ожидай что-нибудь — от бусинки до чего-то большего, чем ты можешь представить",
    'hugs': "Порция обнимашек уже в пути 💞",
    'care': "В течение 24 часов ты почувствуешь мою заботу",
    'shock': lambda: f"Шок-контент: {random.randint(1, 100)}",
    'flirt': "Готовься к весёлым и романтическим заданиям. Легкий флирт включён!",
    'soul': "Сегодня вечером поговорим по душам. Напиши тему, которая тебя волнует"
}

# Главное меню
MAIN_KEYBOARD = [
    ["💖 Удиви меня", "🍳 Хочу завтрак в постель"],
    ["🧰 Очумелые ручки", "➕ Вкусняшки"],
    ["📦 Хочу сюрприз", "🧸 Хочу обнимашек"],
    ["🧴 Забота", "🎲 Шок-контент"],
    ["💃 Флирт-режим", "🧠 По душам"],
    ["🎉 Праздник", "⚙️ Админ"]
]

ADMIN_KEYBOARD = [
    ["👁️ Логи", "📬 Уведомления"],
    ["🛎️ Напоминания", "📥 Экспорт"],
    ["🔙 Назад"]
]

# База данных (временная)
users_wishes = {}
activity_log = []


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    activity_log.append(f"{datetime.now()} - {user.id} запустил бота")
    await show_main_menu(update, "Привет, солнышко! 🌟\nВыбирай, чего тебе хочется:")


async def show_main_menu(update: Update, text: str):
    await update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardMarkup(
            MAIN_KEYBOARD,
            resize_keyboard=True,
            one_time_keyboard=False
        )
    )


# Обработчики для основных команд
async def surprise_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=RESPONSES['adventure']['image'],
        caption=RESPONSES['adventure']['text']
    )


async def breakfast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(RESPONSES['breakfast'])


async def handmade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(RESPONSES['handmade'])


# Обработчик вкусняшек
async def snacks_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🍹 Попить", "🍔 Покушать"], ["📝 Заказать"], ["🔙 Назад"]]
    await update.message.reply_text(
        "Выбирай:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


# Диалог для пользовательских пожеланий
async def custom_wish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Напиши свое пожелание:")
    return TYPING_WISH


async def save_wish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    users_wishes[user_id] = update.message.text
    await update.message.reply_text("Записала! Скоро это появится в твоей жизни ✨")
    return await show_main_menu(update, "Что-нибудь еще?")


# Шок-контент
async def shock_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(RESPONSES['shock']())


# Админские функции
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id == ADMIN_ID:  # Заменить на реальный ID
        await update.message.reply_text(
            "Админ-панель:",
            reply_markup=ReplyKeyboardMarkup(ADMIN_KEYBOARD, resize_keyboard=True)
        )
        return CHOOSING
    return ConversationHandler.END


async def export_wishes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    csv_data = io.StringIO()
    writer = csv.writer(csv_data)
    writer.writerow(["User ID", "Wish"])
    for user_id, wish in users_wishes.items():
        writer.writerow([user_id, wish])

    csv_data.seek(0)
    await update.message.reply_document(
        document=io.BytesIO(csv_data.getvalue().encode()),
        filename="wishes.csv"
    )


# Настройка обработчиков
def setup_handlers(application):
    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex(r"^⚙️ Админ$"), admin_panel),
            MessageHandler(filters.Regex(r"^📝 Заказать$"), custom_wish)
        ],
        states={
            TYPING_WISH: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_wish)],
            CHOOSING: [
                MessageHandler(filters.Regex(r"^📥 Экспорт$"), export_wishes),
                MessageHandler(filters.Regex(r"^🔙 Назад$"), show_main_menu)
            ]
        },
        fallbacks=[CommandHandler('start', start)]
    )

    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.Regex(r"^➕ Вкусняшки$"), snacks_menu))
    application.add_handler(MessageHandler(filters.Regex(r"^🎲 Шок-контент$"), shock_content))
    # Добавить остальные обработчики


def main():
    application = ApplicationBuilder().token("YOUR_TOKEN").build()
    setup_handlers(application)
    application.run_polling()


if __name__ == "__main__":
    main()