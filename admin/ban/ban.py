from telegram import (
    Update,
    Chat,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButtonRequestUsers,
    KeyboardButton,
    ReplyKeyboardRemove,
)

from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from custom_filters import *

import models

from common.common import build_admin_keyboard, build_back_button

from common.back_to_home_page import (
    back_to_admin_home_page_button,
    back_to_admin_home_page_handler,
)

from start import admin_command

(
    USER_ID_TO_BAN_UNBAN,
    BAN_UNBAN_USER,
) = range(2)


async def ban_unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.answer()
        await update.callback_query.delete_message()
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=(
                "اختر حساب المستخدم الذي تريد حظره بالضغط على الزر أدناه\n\n"
                "يمكنك إرسال الid برسالة أيضاً\n\n"
                "أو إلغاء العملية بالضغط على /admin."
            ),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(
                            text="اختيار حساب مستخدم",
                            request_users=KeyboardButtonRequestUsers(
                                request_id=4, user_is_bot=False
                            ),
                        )
                    ]
                ],
                resize_keyboard=True,
            ),
        )
        return USER_ID_TO_BAN_UNBAN


async def user_id_to_ban_unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.effective_message.users_shared:
            user_id = update.effective_message.users_shared.users[0].user_id
        else:
            user_id = int(update.effective_message.text)

        user = models.User.get_user(user_id=user_id)
        if not user:
            await update.message.reply_text(
                text="لم يتم العثور على المستخدم، تأكد من الآيدي ❌",
            )
            return
        if user.is_banned:
            ban_button = [
                InlineKeyboardButton(
                    text="فك الحظر 🔓", callback_data=f"unban {user.id}"
                )
            ]
        else:
            ban_button = [
                InlineKeyboardButton(text="حظر 🔒", callback_data=f"ban {user.id}")
            ]
        keyboard = [
            ban_button,
            build_back_button("back to user id to ban unban"),
            back_to_admin_home_page_button[0],
        ]
        await update.message.reply_text(
            text="تم العثور على المستخدم ✅.",
            reply_markup=ReplyKeyboardRemove(),
        )
        await update.message.reply_text(
            text="هل تريد.",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return BAN_UNBAN_USER


back_to_user_id_to_ban_unban = ban_unban


async def ban_unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await models.User.set_banned(
            user_id=int(update.callback_query.data.split(" ")[-1]),
            banned=True if update.callback_query.data.startswith("ban") else False,
        )

        await update.callback_query.edit_message_text(
            text="تمت العملية بنجاح ✅",
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


ban_unban_user_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            ban_unban,
            "^ban unban$",
        ),
    ],
    states={
        USER_ID_TO_BAN_UNBAN: [
            MessageHandler(
                filters=filters.Regex("^\d+$"),
                callback=user_id_to_ban_unban,
            ),
            MessageHandler(
                filters=filters.StatusUpdate.USERS_SHARED,
                callback=user_id_to_ban_unban,
            ),
        ],
        BAN_UNBAN_USER: [
            CallbackQueryHandler(
                ban_unban_user,
                "^((ban)|(unban)) \d+$",
            ),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(
            back_to_user_id_to_ban_unban,
            "^back to user id to ban unban$",
        ),
        admin_command,
        back_to_admin_home_page_handler,
    ],
)
