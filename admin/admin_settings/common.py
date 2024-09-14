from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Chat,
    Update,
)
from telegram.ext import ContextTypes, ConversationHandler
from custom_filters import Admin
from common.back_to_home_page import back_to_admin_home_page_button

admin_settings_keyboard = [
    [
        InlineKeyboardButton(text="إضافة آدمن➕", callback_data="add admin"),
        InlineKeyboardButton(text="حذف آدمن✖️", callback_data="remove admin"),
    ],
    [
        InlineKeyboardButton(
            text="عرض آيديات الآدمنز الحاليين🆔", callback_data="show admins"
        )
    ],
    back_to_admin_home_page_button[0],
]


async def back_to_admin_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.edit_message_text(
            text="هل تريد:",
            reply_markup=InlineKeyboardMarkup(admin_settings_keyboard),
        )
        return ConversationHandler.END