from pytz import timezone

import logging

from telegram.ext import Updater, Filters, Defaults, Dispatcher
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler

from moon_db import MoonData
import config, services

import os
from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    TIME_ZONE = os.getenv("TIME_ZONE")
    BOT_TOKEN = os.getenv("BOT_TOKEN")

# RUNNING
if __name__ == "__main__":
    # LOGGING
    logging.basicConfig(format="%(asctime)s %(message)s ", level=logging.INFO)

    # INITIALIZATION
    if TIME_ZONE and BOT_TOKEN:
        time_zone = timezone(TIME_ZONE)
        updater: Updater = Updater(token=BOT_TOKEN)
        Defaults(tzinfo=time_zone)
    else:
        raise ValueError("File .env is not correct, or does not exist.")

    config.set_time_after_restart(updater, time_zone)
    dispatcher: Dispatcher = updater.dispatcher
    updater.bot.set_chat_menu_button()

    # HANDLERS
    start_handler = CommandHandler('start', services.start)
    go_back_handler = CallbackQueryHandler(services.start, pattern='back')

    today_handler = CallbackQueryHandler(
        services.get_info, pattern='get_today_info'
    )
    moon_details_handler = CallbackQueryHandler(
        services.get_info,
        pattern=lambda x: x in MoonData().get_moon_data().keys()
    )

    user_details_handler = CallbackQueryHandler(
        services.show_user_info,
        pattern='show_user_details'
    )
    time_set_callback_handler = CallbackQueryHandler(
        services.set_notification_time,
        pattern='set_notification_time'
    )
    if chvakson_pattern := os.getenv(r"chvakson_pattern"):
        chvakson_handler = MessageHandler(
            Filters.regex(chvakson_pattern),
            services.chvakson_response
        )
        dispatcher.add_handler(chvakson_handler)

    firuza_handler = MessageHandler(
        Filters.regex(r"Самир бомбежка"),
        services.firuza_response
    )
    time_set_message_text_handler = MessageHandler(
        Filters.regex(r'^\d\d:\d\d$'),
        services.set_notification_time
    )
    wrong_message_handler = MessageHandler(
        Filters.text,
        services.wrong_text_input
    )

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(firuza_handler)
    dispatcher.add_handler(time_set_callback_handler)
    dispatcher.add_handler(time_set_message_text_handler)
    dispatcher.add_handler(wrong_message_handler)
    dispatcher.add_handler(today_handler)
    dispatcher.add_handler(moon_details_handler)
    dispatcher.add_handler(go_back_handler)
    dispatcher.add_handler(user_details_handler)

    updater.start_polling(drop_pending_updates=True)
    updater.idle()
