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
from telegram.ext import ContextTypes, Job
from telegram.constants import ChatType
import os
import uuid
from common.constants import *
from datetime import datetime, timedelta

from dotenv import load_dotenv

load_dotenv()

import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


def reschedule_kick_user(job: Job):
    ends_at = 0
    diff = job.next_t - datetime.now(TIMEZONE)
    seconds = diff.total_seconds()
    days = int(seconds // (3600 * 24))
    if days <= 3:
        ends_at = diff - timedelta(days=2)
        job.schedule_removal()

    return ends_at


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
            ),
        ],
        [
            InlineKeyboardButton(
                text="📢 إعدادات القنوات ⚙️",
                callback_data="chats_settings",
            ),
        ],
        [
            InlineKeyboardButton(
                text="إعدادات التجربة المجانية 🆓",
                callback_data="free_sub_settings",
            ),
        ],
        [
            InlineKeyboardButton(
                text="إعدادات الأكواد 🔡",
                callback_data="codes_settings",
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
                text="الإحصائيات 📊",
                callback_data="statistics",
            )
        ],
        [
            InlineKeyboardButton(
                text="رسالة جماعية 👥",
                callback_data="broadcast",
            ),
            InlineKeyboardButton(
                text="عرض معلومات مستخدم 👤",
                callback_data="show_user",
            ),
        ],
        [
            InlineKeyboardButton(
                text="إعدادات عامة 🌐",
                callback_data="general_settings",
            ),
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


def build_confirmation_keyboard(data:str):
    return [
        [
            InlineKeyboardButton(
                text="نعم 👍",
                callback_data=f"yes_{data}",
            ),
            InlineKeyboardButton(
                text="لا 👎",
                callback_data=f"no_{data}",
            ),
        ],
    ]

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
