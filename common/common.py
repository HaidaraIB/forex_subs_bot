from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    KeyboardButtonRequestChat,
    KeyboardButtonRequestUsers,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import ContextTypes
from telegram.constants import ChatType
from telegram.error import TimedOut, NetworkError
import os
import uuid
import traceback
import json

from dotenv import load_dotenv

load_dotenv()

import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
if int(os.getenv("OWNER_ID")) != 755501092:
    logging.getLogger("httpx").setLevel(logging.WARNING)


def check_hidden_keyboard(context: ContextTypes.DEFAULT_TYPE):
    if (
        not context.user_data.get("request_keyboard_hidden", None)
        or not context.user_data["request_keyboard_hidden"]
    ):
        context.user_data["request_keyboard_hidden"] = False

        reply_markup = ReplyKeyboardMarkup(request_buttons, resize_keyboard=True)
    else:
        reply_markup = ReplyKeyboardRemove()
    return reply_markup


def build_user_keyboard():
    keyboard = []
    return InlineKeyboardMarkup(keyboard)


def build_admin_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="إعدادات الآدمن⚙️🎛",
                callback_data="admin settings",
            )
        ],
        [
            InlineKeyboardButton(
                text="حظر/فك حظر 🔓🔒",
                callback_data="ban unban",
            )
        ],
        [
            InlineKeyboardButton(
                text="إخفاء/إظهار كيبورد معرفة الآيديات🪄",
                callback_data="hide ids keyboard",
            )
        ],
        [
            InlineKeyboardButton(
                text="رسالة جماعية👥",
                callback_data="broadcast",
            )
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_back_button(data: str):
    return [InlineKeyboardButton(text="الرجوع🔙", callback_data=data)]


def uuid_generator():
    return uuid.uuid4().hex


request_buttons = [
    [
        KeyboardButton(
            text="معرفة id مستخدم🆔",
            request_users=KeyboardButtonRequestUsers(request_id=0, user_is_bot=False),
        ),
        KeyboardButton(
            text="معرفة id قناة📢",
            request_chat=KeyboardButtonRequestChat(request_id=1, chat_is_channel=True),
        ),
    ],
    [
        KeyboardButton(
            text="معرفة id مجموعة👥",
            request_chat=KeyboardButtonRequestChat(request_id=2, chat_is_channel=False),
        ),
        KeyboardButton(
            text="معرفة id بوت🤖",
            request_users=KeyboardButtonRequestUsers(request_id=3, user_is_bot=True),
        ),
    ],
]


def create_folders():
    os.makedirs("data", exist_ok=True)


async def invalid_callback_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == ChatType.PRIVATE:
        await update.callback_query.answer("انتهت صلاحية هذا الزر")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    if isinstance(context.error, (TimedOut, NetworkError)):
        return
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    try:
        error = f"""update = {json.dumps(update_str, indent=2, ensure_ascii=False)} 
        
user_data = {str(context.user_data)}
chat_data = {str(context.chat_data)}

{''.join(traceback.format_exception(None, context.error, context.error.__traceback__))}

{'-'*100}


    """

        with open("errors.txt", "a", encoding="utf-8") as f:
            f.write(error)
    except TypeError:
        error = f"""update = TypeError
        
user_data = {str(context.user_data)}
chat_data = {str(context.chat_data)}

{''.join(traceback.format_exception(None, context.error, context.error.__traceback__))}

{'-'*100}


    """

        with open("errors.txt", "a", encoding="utf-8") as f:
            f.write(error)
