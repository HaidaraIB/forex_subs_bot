from telegram import (
    Chat,
    Update,
    ReplyKeyboardRemove,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from common.common import (
    build_admin_keyboard,
    request_buttons,
)

from common.back_to_home_page import (
    HOME_PAGE_TEXT
)

from custom_filters import Admin

async def find_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.effective_message.users_shared:
            await update.message.reply_text(
                text=f"🆔: <code>{update.effective_message.users_shared.users[0].user_id}</code>",
            )
        else:
            await update.message.reply_text(
                text=f"🆔: <code>{update.effective_message.chat_shared.chat_id}</code>",
            )

async def hide_ids_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if (
            not context.user_data.get("request_keyboard_hidden", None)
            or not context.user_data["request_keyboard_hidden"]
        ):
            context.user_data["request_keyboard_hidden"] = True
            await update.callback_query.delete_message()
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text="تم الإخفاء ✅",
                reply_markup=ReplyKeyboardRemove(),
            )
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text=HOME_PAGE_TEXT,
                reply_markup=build_admin_keyboard(),
            )
        else:
            context.user_data["request_keyboard_hidden"] = False
            await update.callback_query.delete_message()
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text="تم الإظهار ✅",
                reply_markup=ReplyKeyboardMarkup(request_buttons, resize_keyboard=True),
            )
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text=HOME_PAGE_TEXT,
                reply_markup=build_admin_keyboard(),
            )


hide_ids_keyboard_handler = CallbackQueryHandler(callback=hide_ids_keyboard, pattern="^hide ids keyboard$")

find_id_handler = MessageHandler(
    filters=filters.StatusUpdate.USERS_SHARED | filters.StatusUpdate.CHAT_SHARED,
    callback=find_id,
)