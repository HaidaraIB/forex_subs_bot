from telegram import (
    Update,
    Chat,
    ReplyKeyboardMarkup,
    KeyboardButton,
    KeyboardButtonRequestUsers,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
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
from common.back_to_home_page import (
    back_to_admin_home_page_handler,
    back_to_admin_home_page_button,
)
from start import admin_command
from user.check_period import get_period_in_seconds, calc_period
from admin.user_settings.common import build_user_info_keyboard, stringify_user

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

        period = 0
        if user.cur_sub:
            if user.cur_sub == "Free":
                chat_id = context.bot_data["free_sub_chats"][0]
            else:
                chat_id = models.CodeChat.get(attr="code", val=user.cur_sub).chat_id
            seconds = get_period_in_seconds(
                context=context,
                chat_id=chat_id,
                user_id=user_id,
            )
            period = calc_period(seconds)

        keyboard = build_user_info_keyboard(user_id=user_id)
        keyboard.append(back_to_admin_home_page_button[0])
        await update.message.reply_text(
            text="تم العثور على المستخدم ✅",
            reply_markup=ReplyKeyboardRemove(),
        )
        await update.message.reply_text(
            text=stringify_user(user=user, period=period),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return ConversationHandler.END


async def back_to_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        user_id = int(update.callback_query.data.split("_")[-1])
        user = models.User.get_users(user_id=user_id)

        period = 0
        if user.cur_sub:
            if user.cur_sub == "Free":
                chat_id = context.bot_data["free_sub_chats"][0]
            else:
                chat_id = models.CodeChat.get(attr="code", val=user.cur_sub).chat_id
            seconds = get_period_in_seconds(
                context=context,
                chat_id=chat_id,
                user_id=user_id,
            )
            period = calc_period(seconds)

        keyboard = build_user_info_keyboard(user_id=user_id)
        keyboard.append(back_to_admin_home_page_button[0])
        await update.callback_query.edit_message_text(
            text=stringify_user(user=user, period=period),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return ConversationHandler.END


back_to_user_info_handler = CallbackQueryHandler(
    back_to_user_info, "^back_to_user_info"
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
