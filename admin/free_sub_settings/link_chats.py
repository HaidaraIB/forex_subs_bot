from telegram import Update, Chat, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler
from custom_filters import Admin
from common.common import build_back_button
from common.back_to_home_page import back_to_admin_home_page_button
import models


async def link_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if context.bot_data.get("free_sub_chats", None) == None:
            context.bot_data["free_sub_chats"] = []

        if update.callback_query.data.startswith("free_sub_link"):
            chat_id = int(update.callback_query.data.split("_")[-1])
            if chat_id in context.bot_data['free_sub_chats']:
                context.bot_data["free_sub_chats"].remove(chat_id)
                text="تمت إزالة القناة/المجموعة بنجاح ✅"
            else:
                context.bot_data["free_sub_chats"].append(chat_id)
                text="تمت إضافة القناة/المجموعة بنجاح ✅"
            await update.callback_query.answer(
                text=text,
                show_alert=True,
            )
        chats = models.Chat.get()
        chats_keyboard = [
            [
                InlineKeyboardButton(
                    text=f"{chat.name} {'🟢' if chat.chat_id in context.bot_data['free_sub_chats'] else '🔴'}",
                    callback_data=f"free_sub_link_{chat.chat_id}",
                ),
            ]
            for chat in chats
        ]
        chats_keyboard.append(build_back_button("back_to_free_sub_settings"))
        chats_keyboard.append(back_to_admin_home_page_button[0])
        await update.callback_query.edit_message_text(
            text="اختر القنوات/المجموعات 📢",
            reply_markup=InlineKeyboardMarkup(chats_keyboard),
        )


link_chats_handler = CallbackQueryHandler(
    link_chats,
    "^link_chats$|^free_sub_link_",
)
