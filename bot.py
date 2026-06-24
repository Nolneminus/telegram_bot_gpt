from idlelib import query

from openai.types.responses import response
from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler, MessageHandler, filters, Application

from gpt import ChatGptService
from util import (load_message, send_text, send_image, show_main_menu,
                  default_callback_handler, load_prompt, send_text_buttons)
import credentials

chat_modes = {}

        # MAIN
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = load_message('main')
    await send_image(update, context, 'main')
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        'start': 'Головне меню',
        'random': 'Дізнатися випадковий цікавий факт 🧠',
        'gpt': 'Задати питання чату GPT 🤖',
        'talk': 'Поговорити з відомою особистістю 👤',
        'quiz': 'Взяти участь у квізі ❓',
        'translate': 'Перекласти текст 🌍'
        # Додати команду в меню можна так:
        # 'command': 'button text'

    })

        # RANDOM
async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_text(update, context, load_message('random'))
    prompt = load_prompt('random')
    response = await chat_gpt.send_question(prompt, 'Давай рандомний факт')
    await send_image(update, context, 'random')
    await send_text_buttons(update, context, response, {
        'random_finish': 'Закінчити',
        'random_one_more' : 'Хочу ще факт'
    })
async def random_buttons_handler(update: Update, context ):
    query = update.callback_query.data
    if query == 'random_finish':
        await start(update, context)
    elif query == 'random_one_more':
        await random(update,context)
    await update.callback_query.answer()

        # GPT
async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_modes[update.message.from_user.id] = 'GPT_MODE'
    await send_image(update, context, 'gpt')
    await send_text(update, context, load_message('gpt'))

async def gpt_buttons_handler(update: Update, context ):
    query = update.callback_query.data
    if query == 'gpt_finish':
        chat_modes[update.callback_query.from_user.id] = None
        await start(update, context)
    await update.callback_query.answer()

    # TALK
talk_persons = {
    'talk_cobain': 'talk_cobain',
    'talk_queen': 'talk_queen',
    'talk_tolkien': 'talk_tolkien',
    'talk_nietzsche': 'talk_nietzsche',
    'talk_hawking': 'talk_hawking'
}
async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_modes[update.message.from_user.id] = 'TALK_MODE'
    await send_image(update, context, "talk" )
    await send_text_buttons(update, context, load_message('talk'),{
        'talk_cobain': 'Курт Кобейн',
        'talk_queen': 'Єлизавета II',
        'talk_tolkien': 'Джон Толкін',
        'talk_nietzsche': 'Фрідріх Ніцше',
        'talk_hawking': 'Стівен Гокінг'
    })

async def talk_buttons_handler(update: Update, context):
    query = update.callback_query.data
    if query == 'talk_finish':
        chat_modes[update.callback_query.from_user.id] = None
        await start(update, context)
    if query != 'talk_finish':
        context.user_data['person'] = talk_persons[query]
        await send_image(update,context,query)
    await update.callback_query.answer()

        # QUIZ
quiz_scores = {}

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_modes[update.message.from_user.id] = 'QUIZ_MODE'
    await send_image(update,context,'quiz')
    await send_text_buttons(update, context, load_message('quiz'), buttons={
        'quiz_prog': 'Програмування',
        'quiz_math': 'Математичні теорії',
        'quiz_biology': 'Біологія',
        'quiz_more': 'питання на ту ж тему, що й попереднє'
    }
                            )
    chat_gpt.set_prompt(load_prompt('quiz'))
    quiz_scores[update.message.from_user.id] = 0

async def quiz_buttons_handler(update: Update, context):
    query = update.callback_query.data
    response = await chat_gpt.add_message(query)
    await send_text(update,context,response)
    chat_modes[update.callback_query.from_user.id] = 'QUIZ_ANSWER'
    await update.callback_query.answer()

    # TRANSLATOR
