import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Налаштування логування
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Отримання токена бота з змінної оточення
TOKEN = os.getenv("BOT_TOKEN")

# Словник для зберігання стану вибору користувача
# Наприклад: user_data[user_id] = {'color': 'Кольорові', 'size': '37-41', 'quantity': 5}
user_selections = {}

# --- Функції для відображення меню ---

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Відправляє головне меню вибору кольору."""
    keyboard = [
        [InlineKeyboardButton("1) Кольорові", callback_data="select_color_Кольорові")],
        [InlineKeyboardButton("2) Натуральні", callback_data="select_color_Натуральні")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query: # Якщо це перехід назад з іншого меню
        await update.callback_query.edit_message_text(
            "Виберіть колір:", reply_markup=reply_markup
        )
        await update.callback_query.answer()
    else: # Якщо це первинний запуск через /start
        await update.message.reply_text("Виберіть колір:", reply_markup=reply_markup)
    logger.info(f"Головне меню відправлено користувачу {update.effective_user.id}")

async def send_size_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Відправляє меню вибору розміру."""
    query = update.callback_query
    await query.answer()

    # Зберігаємо вибраний колір
    color = query.data.replace("select_color_", "")
    user_selections[query.from_user.id] = {'color': color}
    logger.info(f"Користувач {query.from_user.id} вибрав колір: {color}")


    keyboard = [
        [InlineKeyboardButton("1) 29-33", callback_data="select_size_29-33")],
        [InlineKeyboardButton("2) 34-36", callback_data="select_size_34-36")],
        [InlineKeyboardButton("3) 37-41", callback_data="select_size_37-41")],
        [InlineKeyboardButton("4) 42-46", callback_data="select_size_42-46")],
        [InlineKeyboardButton("⬅️ Назад до кольору", callback_data="back_to_color_selection")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Виберіть розмір:", reply_markup=reply_markup)
    logger.info(f"Меню розмірів відправлено користувачу {query.from_user.id}")

async def ask_for_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Просить користувача ввести кількість пар."""
    query = update.callback_query
    await query.answer()

    # Зберігаємо вибраний розмір
    size = query.data.replace("select_size_", "")
    user_selections[query.from_user.id]['size'] = size
    logger.info(f"Користувач {query.from_user.id} вибрав розмір: {size}")

    keyboard = [[InlineKeyboardButton("⬅️ Назад до розміру", callback_data="back_to_size_selection")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "Вкажіть кількість пар (введіть число):",
        reply_markup=reply_markup
    )
    # Змінюємо стан користувача, щоб наступне текстове повідомлення було оброблено як кількість
    context.user_data['awaiting_quantity'] = True
    logger.info(f"Запит кількості відправлено користувачу {query.from_user.id}")

async def handle_quantity_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробляє введену користувачем кількість."""
    if 'awaiting_quantity' not in context.user_data or not context.user_data['awaiting_quantity']:
        return # Ігноруємо, якщо не очікували кількість

    try:
        quantity = int(update.message.text)
        if quantity <= 0:
            raise ValueError
        
        user_selections[update.effective_user.id]['quantity'] = quantity
        
        # Видаляємо прапор очікування кількості
        context.user_data['awaiting_quantity'] = False

        # Формуємо підсумкове повідомлення
        user_id = update.effective_user.id
        final_color = user_selections[user_id].get('color', 'не вибрано')
        final_size = user_selections[user_id].get('size', 'не вибрано')
        final_quantity = user_selections[user_id].get('quantity', 'не вказано')

        summary_text = (
            f"**Ви купуєте:**\n"
            f"Колір: **{final_color}**\n"
            f"Розмір: **{final_size}**\n"
            f"Кількість пар: **{final_quantity}**"
        )
        await update.message.reply_text(summary_text, parse_mode='Markdown')
        logger.info(f"Підсумок покупки для {user_id}: Колір={final_color}, Розмір={final_size}, Кількість={final_quantity}")

        # Очищаємо вибір користувача після завершення покупки
        if user_id in user_selections:
            del user_selections[user_id]
        
        # Після успішного завершення, можна запропонувати знову почати
        keyboard = [[InlineKeyboardButton("Почати спочатку", callback_data="start_over")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Дякуємо за покупку!", reply_markup=reply_markup)

    except ValueError:
        await update.message.reply_text("Будь ласка, введіть дійсне число для кількості пар.")
        logger.warning(f"Невірний ввід кількості від {update.effective_user.id}: {update.message.text}")


# --- Обробники кнопок "Назад" ---

async def back_to_color_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Повертає до вибору кольору."""
    # При поверненні назад, можливо, потрібно видалити або скоригувати попередній вибір,
    # але для цієї логіки ми просто перепоказуємо меню.
    await send_main_menu(update, context) # Викликаємо функцію, яка показує головне меню
    logger.info(f"Користувач {update.effective_user.id} повернувся до вибору кольору.")

async def back_to_size_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Повертає до вибору розміру."""
    # При поверненні назад з кількості, треба показати меню розмірів.
    # Відновлюємо стан, щоб користувач міг знову вибрати розмір.
    user_id = update.effective_user.id
    current_color = user_selections[user_id]['color'] if user_id in user_selections and 'color' in user_selections[user_id] else None

    if current_color: # Якщо колір був обраний, показуємо меню розмірів для цього кольору
        keyboard = [
            [InlineKeyboardButton("1) 29-33", callback_data="select_size_29-33")],
            [InlineKeyboardButton("2) 34-36", callback_data="select_size_34-36")],
            [InlineKeyboardButton("3) 37-41", callback_data="select_size_37-41")],
            [InlineKeyboardButton("4) 42-46", callback_data="select_size_42-46")],
            [InlineKeyboardButton("⬅️ Назад до кольору", callback_data="back_to_color_selection")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query = update.callback_query
        await query.answer()
        await query.edit_message_text("Виберіть розмір:", reply_markup=reply_markup)
        logger.info(f"Користувач {user_id} повернувся до вибору розміру.")
    else:
        # Якщо колір не збережений (наприклад, бот перезапустився), повертаємо до головного меню
        await send_main_menu(update, context)


# --- Функція запуску бота ---
def main() -> None:
    """Запускає бота."""
    if not TOKEN:
        logger.error("BOT_TOKEN environment variable not set. Please set it in Render dashboard.")
        print("Помилка: Токен бота не встановлено. Будь ласка, встановіть BOT_TOKEN у змінних середовища Render.")
        exit(1)

    application = ApplicationBuilder().token(TOKEN).build()

    # Обробник команди /start
    application.add_handler(CommandHandler("start", send_main_menu))
    application.add_handler(CallbackQueryHandler(send_main_menu, pattern="^start_over$")) # Для кнопки "Почати спочатку"

    # Обробники вибору кольору
    application.add_handler(CallbackQueryHandler(send_size_menu, pattern="^select_color_"))

    # Обробники вибору розміру
    application.add_handler(CallbackQueryHandler(ask_for_quantity, pattern="^select_size_"))

    # Обробник текстових повідомлень для введення кількості
    # Важливо: цей обробник повинен бути перед загальним, якщо такий є.
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_quantity_input))

    # Обробники кнопок "Назад"
    application.add_handler(CallbackQueryHandler(back_to_color_selection, pattern="^back_to_color_selection$"))
    application.add_handler(CallbackQueryHandler(back_to_size_selection, pattern="^back_to_size_selection$"))


    print("Бот запущено в режимі Polling...")
    logger.info("Бот запущено в режимі Polling. Очікування оновлень...")
    application.run_polling()

if __name__ == "__main__":
    main()
