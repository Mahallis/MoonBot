from datetime import time
from pytz import timezone
from collections import namedtuple

from telegram import Update
from telegram.ext import CallbackContext, JobQueue

from moon_db import MoonUser, MoonData
import keyboards
import lexicon

import os
from dotenv import load_dotenv

TIME_ZONE = timezone(os.getenv("TIME_ZONE"))

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

def validate_time(time) -> tuple:
    '''Checks if input in update is valid for using in job queue'''

    hours, minutes = map(int, time.split(':')) 
    if 0 <= hours < 24 and 0 <= minutes < 60:
        MoonTime = namedtuple('MoonTime', ['hours', 'minutes'])
        return MoonTime(hours, minutes)
    return ()

def update_job(queue, job_name, moon_time, user_id) -> None:
    '''Creates a new job or updates time of existing job'''

    hours, minutes = moon_time
    if job := queue.get_jobs_by_name(job_name):
        job[0].schedule_removal() 
        queue.run_daily(send_a_moon_info, 
                time(hour=hours, minute=minutes, tzinfo=TIME_ZONE), 
                name = str(user_id),
                context=user_id)
        MoonUser().set_user_time(user_id, f'{hours}:{minutes}')

def set_notification_time(update: Update, context: CallbackContext) -> None:
    '''Handles setting notification time'''

    if callback := update.callback_query:
        callback.edit_message_text(
            text = lexicon.set_notification_time_offer,
            reply_markup = keyboards.show_set_time_callback_keyboard
            )
    else:
        if moon_time := validate_time(update.message.text):
            update.message.reply_text(
                    text=lexicon.set_notification_time_success.format(update.message.text),
                    reply_markup=keyboards.set_notification_time_seccess)

            queue: JobQueue | None = context.job_queue
            user_id: int = update.message.from_user.id
           
            update_job(queue, str(update.message.from_user.id), moon_time, user_id)
        else:
            wrong_text_input(update, context)


def wrong_text_input(update: Update, context: CallbackContext) -> None:
    '''Handles a response when wrong text input recieved'''

    update.message.reply_text(text=lexicon.set_notification_time_failure + 
            '\n' +
            lexicon.set_notification_time_offer,
            reply_markup=keyboards.show_set_time_callback_keyboard)


def send_a_moon_info(context: CallbackContext) -> None:
    '''Send today info at specified time'''

    moon_data: dict = MoonData().get_moon_data()
    data = moon_data[list(moon_data.keys())[0]].text 
    headers = {key: value.header for key, value in moon_data.items()}

    context.bot.send_message(
            text=data,
            reply_markup=keyboards.show_moon_keyboard(headers),
            chat_id=context.job.context)


def get_info(update: Update, context: CallbackContext) -> None:
    '''Show MOON_INFO data'''

    moon_data: dict = MoonData().get_moon_data()
    headers = {key: value.header for key, value in moon_data.items()}

    if update.callback_query.data in moon_data.keys():
        data = moon_data[update.callback_query.data].text
    else:
        data = moon_data[list(moon_data.keys())[0]].text

    if data != update.callback_query.message.text:
        update.callback_query.edit_message_text(
                text=data,
                reply_markup=keyboards.show_moon_keyboard(headers))
    else:
        update.callback_query.answer()

def show_user_info(update: Update, context: CallbackContext) -> None:
    user_info = MoonUser().get_user_time(update.callback_query.from_user.id)
    if user_info:
        update.callback_query.edit_message_text(
                text=lexicon.show_user_info_authorized.format(user_info),
                reply_markup=keyboards.show_user_info_keyboard)
    else:
        update.callback_query.edit_message_text(
                text=lexicon.show_user_info_anauthorized,
                reply_markup=keyboards.show_user_info_keyboard)

def chvakson_response(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.username == 'Dr_chvakson':
        update.message.reply_text(
                text=os.getenv("chvakson_message"))
        context.bot.send_photo(photo=os.getenv("chvakson_photo"), chat_id=update.message.from_user.id)
    else:
        update.message.reply_text(
                text='Если Вас Алексей Чванов научил этому, то пусть сам идет туда')

def firuza_response(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.username == 'samirobojusabinaklass':
        update.message.reply_text(
                text="Не балуйся, я буду резать всё палчики!!") 
    else:
        update.message.reply_text(
                text='Вы недостаточно фирузисты')
