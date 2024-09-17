from telegram import Chat, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from common.common import build_admin_keyboard, build_back_button
from admin.broadcast.common import broadcast_keyboard
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
    ENTER_USERS,
) = range(3)


async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.edit_message_text(
            text="أرسل الرسالة.",
            reply_markup=InlineKeyboardMarkup(back_to_admin_home_page_button),
        )
        return THE_MESSAGE


async def the_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        context.user_data["the message"] = update.message.text
        await update.message.reply_text(
            text="هل تريد إرسال الرسالة إلى:",
            reply_markup=InlineKeyboardMarkup(broadcast_keyboard),
        )
        return SEND_TO


back_to_the_message = broadcast_message


async def send_to_(users: list[models.User], context: ContextTypes.DEFAULT_TYPE):
    text = context.user_data["the message"]
    for user in users:
        try:
            await context.bot.send_message(
                chat_id=user.id if isinstance(user, models.User) else user, text=text
            )
        except:
            pass


async def send_to(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.callback_query.data == "all users":
            users = models.User.get_users()

        elif update.callback_query.data == "subsicribers":
            users = models.User.get_users(subsicribers=True)

        elif update.callback_query.data == "none subsicribers":
            users = models.User.get_users(subsicribers=False)

        elif update.callback_query.data == "specific users":
            context.user_data["specific users"] = []
            done_button = [
                [
                    InlineKeyboardButton(
                        text="تم الانتهاء👍", callback_data="done entering users"
                    )
                ],
                build_back_button("back to send to"),
                back_to_admin_home_page_button[0],
            ]
            await update.callback_query.edit_message_text(
                text="قم بإرسال آيديات المستخدمين الذين تريد إرسال الرسالة لهم عند الانتهاء اضغط تم الانتهاء.",
                reply_markup=InlineKeyboardMarkup(done_button),
            )
            return ENTER_USERS

        asyncio.create_task(send_to_(users=users, context=context))

        keyboard = build_admin_keyboard()
        await update.callback_query.edit_message_text(
            text="يقوم البوت بإرسال الرسائل الآن، يمكنك متابعة استخدامه بشكل طبيعي.",
            reply_markup=keyboard,
        )

        return ConversationHandler.END


async def back_to_send_to(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.edit_message_text(
            text="هل تريد إرسال الرسالة إلى:",
            reply_markup=InlineKeyboardMarkup(broadcast_keyboard),
        )
        return SEND_TO


async def enter_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.message.text.isnumeric():
            context.user_data["specific users"].append(int(update.message.text))
        else:
            await update.message.reply_text(text="الرجاء إرسال id.")


async def done_entering_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        keyboard = build_admin_keyboard()
        await update.callback_query.edit_message_text(
            text="يقوم البوت بإرسال الرسائل الآن، يمكنك متابعة استخدامه بشكل طبيعي.",
            reply_markup=keyboard,
        )
        asyncio.create_task(
            send_to_(users=context.user_data["specific users"], context=context)
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
                filters=filters.TEXT & ~filters.COMMAND,
                callback=the_message,
            )
        ],
        SEND_TO: [
            CallbackQueryHandler(
                callback=send_to,
                pattern="^((all)|(specific)) users$|^(none )?subsicribers$",
            )
        ],
        ENTER_USERS: [
            CallbackQueryHandler(
                done_entering_users,
                "^done entering users$",
            ),
            MessageHandler(
                filters=filters.Regex("^\d+$"),
                callback=enter_users,
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
