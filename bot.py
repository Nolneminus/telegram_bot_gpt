from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler

from gpt import ChatGptService
from util import (load_message, send_text, send_image, show_main_menu,
                  default_callback_handler)
import credentials


# ### 1. *"Випадковий факт"*
# Телеграм-бот повинен обробляти команду /random.
# При обробці команди він надсилає заздалегідь підготовлене зображення
# та робить запит до ChatGPT із заздалегідь підготовленим промптом.
# Відповідь ChatGPT потрібно отримати та передати користувачеві.
# До повідомлення має бути прикріплена кнопка "Закінчити", натискання на яку
# працює так само, як команда /start.
# І кнопка "Хочу ще факт", натискання на яку
# працює так само, як команда /random


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = load_message('main')
    await send_image(update, context, 'main')
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        'start': 'Головне меню',
        'random': 'Дізнатися випадковий цікавий факт 🧠',
        'gpt': 'Задати питання чату GPT 🤖',
        'talk': 'Поговорити з відомою особистістю 👤',
        'quiz': 'Взяти участь у квізі ❓'
        # Додати команду в меню можна так:
        # 'command': 'button text'

    })


chat_gpt = ChatGptService(credentials.ChatGPT_TOKEN)
app = ApplicationBuilder().token(credentials.BOT_TOKEN).build()

app.add_handler(CommandHandler('start', start))
# Зареєструвати обробник команди можна так:
# app.add_handler(CommandHandler('command', handler_func))

# Зареєструвати обробник колбеку можна так:
# app.add_handler(CallbackQueryHandler(app_button, pattern='^app_.*'))
app.add_handler(CallbackQueryHandler(default_callback_handler))
app.run_polling()
