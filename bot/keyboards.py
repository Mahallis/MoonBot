from telegram import InlineKeyboardButton, InlineKeyboardMarkup


show_today_button: InlineKeyboardButton = InlineKeyboardButton(
        text='Показать сводку на сегодня',
        callback_data='get_today_info')

set_time_button: InlineKeyboardButton = InlineKeyboardButton(
        text='Установить время уведомлений',
        callback_data='set_notification_time')

show_user_details_menu_button: InlineKeyboardButton = InlineKeyboardButton(
        text='Пользователь',
        callback_data='show_user_details')

go_back_button: InlineKeyboardButton = InlineKeyboardButton(
        text='Вернуться назад',
        callback_data='back')


start_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup([
        [set_time_button],
        [show_today_button],
        [show_user_details_menu_button],
    ])


def show_moon_keyboard(headers) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        *[[InlineKeyboardButton(
            text=value,
            callback_data=key
        )] for key, value in headers.items()],
        [go_back_button],
    ])


show_set_time_callback_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup([
        [go_back_button],
    ])

set_notification_time_seccess: InlineKeyboardMarkup = InlineKeyboardMarkup([
        [show_today_button],
        [go_back_button],
    ])

show_user_info_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup([
        [set_time_button],
        [go_back_button],
    ])
