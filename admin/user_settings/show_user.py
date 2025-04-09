from telegram import (
    Update,
    Chat,
    ReplyKeyboardMarkup,
    KeyboardButton,
    KeyboardButtonRequestUsers,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from custom_filters import Admin
import models
from common.back_to_home_page import back_to_admin_home_page_handler
from start import admin_command

USER_ID = 0


async def show_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.answer()
        await update.callback_query.delete_message()
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=(
                "اختر حساب المستخدم بالضغط على الزر أدناه\n\n"
                "يمكنك إلغاء العملية بالضغط على /admin."
            ),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(
                            text="اختيار حساب مستخدم",
                            request_users=KeyboardButtonRequestUsers(
                                request_id=5, user_is_bot=False
                            ),
                        )
                    ]
                ],
                resize_keyboard=True,
            ),
        )
        return USER_ID


async def get_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.effective_message.users_shared:
            user_id = update.effective_message.users_shared.users[0].user_id
        else:
            user_id = int(update.message.text)
        user = models.User.get_users(user_id=user_id)
        if not user:
            await update.message.reply_text(
                text="لم يتم التعرف على المستخدم تحقق من الآيدي وأعد المحاولة",
            )
            return

        keyboard = [
            [
                InlineKeyboardButton(
                    text="إلغاء الاشتراك الحالي ✖️",
                    callback_data=f"cancel_sub_{user_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="إضافة اشتراك جديد ➕",
                    callback_data=f"add_sub_{user_id}",
                ),
            ],
        ]
        await update.message.reply_text(
            text=stringify_user(user), reply_markup=InlineKeyboardMarkup(keyboard)
        )
        await update.message.reply_text(
            text="يمكنك عرض مستخدم آخر أو الإلغاء بالضغط على /admin"
        )


def stringify_user(user: models.User):
    return (
        "معلومات مستخدم 👤\n\n"
        f"الآيدي: <code>{user.id}</code>\n"
        f"اسم المستخدم: {f'@{user.username}' if user.username else '<i>لا يوجد</i>'}\n"
        f"الاسم الكامل: <b>{user.name}</b>\n"
        f"كود الاشتراك الأخير: {f'<code>{user.cur_sub}</code>' if user.cur_sub else '<i>لا يوجد</i>'}"
    )


async def back_to_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        user_id = int(update.callback_query.data.split("_")[-1])
        user = models.User.get_users(user_id=user_id)
        keyboard = [
            [
                InlineKeyboardButton(
                    text="إلغاء الاشتراك الحالي ✖️",
                    callback_data=f"cancel_sub_{user_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="إضافة اشتراك جديد ➕",
                    callback_data=f"add_sub_{user_id}",
                ),
            ],
        ]
        await update.callback_query.edit_message_text(
            text=stringify_user(user),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return ConversationHandler.END


back_to_user_info_handler = CallbackQueryHandler(
    back_to_user_info, "^back_to_user_info$"
)

show_user_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            show_user,
            "^show_user$",
        ),
    ],
    states={
        USER_ID: [
            MessageHandler(
                filters=filters.StatusUpdate.USERS_SHARED,
                callback=get_user_id,
            ),
            MessageHandler(
                filters=filters.Regex("^-?[0-9]+$"),
                callback=get_user_id,
            ),
        ],
    },
    fallbacks=[
        admin_command,
        back_to_admin_home_page_handler,
    ],
)
