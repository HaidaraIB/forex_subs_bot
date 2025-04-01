from telegram import Chat, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler
from common.common import build_back_button
from common.back_to_home_page import (
    back_to_admin_home_page_button,
    back_to_admin_home_page_handler,
)
from start import admin_command
from admin.chats_settings.common import (
    stringify_chat_info,
    build_chats_keyboard,
    back_to_chats_settings,
)
from admin.chats_settings.notify_none_members import notify_none_members_handler
from custom_filters import Admin
import models

CHAT = range(1)


async def show_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        keyboard = build_chats_keyboard("s")
        if not isinstance(keyboard, InlineKeyboardMarkup) and len(keyboard) == 2:
            await update.callback_query.answer(
                text="ليس لديك قنوات/مجموعات",
                show_alert=True,
            )
            return

        await update.callback_query.edit_message_text(
            text="اختر القناة/المجموعة",
            reply_markup=keyboard,
        )
        return CHAT


async def choose_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        chat_id = update.callback_query.data.split("_")[-1]
        context.user_data["chat_id"] = chat_id
        ch = models.Chat.get(attr="chat_id", val=chat_id)
        keyboard = [
            [
                InlineKeyboardButton(
                    text="إرسال روابط للمشتركين الذين غادروا وما زال اشتراكهم فعالاً",
                    callback_data="notify_none_members",
                ),
            ],
            build_back_button("back_to_choose_chat"),
            back_to_admin_home_page_button[0],
        ]
        await update.callback_query.edit_message_text(
            text=stringify_chat_info(ch),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


back_to_choose_chat = show_chats

show_chats_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            callback=show_chats,
            pattern="^show_chats$",
        )
    ],
    states={
        CHAT: [
            CallbackQueryHandler(
                choose_chat,
                "^s_ch",
            ),
            notify_none_members_handler,
        ],
    },
    fallbacks=[
        CallbackQueryHandler(
            callback=back_to_chats_settings, pattern="^back_to_chats_settings$"
        ),
        CallbackQueryHandler(
            callback=back_to_choose_chat, pattern="^back_to_choose_chat$"
        ),
        back_to_admin_home_page_handler,
        admin_command,
    ],
)
