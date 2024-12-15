from telegram import Update, Chat, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

from custom_filters import Admin
from admin.free_sub_settings.common import build_free_sub_settings_keyboard
from common.back_to_home_page import back_to_admin_home_page_button


async def pause_free_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if not context.bot_data.get("free_on", False):
            context.bot_data["free_on"] = True
        context.bot_data["free_on"] = not context.bot_data["free_on"]
        await update.callback_query.answer(
            text=f"تم {'تشغيل' if context.bot_data['free_on'] else 'إيقاف'} التجربة المجانية ✅",
            show_alert=True,
        )
        keyboard = build_free_sub_settings_keyboard(context.bot_data["free_on"])
        keyboard.append(back_to_admin_home_page_button[0])
        await update.callback_query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


pause_free_sub_handler = CallbackQueryHandler(
    pause_free_sub,
    "^pause free sub$",
)
