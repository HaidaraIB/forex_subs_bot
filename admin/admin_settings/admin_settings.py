from telegram import (
    Chat,
    Update,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
)

from common.common import build_admin_keyboard
from admin.admin_settings.common import admin_settings_keyboard
import os
from custom_filters import Admin
import models


async def admin_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.edit_message_text(
            text="إعدادات الآدمن🪄",
            reply_markup=InlineKeyboardMarkup(admin_settings_keyboard),
        )


async def show_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admins = models.Admin.get_admin_ids()
    text = "آيديات الآدمنز الحاليين:\n\n"
    for admin in admins:
        if admin.id == int(os.getenv("OWNER_ID")):
            text += "<code>" + str(admin.id) + "</code>" + " <b>مالك البوت</b>\n"
            continue
        text += "<code>" + str(admin.id) + "</code>" + "\n"
    text += "\nاختر ماذا تريد أن تفعل:"
    await update.callback_query.edit_message_text(
        text=text,
        reply_markup=build_admin_keyboard(),
    )


admin_settings_handler = CallbackQueryHandler(
    admin_settings,
    "^admin settings$",
)

show_admins_handler = CallbackQueryHandler(
    callback=show_admins,
    pattern="^show admins$",
)
