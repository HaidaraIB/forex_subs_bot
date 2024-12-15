from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Chat
from telegram.ext import ContextTypes, CallbackQueryHandler

from common.common import build_back_button
from common.back_to_home_page import back_to_admin_home_page_button

from custom_filters import Admin


def build_free_sub_settings_keyboard(free_on: bool):
    keyboard = [
        [
            InlineKeyboardButton(
                text="تصفير التجربة المجانية",
                callback_data="clear free sub",
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{'إيقاف' if free_on else 'تشغيل'} التجربة المجانية {'🔴' if free_on else '🟢'}",
                callback_data="pause free sub",
            )
        ],
    ]
    return keyboard


async def free_sub_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if not context.bot_data.get("free_on", False):
            context.bot_data['free_on'] = True
        keyboard = build_free_sub_settings_keyboard(context.bot_data['free_on'])
        keyboard.append(back_to_admin_home_page_button[0])
        await update.callback_query.edit_message_text(
            text="اختر ماذا تريد أن تفعل",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


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


free_sub_settings_handler = CallbackQueryHandler(
    free_sub_settings,
    "^free sub settings$",
)
