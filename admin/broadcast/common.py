from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram.ext import ContextTypes
from common.common import build_back_button
from common.back_to_home_page import back_to_admin_home_page_button
import models

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


async def send_to(users: list[models.User], context: ContextTypes.DEFAULT_TYPE):
    msg: Message = context.user_data["the message"]
    for user in users:
        try:
            if msg.photo:
                await context.bot.send_photo(
                    chat_id=user.id if isinstance(user, models.User) else user,
                    photo=msg.photo[-1],
                    caption=msg.caption,
                )
            elif msg.video:
                await context.bot.send_video(
                    chat_id=user.id if isinstance(user, models.User) else user,
                    video=msg.video,
                    caption=msg.caption,
                )
            elif msg.audio:
                await context.bot.send_audio(
                    chat_id=user.id if isinstance(user, models.User) else user,
                    audio=msg.audio,
                    caption=msg.caption,
                )
            else:
                await context.bot.send_message(
                    chat_id=user.id if isinstance(user, models.User) else user,
                    text=msg.text,
                )
        except:
            continue


def build_done_button():
    done_button = [
        [
            InlineKeyboardButton(
                text="تم الانتهاء 👍",
                callback_data="done entering users",
            )
        ],
        build_back_button("back_to_send_to"),
        back_to_admin_home_page_button[0],
    ]
    return InlineKeyboardMarkup(done_button)
