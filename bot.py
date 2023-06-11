from datetime import time 
from pytz import timezone

import logging

from telegram import Update
from telegram.ext import Updater, Filters, CallbackContext, Defaults 
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler

import keyboards
from moon_db import MoonData, MoonUser
import lexicon
from services import services

import os
from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

def start(update: Update, context: CallbackContext) -> None:
    '''Handles start command'''

    if update.message:
        update.message.reply_text(
                text= lexicon.start_greeting,
                reply_markup=keyboards.start_keyboard)
    else:
        update.callback_query.edit_message_text(
                text=lexicon.start_greeting,
                reply_markup=keyboards.start_keyboard)

# RUNNING
if __name__ == "__main__":
    # LOGGING
    logging.basicConfig(format="%(asctime)s %(message)s ", level=logging.INFO)

    # INITIALIZATION
    TIME_ZONE = timezone(os.getenv("TIME_ZONE"))
    updater = Updater(token=os.getenv("BOT_TOKEN"))
    Defaults(tzinfo=TIME_ZONE)
    
    for user_time in MoonUser().get_all_users():
        hours, minutes = map(int, user_time.notify_time.split(':'))
        updater.job_queue.run_daily(services.send_a_moon_info,
                    time(hour=hours, minute=minutes, tzinfo=TIME_ZONE),
                    name = str(user_time.user_id),
                    context = user_time.user_id
                    )

    dispatcher = updater.dispatcher
    updater.bot.set_chat_menu_button()


    # HANDLERS
    start_handler = CommandHandler('start', start)
    go_back_handler = CallbackQueryHandler(start, pattern='back')

    today_handler = CallbackQueryHandler(services.get_info, pattern='get_today_info')
    moon_details_handler = CallbackQueryHandler(services.get_info, pattern=lambda x: x in MoonData().get_moon_data().keys())

    user_details_handler = CallbackQueryHandler(services.show_user_info, pattern='show_user_details')
    time_set_callback_handler = CallbackQueryHandler(services.set_notification_time, pattern='set_notification_time')
    chvakson_handler = MessageHandler(Filters.regex(os.getenv(r"chvakson_pattern")), services.chvakson_response)
    time_set_message_text_handler = MessageHandler(Filters.regex(r'\d\d:\d\d'), services.set_notification_time)
    wrong_message_handler = MessageHandler(Filters.text, services.wrong_text_input)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(chvakson_handler)
    dispatcher.add_handler(time_set_callback_handler)
    dispatcher.add_handler(time_set_message_text_handler)
    dispatcher.add_handler(wrong_message_handler)
    dispatcher.add_handler(today_handler)
    dispatcher.add_handler(moon_details_handler)
    dispatcher.add_handler(go_back_handler)
    dispatcher.add_handler(user_details_handler)



    updater.start_polling(drop_pending_updates=True)
    updater.idle()
