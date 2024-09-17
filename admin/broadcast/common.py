from telegram import InlineKeyboardButton
from common.common import build_back_button
from common.back_to_home_page import back_to_admin_home_page_button

broadcast_keyboard = [
    [
        InlineKeyboardButton(
            text="الجميع 👥",
            callback_data="all users",
        ),
        InlineKeyboardButton(
            text="مستخدمين محددين 👤",
            callback_data="specific users",
        ),
    ],
    [
        InlineKeyboardButton(
            text="غير المشتركين 💤",
            callback_data="none subsicribers",
        ),
        InlineKeyboardButton(
            text="المشتركين ⭐️",
            callback_data="subsicribers",
        ),
    ],
    build_back_button("back to the message"),
    back_to_admin_home_page_button[0],
]