languages = {
    'trans_eng': 'Англійська',
    'trans_esp': 'Іспанська',
    'trans_pol': 'Польська',
    'trans_ger': 'Німецька'
}
user_language = {}
async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image(update,context, 'translate')
    await send_text_buttons(update,context,load_message('translate'), buttons={
        'trans_eng': 'Англійська',
        'trans_esp': 'Іспанська',
        'trans_pol': 'Польська',
        'trans_ger': 'Німецька'
    })

async def translate_buttons_handler(update: Update, context):
    query = update.callback_query.data
    if query in languages:
        user_language[update.callback_query.from_user.id] = languages[query]
        chat_modes[update.callback_query.from_user.id] = 'TRANSLATE_ANSWER'
        await send_text(update,context,f'Який текст треба перекласти на {languages[query]}')
    elif query == 'trans_finish':
        chat_modes[update.callback_query.from_user.id] = None
        await start(update,context)
    elif query == 'trans_any_lang':
        chat_modes[update.callback_query.from_user.id] = 'TRANSLATE_ANSWER'
        await translate(update,context)
    await update.callback_query.answer()



        # Обработчик
async def plain_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = chat_modes.get(update.message.from_user.id)
    text = update.message.text
    if mode is None:
        if text == '/start':
            await start(update,context)
        elif text == '/random':
            await random(update,context)
        elif text == '/gpt':
            await gpt(update,context)
        elif text == '/talk':
            await talk(update,context)
        elif text == '/quiz':
            await quiz(update,context)
        elif text == '/translate':
            await translate(update,context)
        else:
            await send_text(update,context,'i dont know such command. Use /start command for information')
    elif mode == 'TRANSLATE_ANSWER':
        lang = user_language.get(update.message.from_user.id)
        pt = f'''Переклати наступний текст на {lang}. Поверни тільки переклад без пояснень'''
        response = await chat_gpt.send_question(pt, update.message.text)
        await send_text_buttons(update, context, response, {
            'trans_any_lang': 'Інша мова',
            'trans_finish': 'Закінчити'
            })
    elif mode == 'GPT_MODE':
        pt = load_prompt('gpt')
        response = await chat_gpt.send_question(pt, update.message.text)
        await send_text_buttons(update, context, response, {
            'gpt_finish': 'Закінчити'
        })
    elif mode == 'TALK_MODE':
        person = context.user_data['person']
        pt = load_prompt(person)
        response = await chat_gpt.send_question(pt, update.message.text)
        await send_text_buttons(update, context, response, {
            'talk_finish': 'Закінчити'
        })
    elif mode == 'QUIZ_ANSWER':
        answer = await chat_gpt.add_message(text)
        if answer == "Правильно!":
            quiz_scores[update.message.from_user.id] +=1
        await send_text(update,context,answer)
        await send_text(update,context,f'Ваші бали {quiz_scores[update.message.from_user.id]}')
        chat_modes[update.message.from_user.id] = 'QUIZ_MODE'







chat_gpt = ChatGptService(credentials.ChatGPT_TOKEN)
app = ApplicationBuilder().token(credentials.BOT_TOKEN).build()

# Зареєструвати обробник команди можна так:
# app.add_handler(CommandHandler('command', handler_func))
app.add_handler(MessageHandler(None, plain_text_handler))
# app.add_handler(CommandHandler('start', start))


# Зареєструвати обробник колбеку можна так:
app.add_handler(CallbackQueryHandler(random_buttons_handler, pattern='^random_.*'))
app.add_handler(CallbackQueryHandler(gpt_buttons_handler, pattern='^gpt_.*'))
app.add_handler(CallbackQueryHandler(talk_buttons_handler, pattern='^talk_.*'))
app.add_handler(CallbackQueryHandler(quiz_buttons_handler, pattern='^quiz_.*'))
app.add_handler(CallbackQueryHandler(translate_buttons_handler, pattern='^trans_.*'))
app.add_handler(CallbackQueryHandler(default_callback_handler))
app.run_polling()
