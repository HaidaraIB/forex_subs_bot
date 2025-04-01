from telegram import (
    Chat,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
)
from start import start_command, admin_command
from common.common import build_back_button
from common.back_to_home_page import (
    back_to_admin_home_page_button,
    back_to_admin_home_page_handler,
)
from admin.admin_settings.common import back_to_admin_settings
import os
from custom_filters import Admin
import models
from common.constants import *


CHOOSE_ADMIN_ID_TO_REMOVE = 0


async def remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.answer()
        admins = models.Admin.get_admin_ids()
        admin_ids_keyboard = [
            [InlineKeyboardButton(text=str(admin.id), callback_data=str(admin.id))]
            for admin in admins
        ]
        admin_ids_keyboard.append(build_back_button("back_to_admin_settings"))
        admin_ids_keyboard.append(back_to_admin_home_page_button[0])
        await update.callback_query.edit_message_text(
            text="اختر من القائمة أدناه id الآدمن الذي تريد إزالته.",
            reply_markup=InlineKeyboardMarkup(admin_ids_keyboard),
        )
        return CHOOSE_ADMIN_ID_TO_REMOVE


async def choose_admin_id_to_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        admin_id = int(update.callback_query.data)
        if admin_id == int(os.getenv("OWNER_ID")):
            await update.callback_query.answer(
                text="لا يمكنك إزالة مالك البوت من قائمة الآدمنز❗️",
                show_alert=True,
            )
            return

        await models.Admin.remove_admin(admin_id=admin_id)
        await update.callback_query.answer(text="تمت إزالة الآدمن بنجاح✅")
        admins = models.Admin.get_admin_ids()
        admin_ids_keyboard = [
            [InlineKeyboardButton(text=str(admin.id), callback_data=str(admin.id))]
            for admin in admins
        ]
        admin_ids_keyboard.append(build_back_button("back_to_admin_settings"))
        admin_ids_keyboard.append(back_to_admin_home_page_button[0])
        await update.callback_query.edit_message_text(
            text="اختر من القائمة أدناه id الآدمن الذي تريد إزالته.",
            reply_markup=InlineKeyboardMarkup(admin_ids_keyboard),
        )

        return CHOOSE_ADMIN_ID_TO_REMOVE


remove_admin_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            callback=remove_admin,
            pattern="^remove admin$",
        ),
    ],
    states={
        CHOOSE_ADMIN_ID_TO_REMOVE: [
            CallbackQueryHandler(
                choose_admin_id_to_remove,
                "^\d+$",
            ),
        ]
    },
    fallbacks=[
        CallbackQueryHandler(
            callback=back_to_admin_settings,
            pattern="^back_to_admin_settings$",
        ),
        admin_command,
        start_command,
        back_to_admin_home_page_handler,
    ],
)
