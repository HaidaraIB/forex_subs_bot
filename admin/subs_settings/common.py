from telegram import InlineKeyboardButton


def build_subs_settings_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="إضافة اشتراكات 🆕",
                callback_data="add_subs",
            ),
        ],
        [
            InlineKeyboardButton(
                text="إلغاء اشتراكات ❌",
                callback_data="cancel_subs",
            ),
        ],
    ]
    return keyboard
