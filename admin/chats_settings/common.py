from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Chat, Update
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
from custom_filters import Admin
from common.back_to_home_page import back_to_admin_home_page_button
from common.common import build_back_button
import models


chats_settings_keyboard = [
    [
        InlineKeyboardButton(
            text="إضافة قناة/مجموعة ➕",
            callback_data="add_chat",
        ),
        InlineKeyboardButton(
            text="حذف قناة/مجموعة ✖️",
            callback_data="delete_chat",
        ),
    ],
    [
        InlineKeyboardButton(
            text="قائمة القنوات/المجموعات 📋",
            callback_data="show_chats",
        )
    ],
    back_to_admin_home_page_button[0],
]


def stringify_chat_info(chat: models.Chat):
    return (
        f"آيدي القناة:\n<code>{chat.chat_id}</code>\n"
        f"اسم القناة: <b>{chat.name}</b>\n"
        f"اليوزر: {chat.username}\n"
    )


async def back_to_chats_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.edit_message_text(
            text="هل تريد:",
            reply_markup=InlineKeyboardMarkup(chats_settings_keyboard),
        )
        if update.callback_query.data.startswith("back"):
            return ConversationHandler.END


def build_chats_keyboard(op: str):
    chats = models.Chat.get()
    back_buttons = [
        build_back_button("back_to_chats_settings"),
        back_to_admin_home_page_button[0],
    ]
    if not chats:
        return back_buttons
    chats_keyboard = [
        [
            InlineKeyboardButton(
                text=chat.name,
                callback_data=f"{op}_ch_{chat.chat_id}",
            )
        ]
        for chat in chats
    ]
    for back_button in back_buttons:
        chats_keyboard.append(back_button)
    return InlineKeyboardMarkup(chats_keyboard)


chats_settings_handler = CallbackQueryHandler(
    back_to_chats_settings, "^chats_settings$"
)
