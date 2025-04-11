from telegram import Update, Chat, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler
from custom_filters import Admin
from admin.subs_settings.common import build_subs_settings_keyboard
from common.back_to_home_page import back_to_admin_home_page_button


async def subs_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        keyboard = build_subs_settings_keyboard()
        keyboard.append(back_to_admin_home_page_button[0])
        await update.callback_query.edit_message_text(
            text="إعدادات الاشتراكات",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return ConversationHandler.END


subs_settings_handler = CallbackQueryHandler(
    subs_settings, "^(back_to_)?subs_settings$"
)
