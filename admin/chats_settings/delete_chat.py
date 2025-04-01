from telegram import Chat, Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler
from admin.chats_settings.common import (
    back_to_chats_settings,
    build_chats_keyboard,
    chats_settings_keyboard,
)
from start import admin_command
from common.back_to_home_page import back_to_admin_home_page_handler
from custom_filters import Admin
import models


CHAT = 0


async def delete_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        data = update.callback_query.data.split("_")
        if data[-1][1:].isnumeric():
            await models.Chat.delete(chat_id=int(data[-1]))
            await update.callback_query.answer(
                text="تمت العملية بنجاح ✅",
                show_alert=True,
            )
        keyboard = build_chats_keyboard("r")

        if not isinstance(keyboard, InlineKeyboardMarkup) and len(keyboard) == 2:
            await update.callback_query.answer(
                text="ليس لديك قنوات/مجموعات ",
                show_alert=True,
            )
            try:
                await update.callback_query.edit_message_text(
                    text="هل تريد:",
                    reply_markup=InlineKeyboardMarkup(chats_settings_keyboard),
                )
            except:
                pass
            return ConversationHandler.END

        await update.callback_query.edit_message_text(
            text="اختر من القائمة أدناه القناة التي تريد إزالتها.",
            reply_markup=keyboard,
        )
        return CHAT


delete_chat_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            callback=delete_chat,
            pattern="^delete_chat$",
        ),
    ],
    states={
        CHAT: [
            CallbackQueryHandler(
                delete_chat,
                "^r_ch",
            ),
        ]
    },
    fallbacks=[
        CallbackQueryHandler(
            callback=back_to_chats_settings,
            pattern="^back_to_chats_settings$",
        ),
        admin_command,
        back_to_admin_home_page_handler,
    ],
)
