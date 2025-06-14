from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я работаю на Render 😊")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получение токена бота из переменной окружения
TOKEN = os.getenv("BOT_TOKEN")

# --- Главное меню ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет главное меню при команде /start."""
    keyboard = [
        [InlineKeyboardButton("Виберіть колір", callback_data="main_menu_1")],
        [InlineKeyboardButton("Виберіть розмір", callback_data="main_menu_2")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите пункт:", reply_markup=reply_markup)
    logger.info(f"Главное меню отправлено пользователю {update.effective_user.id}")

# --- Подменю 1 (3 пункта) ---
async def show_sub_menu_1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает подменю 1."""
    query = update.callback_query
    await query.answer() # Всегда отвечайте на callback_query

    keyboard = [
        [InlineKeyboardButton("Кольорові", callback_data="sub_menu_1_item_1")],
        [InlineKeyboardButton("Чорні", callback_data="sub_menu_1_item_2")],
        [InlineKeyboardButton("Білі", callback_data="sub_menu_1_item_3")],
        [InlineKeyboardButton("Назад в головне меню", callback_data="back_to_main")] # Кнопка "Назад"
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Вы выбрали Пункт 1. Выберите опцию:", reply_markup=reply_markup)
    logger.info(f"Подменю 1 отправлено пользователю {query.from_user.id}")

# --- Подменю 2 (4 пункта) ---
async def show_sub_menu_2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает подменю 2."""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("29-33", callback_data="sub_menu_2_item_1")],
        [InlineKeyboardButton("34-37", callback_data="sub_menu_2_item_2")],
        [InlineKeyboardButton("38-41", callback_data="sub_menu_2_item_3")],
        [InlineKeyboardButton("42-45", callback_data="sub_menu_2_item_4")],
        [InlineKeyboardButton("Назад в головне меню", callback_data="back_to_main")] # Кнопка "Назад"
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Вы выбрали Пункт 2. Выберите опцию:", reply_markup=reply_markup)
    logger.info(f"Подменю 2 отправлено пользователю {query.from_user.id}")

# --- Обработчик выбора пунктов подменю ---
async def handle_sub_menu_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает выбор пунктов из подменю."""
    query = update.callback_query
    await query.answer(f"Вы выбрали: {query.data}") # Всплывающее уведомление для пользователя

    # Здесь можно добавить логику в зависимости от выбранного пункта
    response_text = f"Вы выбрали: {query.data}. Пока это просто заглушка."
    await query.edit_message_text(response_text) # Изменяем сообщение на подтверждение выбора
    logger.info(f"Пользователь {query.from_user.id} выбрал {query.data}")

    # Опционально: можно предложить вернуться в главное меню или показать кнопки действия
    # keyboard = [[InlineKeyboardButton("Вернуться в главное меню", callback_data="back_to_main")]]
    # await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))


# --- Обработчик кнопки "Назад" ---
async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Возвращает в главное меню."""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Виберіть колір", callback_data="main_menu_1")],
        [InlineKeyboardButton("Виберіть розмір", callback_data="main_menu_2")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Выберите пункт:", reply_markup=reply_markup)
    logger.info(f"Возвращение в главное меню для пользователя {query.from_user.id}")


def main() -> None:
    """Запускает бота."""
    if not TOKEN:
        logger.error("BOT_TOKEN environment variable not set. Please set it in Render dashboard.")
        print("Ошибка: Токен бота не установлен. Пожалуйста, установите BOT_TOKEN в переменных окружения Render.")
        exit(1)

    application = ApplicationBuilder().token(TOKEN).build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))

    # Добавляем CallbackQueryHandler для каждого пункта меню
    application.add_handler(CallbackQueryHandler(show_sub_menu_1, pattern="^main_menu_1$"))
    application.add_handler(CallbackQueryHandler(show_sub_menu_2, pattern="^main_menu_2$"))
    application.add_handler(CallbackQueryHandler(back_to_main_menu, pattern="^back_to_main$"))

    # Общий обработчик для пунктов подменю (начинаются с "sub_menu_")
    # Важно: этот обработчик должен быть ПОСЛЕ более специфичных обработчиков,
    # если их callback_data начинается с "sub_menu_", чтобы избежать конфликтов.
    application.add_handler(CallbackQueryHandler(handle_sub_menu_item, pattern="^sub_menu_"))


    print("Бот запущен в режиме Polling...")
    logger.info("Бот запущен в режиме Polling. Ожидание обновлений...")
    application.run_polling()

if __name__ == "__main__":
    main()
print("Бот запущен...")
app.run_polling()
