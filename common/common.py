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
import os
import uuid

from dotenv import load_dotenv

load_dotenv()

import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


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


def build_user_keyboard(free_used: bool):
    keyboard = [
        [
            InlineKeyboardButton(
                text="إدخال كود الاشتراك",
                callback_data="enter code",
            ),
        ],
        [
            InlineKeyboardButton(
                text="التحقق من مدة الاشتراك",
                callback_data="check_period",
            ),
        ],
    ]
    if not free_used:
        free_sub_button = [
            InlineKeyboardButton(
                text="تجربة مجانية",
                callback_data="try for free",
            ),
        ]
        keyboard.append(free_sub_button)
    return InlineKeyboardMarkup(keyboard)


def build_admin_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="🎛 إعدادات الآدمن ⚙️",
                callback_data="admin settings",
            )
        ],
        [
            InlineKeyboardButton(
                text="إضافة أكواد",
                callback_data="add codes",
            )
        ],
        [
            InlineKeyboardButton(
                text="عرض الأكواد غير المستخدمة",
                callback_data="show NO codes",
            ),
            InlineKeyboardButton(
                text="عرض الأكواد المستخدمة",
                callback_data="show YES codes",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🔒 حظر/فك حظر 🔓",
                callback_data="ban unban",
            )
        ],
        [
            InlineKeyboardButton(
                text="إخفاء/إظهار كيبورد معرفة الآيديات 🪄",
                callback_data="hide ids keyboard",
            )
        ],
        [
            InlineKeyboardButton(
                text="الإحصائيات",
                callback_data="statistics",
            )
        ],
        [
            InlineKeyboardButton(
                text="رسالة جماعية 👥",
                callback_data="broadcast",
            )
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_periods_keyboard(periods):
    periods_keyboard = [
        [
            InlineKeyboardButton(
                text=f"{p} يوم",
                callback_data=f"{p}_period",
            ),
        ]
        for p in periods
    ]
    return periods_keyboard


def build_back_button(data: str):
    return [InlineKeyboardButton(text="الرجوع🔙", callback_data=data)]


def uuid_generator():
    return uuid.uuid4().hex


request_buttons = [
    [
        KeyboardButton(
            text="معرفة id مستخدم 🆔",
            request_users=KeyboardButtonRequestUsers(
                request_id=0,
                user_is_bot=False,
            ),
        ),
        KeyboardButton(
            text="معرفة id قناة 📢",
            request_chat=KeyboardButtonRequestChat(
                request_id=1,
                chat_is_channel=True,
            ),
        ),
    ],
    [
        KeyboardButton(
            text="معرفة id مجموعة 👥",
            request_chat=KeyboardButtonRequestChat(
                request_id=2,
                chat_is_channel=False,
            ),
        ),
        KeyboardButton(
            text="معرفة id بوت 🤖",
            request_users=KeyboardButtonRequestUsers(
                request_id=3,
                user_is_bot=True,
            ),
        ),
    ],
]


def create_folders():
    os.makedirs("data", exist_ok=True)


async def invalid_callback_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == ChatType.PRIVATE:
        await update.callback_query.answer("انتهت صلاحية هذا الزر")
