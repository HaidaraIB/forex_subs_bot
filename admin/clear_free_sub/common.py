from telegram import InlineKeyboardButton


def build_clear_free_sub_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="جميع المستخدمين",
                callback_data="all_clear_free_sub",
            ),
            InlineKeyboardButton(
                text="مستخدمين محددين",
                callback_data="specific_clear_free_sub",
            ),
        ]
    ]
    return keyboard