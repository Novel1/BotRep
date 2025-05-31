import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackContext,
    JobQueue
)
import requests
from telegram import ReplyKeyboardRemove
import random
from datetime import datetime, timedelta
import csv
import io
import os
import requests
from io import BytesIO

# Настройка логгирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Константы для состояний
CHOOSING, TYPING_WISH, TYPING_SOUL, HOLIDAY_NAME, HOLIDAY_STYLE = range(5)
ADMIN_ID = int(os.getenv('1291710833', 1291710833))  # Замените на реальный ID

# Данные для ответов
RESPONSES = {
    'adventure': {
        'text': "Приготовься к приключениям в ближайшие выходные!",
        'image': 'https://upload.wikimedia.org/wikipedia/ru/3/37/Adventure_Time_-_Title_card.png'
    },
    'something_new': "Будь готова испытать что-то новое!",
    'breakfast': "Ожидай сюрприз-завтрак совсем скоро!",
    'handmade': "Сделаем что-то своими руками — готовься к творчеству!",
    'snacks': {
        'drink': "Жди, я уже в пути",
        'food': "Жди, я уже в пути",
        'order': "Напиши, что бы ты хотела — будет исполнено!"
    },
    'surprise': "Запрос принят. Ожидай что-нибудь — от бусинки до чего-то большего, чем ты можешь представить",
    'hugs': "Порция обнимашек уже в пути 💞",
    'care': "В течение 24 часов ты почувствуешь мою заботу",
    'shock': lambda: f"{random.randint(1, 100)}",
    'games': "Раздел в разработке. Скоро здесь появится что-то интересное!",
    'flirt': "Готовься к весёлым и романтическим заданиям. Легкий флирт включён!",
    'secret': "Ты активировала квест. Жди первую инструкцию...",
    'soul': "Сегодня вечером поговорим по душам. Напиши тему, которая тебя волнует",
    'about': "Я — твой персональный романтический помощник, созданный для счастья 💘И, кстати... я — небольшой, но особенный подарок на нашу годовщину 🎁❤️",
    'settings': "Раздел пока в разработке. Обновления скоро"
}

# Главное меню
MAIN_KEYBOARD = [
    ["😱 Удиви меня", "🪄 Что-то новенькое"],
    ["🍳 Хочу завтрак в постель", "🧰 Кружок Очумелые ручки"],
    ["➕ Время для вкусняшек", "📦 Хочу сюрприз"],
    ["🧸 Хочу обнимашек", "🧴 Забота и внимание"],
    ["🎲 Шок-контент", "🎮 Мини-игры"],
    ["🪄 Добавить свое пожелание", "🎉 Праздничные режимы"],
    ["💃 Флирт-режим", "💌 Секретный уровень"],
    ["🧠 Для души", "⚙️ О нас / Помощь"]
]

# Меню вкусняшек
SNACKS_KEYBOARD = [
    ["🍹 Попить", "🍔 Покушать"],
    ["📝 Заказать что-нибудь"],
    ["🔙 Назад"]
]

# Меню "О нас"
ABOUT_KEYBOARD = [
    ["🤖 Инфо о боте"],
    ["🛠️ Настройки"],
    ["⚙️ Админский режим"],
    ["🔙 Назад"]
]

# Админское меню
ADMIN_KEYBOARD = [
    ["👁️ Логи активности", "📬 Уведомления"],
    ["🛎️ Напоминания", "📥 Экспорт пожеланий"],
    ["🔙 Назад"]
]

# База данных (временная)
users_wishes = {}
activity_log = []
user_requests = []
notification_enabled = True
last_surprise_date = {}


def log_activity(user_id: int, action: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"{timestamp} - {user_id} - {action}"
    activity_log.append(entry)
    logger.info(entry)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    log_activity(user.id, "Запустил бота")
    await show_main_menu(update, "Привет, солнышко! 💓\nВыбирай, чего тебе хочется:")


async def show_main_menu(update: Update, text: str):
    await update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardMarkup(
            MAIN_KEYBOARD,
            resize_keyboard=True,
            one_time_keyboard=False
        )
    )
    return ConversationHandler.END


# --- Обработчики основных команд ---
async def surprise_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    log_activity(user.id, "Удиви меня")

    try:
        # Загружаем изображение по URL
        response = requests.get(RESPONSES['adventure']['image'])
        photo = BytesIO(response.content)
        photo.name = 'adventure_time.jpg'

        await update.message.reply_photo(
            photo=photo,
            caption=RESPONSES['adventure']['text']
        )
    except Exception as e:
        logger.error(f"Ошибка при загрузке изображения: {e}")
        await update.message.reply_text(RESPONSES['adventure']['text'])


