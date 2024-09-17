from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def build_statistics_keyboard():
    statistics_keyboard = [
        [
            InlineKeyboardButton(
                text="إحصائيات المستخدمين",
                callback_data="in_bot_statistics",
            ),
            InlineKeyboardButton(
                text="ملف إكسل",
                callback_data="excel_statistics",
            ),
        ],
    ]
    return statistics_keyboard


def stringify_statistics(all_users:int, subsicribers:int):
    return (
        f"عدد المستخدمين الكلي: <b>{all_users}</b>\n\n"
        f"عدد المشتركين: <b>{subsicribers}</b>\n\n"
    )
