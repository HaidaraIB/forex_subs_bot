from telegram import Update, Chat, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler
import models
from custom_filters import Admin
from common.back_to_home_page import back_to_admin_home_page_button


async def codes_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        keyboard = [
            [
                InlineKeyboardButton(
                    text="إضافة أكواد ➕",
                    callback_data="add_codes",
                ),
                InlineKeyboardButton(
                    text="حذف أكواد ✖️",
                    callback_data="delete_codes",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="عرض الأكواد غير المستخدمة",
                    callback_data="show_NO_codes",
                ),
                InlineKeyboardButton(
                    text="عرض الأكواد المستخدمة",
                    callback_data="show_YES_codes",
                ),
            ],
            back_to_admin_home_page_button[0],
        ]
        await update.callback_query.edit_message_text(
            text="إعدادات الأكواد",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return ConversationHandler.END


codes_settings_handler = CallbackQueryHandler(
    codes_settings, "^codes_settings$|^back_to_codes_settings$"
)
