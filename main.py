import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
import random

# Настройка логгирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Данные для ответов
ROMANTIC_PHRASES = [
    "Ты — самое красивое чудо в моей жизни 🌸",
    "Каждый твой взгляд делает мой день ярче ☀️",
    "Я бы преодолел любые расстояния, чтобы услышать твой смех 🚀",
]

SURPRISE_ACTIONS = [
    "Секретная доставка букета 🌹 с запиской: 'Просто потому, что ты существуешь'",
    "Романтический квест по квартире с подсказками-стихами 🧩",
    "Флешмоб из 100 бумажных сердец с причинами, почему я тебя люблю 💌",
]

BREAKFAST_OPTIONS = [
    "Омлет с трюфелем и свежевыжатый апельсиновый сок 🍳",
    "Блинчики с клубникой и взбитыми сливками 🥞",
    "Фруктовая тарелка с йогуртом и мёдом 🍓",
]

CARE_ACTIONS = [
    "Вечерняя ванна с лепестками роз и аромасвечами 🛁",
    "Массаж спины с тёплым маслом лаванды 💆♀️",
    "Медитация под звуки океана вместе 🧘♂️",
]

DATE_IDEAS = [
    "Пикник на крыше с видом на закат 🌇",
    "Тематический ужин в стиле «Парижских кафе» 🥐",
    "Киноночь под звездами в саду 🎬",
]

GIFT_IDEAS = [
    "Кольцо с твоим камнем рождения 💍",
    "Персональная книга комиксов о нашей любви 📖",
    "Подписка на мастер-класс по танго 💃",
]

PHOTO_IDEAS = [
    "Фотосессия в стиле «Винтаж» с полароидом 📸",
    "Селфи с табличкой «Я ♥ тебя» в неожиданном месте 🤳",
    "Фото-коллаж из 100 моментов за год 🖼️",
]

# Главное меню
MAIN_KEYBOARD = [
    ["💖 Удиви меня", "🍳 Хочу завтрак в постель"],
    ["📦 Хочу сюрприз", "🧴 Забота и внимание"],
    ["🧸 Хочу обнимашек", "📸 Хочу фото с тобой"],
    ["🎁 Мне нужен подарок", "📅 Хочу идеальное свидание"],
    ["😘 Скажи мне что-нибудь приятное", "😱 Шок-контент!"],
    ["⚙️ Поддержка 24/7", "✈️ Спонтанный отдых"],
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    await update.message.reply_text(
        f"Привет, {user.first_name}! 🌟\nЯ — твоя личная горячая линия счастья.",
        reply_markup=ReplyKeyboardMarkup(
            MAIN_KEYBOARD,
            resize_keyboard=True,
            one_time_keyboard=False
        )
    )


async def surprise_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = random.choice(SURPRISE_ACTIONS)
    await update.message.reply_text(f"✨ Твой сюрприз: {response}")


async def breakfast_in_bed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dish = random.choice(BREAKFAST_OPTIONS)
    await update.message.reply_text(f"🍴 Завтрак готовится! Меню: {dish}")


async def want_surprise(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎁 Сюрприз уже в пути! Ожидай доставку к 18:00 🚚")


async def care_and_attention(update: Update, context: ContextTypes.DEFAULT_TYPE):
    action = random.choice(CARE_ACTIONS)
    await update.message.reply_text(f"💆♀️ Программа заботы: {action}")


async def want_hugs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤗 Обнимашки запущены! Приготовься к 10-минутному сеансу!")


async def want_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    idea = random.choice(PHOTO_IDEAS)
    await update.message.reply_text(f"📸 Идея для фото: {idea}")


async def want_gift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gift = random.choice(GIFT_IDEAS)
    await update.message.reply_text(f"🎁 Твой подарок: {gift} (доставка: 1-3 дня)")


async def perfect_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date = random.choice(DATE_IDEAS)
    await update.message.reply_text(f"🌹 Идея свидания: {date}")


async def romantic_phrase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phrase = random.choice(ROMANTIC_PHRASES)
    await update.message.reply_text(f"{phrase} 💞")


async def shock_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💣 Шок-контент активирован! Ожидай неожиданное в течение часа! ⏳")


async def support_24_7(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛎️ Ваш запрос принят! Романтический оператор уже на связи! 💌")


async def spontaneous_trip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✈️ Чемодан собран! Сюрприз-путешествие начнётся через 24 часа! 🧳")


def main():
    application = ApplicationBuilder().token("7784104353:AAFejazyv74OqVjis3Fr3C9Km1pAUWIZg90").build()

    handlers = [
        CommandHandler("start", start),
        MessageHandler(filters.Regex(r"^💖 Удиви меня$"), surprise_me),
        MessageHandler(filters.Regex(r"^🍳 Хочу завтрак в постель$"), breakfast_in_bed),
        MessageHandler(filters.Regex(r"^📦 Хочу сюрприз$"), want_surprise),
        MessageHandler(filters.Regex(r"^🧴 Забота и внимание$"), care_and_attention),
        MessageHandler(filters.Regex(r"^🧸 Хочу обнимашек$"), want_hugs),
        MessageHandler(filters.Regex(r"^📸 Хочу фото с тобой$"), want_photo),
        MessageHandler(filters.Regex(r"^🎁 Мне нужен подарок$"), want_gift),
        MessageHandler(filters.Regex(r"^📅 Хочу идеальное свидание$"), perfect_date),
        MessageHandler(filters.Regex(r"^😘 Скажи мне что-нибудь приятное$"), romantic_phrase),
        MessageHandler(filters.Regex(r"^😱 Шок-контент!$"), shock_content),
        MessageHandler(filters.Regex(r"^⚙️ Поддержка 24/7$"), support_24_7),
        MessageHandler(filters.Regex(r"^✈️ Спонтанный отдых$"), spontaneous_trip),
    ]

    for handler in handlers:
        application.add_handler(handler)

    application.run_polling()


if __name__ == "__main__":
    main()
