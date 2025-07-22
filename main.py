import logging
import os
from pymongo import MongoClient
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext



user_data = {} # user_id: {'quiz_active': True, 'current_question': {}, 'score': 0}

def get_mongo_collection():
    try:
        client = MongoClient('localhost', 27017)
        db = client[hist]
        return db[question]
    except:
        logger.error("Error connecting to database")


async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    await update.message.reply_html(rf"Добро пожаловать! Я — ваш помощник по истории и науке. Здесь вы сможете узнать интересные факты, пройти викторины и получить полезную информацию о великих ученых, открытиях и исторических событиях.")

async def menu(update: Update, context: CallbackContext):
    text = update.message.text
    if text == "Викторина":
        await start_quiz(update, context)
    elif text == "Рассказать историю":
        await start_tell_story(update, context)
    #комментарий
    else text == "Задать вопрос":
        await ask_question(update, context) #подключение нейронки

async def start_quiz(update: Update, context: CallbackContext):
    collection = get_mongo_collection()
    question_data = list(collection.aggregate(pipeline))
    question = question_data[0]
    user_id = update.effective_user.id
    user_data[user_id] = {'quiz_active': True, 'current_question': question,
                          'score': user_data.get(user_id, {}).get('score', 0)}

    options = question['options']
    keyboard = [[option] for option in options]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(question['question'], reply_markup=reply_markup)
    context.user_data['state'] = QUIZ_QUESTION

async def handle_quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id not in user_data or not user_data[user_id]['quiz_active']:
        await update.message.reply_text("Викторина не активна. Чтобы начать, выберите 'Викторина' в меню.")
        return

    current_question = user_data[user_id]['current_question']
    user_answer = update.message.text
    correct_answer = current_question['correct_answer']
    user_score = user_data[user_id]['score']

    if user_answer == correct_answer:
        user_score += 1
        user_data[user_id]['score'] = user_score
        await update.message.reply_text(f"Здорово! Это правильный ответ! Твой текущий рейтинг: {user_score}",
                                        reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_text(
            f"Очень жаль, это неправильный ответ. Правильный ответ: '{correct_answer}'. Твой текущий рейтинг: {user_score}",
            reply_markup=ReplyKeyboardRemove())

    user_data[user_id]['quiz_active'] = False  # Завершаем текущий раунд викторины
    await update.message.reply_text("Хочешь продолжить?",
                                    reply_markup=ReplyKeyboardMarkup([['Викторина', 'Рассказать историю?']],
                                                                     resize_keyboard=True, one_time_keyboard=True))
    context.user_data['state'] = None

async def tell_story(update: Update, context: CallbackContext):
    #collection = get_mongo_collection()

async def main():
    application = Application.builder().token('7830391433:AAEA9XBPgBlunk2wnAQufmyKuu0YPwkd1lc').build()
    application.add_hadler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filter.Regex('^(Викторина|Рассказать историю')))
    application.add_handler(MessageHadler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, handle_quiz_answer))

    logger.info("Running...")
    application.run_polling(allowed_updates = Update.ALL_TYPES)

    if __name__ == '__main__':
        main()