async def something_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    log_activity(user.id, "Что-то новенькое")
    await update.message.reply_text(RESPONSES['something_new'])


async def breakfast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    log_activity(user.id, "Завтрак в постель")
    await update.message.reply_text(RESPONSES['breakfast'])


async def handmade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    log_activity(user.id, "Очумелые ручки")
    await update.message.reply_text(RESPONSES['handmade'])


async def surprise(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    log_activity(user.id, "Хочу сюрприз")
    last_surprise_date[user.id] = datetime.now()
    await update.message.reply_text(RESPONSES['surprise'])


async def hugs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    log_activity(user.id, "Хочу обнимашек")
    await update.message.reply_text(RESPONSES['hugs'])


async def care(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    log_activity(user.id, "Забота и внимание")
    await update.message.reply_text(RESPONSES['care'])


async def shock_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    log_activity(user.id, "Шок-контент")
    await update.message.reply_text(RESPONSES['shock']())


async def games(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    log_activity(user.id, "Мини-игры")
    await update.message.reply_text(RESPONSES['games'])


async def flirt_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    log_activity(user.id, "Флирт-режим")
    await update.message.reply_text(RESPONSES['flirt'])


async def secret_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    log_activity(user.id, "Секретный уровень")
    await update.message.reply_text(RESPONSES['secret'])


async def about_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    log_activity(user.id, "Инфо о боте")
    await update.message.reply_text(RESPONSES['about'])


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    log_activity(user.id, "Настройки")
    await update.message.reply_text(RESPONSES['settings'])


# --- Обработчики меню вкусняшек ---
async def snacks_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    log_activity(user.id, "Меню вкусняшек")
    await update.message.reply_text(
        "Выбирай:",
        reply_markup=ReplyKeyboardMarkup(SNACKS_KEYBOARD, resize_keyboard=True)
    )


async def snacks_drink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    log_activity(user.id, "Попить")
    await update.message.reply_text(RESPONSES['snacks']['drink'])
    await show_main_menu(update, "Что-нибудь еще?")


async def snacks_food(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    log_activity(user.id, "Покушать")
    await update.message.reply_text(RESPONSES['snacks']['food'])
    await show_main_menu(update, "Что-нибудь еще?")


# --- Диалог для пользовательских пожеланий ---
async def custom_wish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    log_activity(user.id, "Добавить пожелание")
    await update.message.reply_text("Напиши, чего тебе хочется — и я это реализую!",
                                    reply_markup=ReplyKeyboardRemove())
    return TYPING_WISH


async def save_wish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    wish_text = update.message.text
    timestamp = datetime.now()
    user_requests.append((user.id, user.first_name, wish_text, timestamp))
    log_activity(user.id, f"Пожелание: {wish_text}")

    # Отправляем уведомление админу, если включены уведомления
    if notification_enabled:
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"🎉 Новое пожелание от {user.first_name}!\n\n"
                     f"💬 Текст: {wish_text}\n"
                     f"🕒 Время: {timestamp.strftime('%Y-%m-%d %H:%M')}"
            )
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления админу: {e}")

    await update.message.reply_text("Записал! Скоро это появится в твоей жизни ✨")
    await show_main_menu(update, "Что-нибудь еще?")
    return ConversationHandler.END


# --- Диалог "По душам" ---
async def soul_talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    log_activity(user.id, "По душам")
    await update.message.reply_text(RESPONSES['soul'], reply_markup=ReplyKeyboardRemove())
    return TYPING_SOUL


async def save_soul_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    topic = update.message.text
    timestamp = datetime.now()
    user_requests.append((user.id, user.first_name, f"Тема по душам: {topic}", timestamp))
    log_activity(user.id, f"Тема для разговора: {topic}")
    await update.message.reply_text("Хорошо, обсудим это сегодня вечером 🌙")
    await show_main_menu(update, "Что-нибудь еще?")
    return ConversationHandler.END


# --- Праздничные режимы ---
async def holiday_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    log_activity(user.id, "Праздничные режимы")
    await update.message.reply_text("Введите название праздника:", reply_markup=ReplyKeyboardRemove())
    return HOLIDAY_NAME


async def holiday_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['holiday_name'] = update.message.text
    keyboard = [["🎬 В стиле фильма", "🏠 Уютно"], ["😂 Шутливо"], ["🔙 Назад"]]
    await update.message.reply_text("Выберите стиль:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return HOLIDAY_STYLE


async def holiday_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    style = update.message.text
    name = context.user_data.get("holiday_name", "Без названия")
    log_activity(user.id, f"Праздник: {name}, Стиль: {style}")
    await show_main_menu(update, f"Отлично! Праздник «{name}» в стиле «{style}» записан!")
    return ConversationHandler.END


# --- Меню "О нас" ---
async def about_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    log_activity(user.id, "Меню 'О нас'")
    await update.message.reply_text(
        "Выберите раздел:",
        reply_markup=ReplyKeyboardMarkup(ABOUT_KEYBOARD, resize_keyboard=True)
    )


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    if user.id == ADMIN_ID:
        log_activity(user.id, "Админ-панель")
        await update.message.reply_text(
            "Админ-панель:",
            reply_markup=ReplyKeyboardMarkup(ADMIN_KEYBOARD, resize_keyboard=True)
        )
        return CHOOSING
    await update.message.reply_text("⛔ Доступ запрещен")
    return ConversationHandler.END


# --- Админские функции ---
async def export_wishes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    if user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Доступ запрещен")
        return

    log_activity(user.id, "Экспорт пожеланий")
    if not user_requests:
        await update.message.reply_text("Список пожеланий пуст")
        return

    # Создаем более читаемый CSV
    csv_data = io.StringIO()
    writer = csv.writer(csv_data)

    # Заголовки с описанием
    writer.writerow(["Имя", "Пожелание", "Дата и время"])

    for username, wish, timestamp in user_requests:
        writer.writerow([
            username,
            wish,
            timestamp.strftime("%Y-%m-%d %H:%M")
        ])

    csv_data.seek(0)
    await update.message.reply_document(
        document=io.BytesIO(csv_data.getvalue().encode()),
        filename="romantic_wishes.csv",
        caption="Вот список всех пожеланий 🌟"
    )


async def show_activity_log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    if user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Доступ запрещен")
        return

    log_activity(user.id, "Просмотр логов")
    if not activity_log:
        await update.message.reply_text("Логи активности пусты")
        return

    # Отправляем последние 20 записей
    log_text = "📝 Последние действия:\n\n" + "\n".join(activity_log[-20:])
    await update.message.reply_text(log_text)


async def admin_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    if user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Доступ запрещен")
        return

    global notification_enabled
    notification_enabled = not notification_enabled
    status = "включены" if notification_enabled else "выключены"
    log_activity(user.id, f"Уведомления: {status}")
    await update.message.reply_text(f"Уведомления о новых пожеланиях теперь {status} 🔔")


async def admin_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    if user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Доступ запрещен")
        return

    log_activity(user.id, "Проверка напоминаний")

    # Проверяем, когда последний раз были сюрпризы
    reminder_text = "🎯 Статус сюрпризов:\n\n"
    now = datetime.now()

    if not last_surprise_date:
        reminder_text += "Вы еще не делали сюрпризов 😢"
    else:
        for user_id, last_date in last_surprise_date.items():
            days_passed = (now - last_date).days
            reminder_text += f"• Пользователь {user_id}: "

            if days_passed > 7:
                reminder_text += f"❌ Очень давно не было сюрприза ({days_passed} дней)"
            elif days_passed > 3:
                reminder_text += f"⚠️ Давно не было сюрприза ({days_passed} дней)"
            else:
                reminder_text += f"✅ Недавно был сюрприз ({days_passed} дней назад)"

            reminder_text += "\n"

    reminder_text += "\n💡 Совет: сделайте сюрприз сегодня!"
    await update.message.reply_text(reminder_text)


# --- Функция для кнопки "Назад" ---
async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update, "Главное меню 💓")
    return ConversationHandler.END


# --- Периодические напоминания ---
async def send_reminders(context: CallbackContext):
    job = context.job
    now = datetime.now()

    # Проверяем для каждого пользователя, когда был последний сюрприз
    for user_id, last_date in last_surprise_date.items():
        days_passed = (now - last_date).days

        # Отправляем напоминание, если прошло больше 3 дней
        if days_passed >= 3:
            try:
                await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=f"💌 Напоминание!\n\n"
                         f"Вы давно не делали сюрприз пользователю {user_id}.\n"
                         f"Последний сюрприз был {days_passed} дней назад.\n\n"
                         f"Сделайте что-нибудь приятное сегодня! 💖"
                )
                # Обновляем дату, чтобы не спамить
                last_surprise_date[user_id] = now
            except Exception as e:
                logger.error(f"Ошибка отправки напоминания: {e}")


# --- Настройка обработчиков ---
def setup_handlers(application):
    # Главный обработчик диалогов
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(filters.Regex(r"^⚙️ О нас / Помощь$"), about_menu),
            MessageHandler(filters.Regex(r"^⚙️ Админский режим$"), admin_panel),
            MessageHandler(filters.Regex(r"^📝 Заказать что-нибудь$"), custom_wish),
            MessageHandler(filters.Regex(r"^🪄 Добавить свое пожелание$"), custom_wish),
            MessageHandler(filters.Regex(r"^🎉 Праздничные режимы$"), holiday_menu),
            MessageHandler(filters.Regex(r"^🧠 Для души$"), soul_talk),
        ],
        states={
            TYPING_WISH: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_wish),
                MessageHandler(filters.Regex(r"^🔙 Назад$"), back_to_main)
            ],
            TYPING_SOUL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_soul_topic),
                MessageHandler(filters.Regex(r"^🔙 Назад$"), back_to_main)
            ],
            HOLIDAY_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, holiday_name),
                MessageHandler(filters.Regex(r"^🔙 Назад$"), back_to_main)
            ],
            HOLIDAY_STYLE: [
                MessageHandler(filters.Regex(r"^(🎬 В стиле фильма|🏠 Уютно|😂 Шутливо)$"), holiday_style),
                MessageHandler(filters.Regex(r"^🔙 Назад$"), back_to_main)
            ],
            CHOOSING: [
                MessageHandler(filters.Regex(r"^📥 Экспорт пожеланий$"), export_wishes),
                MessageHandler(filters.Regex(r"^👁️ Логи активности$"), show_activity_log),
                MessageHandler(filters.Regex(r"^📬 Уведомления$"), admin_notifications),
                MessageHandler(filters.Regex(r"^🛎️ Напоминания$"), admin_reminders),
                MessageHandler(filters.Regex(r"^🔙 Назад$"), back_to_main)
            ]
        },
        fallbacks=[CommandHandler('start', start)],
        allow_reentry=True
    )

    # Регистрация обработчиков команд
    application.add_handler(conv_handler)

    # Обработчики кнопок
    application.add_handler(MessageHandler(filters.Regex(r"^😱 Удиви меня$"), surprise_me))
    application.add_handler(MessageHandler(filters.Regex(r"^🪄 Что-то новенькое$"), something_new))
    application.add_handler(MessageHandler(filters.Regex(r"^🍳 Хочу завтрак в постель$"), breakfast))
    application.add_handler(MessageHandler(filters.Regex(r"^🧰 Кружок Очумелые ручки$"), handmade))
    application.add_handler(MessageHandler(filters.Regex(r"^📦 Хочу сюрприз$"), surprise))
    application.add_handler(MessageHandler(filters.Regex(r"^🧸 Хочу обнимашек$"), hugs))
    application.add_handler(MessageHandler(filters.Regex(r"^🧴 Забота и внимание$"), care))
    application.add_handler(MessageHandler(filters.Regex(r"^🎲 Шок-контент$"), shock_content))
    application.add_handler(MessageHandler(filters.Regex(r"^🎮 Мини-игры$"), games))
    application.add_handler(MessageHandler(filters.Regex(r"^💃 Флирт-режим$"), flirt_mode))
    application.add_handler(MessageHandler(filters.Regex(r"^💌 Секретный уровень$"), secret_level))
    application.add_handler(MessageHandler(filters.Regex(r"^🤖 Инфо о боте$"), about_bot))
    application.add_handler(MessageHandler(filters.Regex(r"^🛠️ Настройки$"), settings))

    # Обработчики меню
    application.add_handler(MessageHandler(filters.Regex(r"^➕ Время для вкусняшек$"), snacks_menu))
    application.add_handler(MessageHandler(filters.Regex(r"^🍹 Попить$"), snacks_drink))
    application.add_handler(MessageHandler(filters.Regex(r"^🍔 Покушать$"), snacks_food))

    # Навигация
    application.add_handler(MessageHandler(filters.Regex(r"^🔙 Назад$"), back_to_main))


def main():
    application = ApplicationBuilder().token("8054818207:AAFq18jcwhO0h1i28mH-H2B_btNIMRyJLqQ").build()

    # Настраиваем периодические напоминания (только если JobQueue доступен)
    if application.job_queue:
        application.job_queue.run_repeating(
            send_reminders,
            interval=timedelta(days=1),
            first=10
        )
    else:
        logger.warning("JobQueue не доступен. Напоминания отключены.")

    setup_handlers(application)
    application.run_polling()


if __name__ == "__main__":
    main()
