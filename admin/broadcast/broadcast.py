from telegram import Chat, Update, InlineKeyboardButton, InlineKeyboardMarkup, error
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from common.common import build_admin_keyboard, build_back_button
from admin.broadcast.common import broadcast_keyboard, send_to, build_done_button
from common.back_to_home_page import (
    back_to_admin_home_page_handler,
    back_to_admin_home_page_button,
)
from start import start_command, admin_command
import models
import asyncio
from custom_filters import Admin

(
    THE_MESSAGE,
    SEND_TO,
    USERS,
) = range(3)


async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.edit_message_text(
            text="أرسل الرسالة.",
            reply_markup=InlineKeyboardMarkup(back_to_admin_home_page_button),
        )
        return THE_MESSAGE


async def get_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.message:
            context.user_data["the message"] = update.message
            await update.message.reply_text(
                text="هل تريد إرسال الرسالة إلى:",
                reply_markup=InlineKeyboardMarkup(broadcast_keyboard),
            )
        else:
            await update.callback_query.edit_message_text(
                text="هل تريد إرسال الرسالة إلى:",
                reply_markup=InlineKeyboardMarkup(broadcast_keyboard),
            )
        return SEND_TO


back_to_the_message = broadcast_message


async def choose_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.callback_query.data == "all users":
            users = models.User.get_users()

        elif update.callback_query.data == "subsicribers":
            users = models.User.get_users(subsicribers=True)

        elif update.callback_query.data == "none subsicribers":
            users = models.User.get_users(subsicribers=False)

        elif update.callback_query.data == "specific users":
            back_buttons = [
                build_back_button("back to send to"),
                back_to_admin_home_page_button[0],
            ]
            await update.callback_query.edit_message_text(
                text="قم بإرسال آيديات المستخدمين الذين تريد إرسال الرسالة لهم سطراً سطراً.",
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
            return USERS

        asyncio.create_task(send_to(users=users, context=context))

        keyboard = build_admin_keyboard()
        await update.callback_query.edit_message_text(
            text="يقوم البوت بإرسال الرسائل الآن، يمكنك متابعة استخدامه بشكل طبيعي.",
            reply_markup=keyboard,
        )

        return ConversationHandler.END


back_to_send_to = get_message


async def get_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        users = set(map(int, update.message.text.split("\n")))
        asyncio.create_task(send_to(users=users, context=context))
        await update.message.reply_text(
            text="يقوم البوت بإرسال الرسائل الآن، يمكنك متابعة استخدامه بشكل طبيعي.",
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


broadcast_message_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            broadcast_message,
            "^broadcast$",
        )
    ],
    states={
        THE_MESSAGE: [
            MessageHandler(
                filters=(filters.TEXT & ~filters.COMMAND)
                | filters.PHOTO
                | filters.VIDEO
                | filters.AUDIO
                | filters.VOICE
                | filters.CAPTION,
                callback=get_message,
            )
        ],
        SEND_TO: [
            CallbackQueryHandler(
                callback=choose_users,
                pattern="^((all)|(specific)) users$|^(none )?subsicribers$",
            )
        ],
        USERS: [
            MessageHandler(
                filters=filters.Regex(r"^-?[0-9]+(?:\n-?[0-9]+)*$"),
                callback=get_users,
            ),
        ],
    },
    fallbacks=[
        back_to_admin_home_page_handler,
        start_command,
        admin_command,
        CallbackQueryHandler(back_to_the_message, "^back to the message$"),
        CallbackQueryHandler(back_to_send_to, "^back to send to$"),
    ],
)
