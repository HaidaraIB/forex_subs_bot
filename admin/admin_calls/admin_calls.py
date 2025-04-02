from telegram import (
    Chat,
    Update,
    ReplyKeyboardRemove,
    ReplyKeyboardMarkup,
    KeyboardButton,
    KeyboardButtonRequestUsers,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)
from common.common import build_admin_keyboard, request_buttons, build_back_button
from common.back_to_home_page import (
    HOME_PAGE_TEXT,
    back_to_admin_home_page_button,
    back_to_admin_home_page_handler,
)
from custom_filters import Admin
import models
from start import admin_command


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
        await update.message.reply_text(text=stringify_user(user))
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


GENERAL_OPTION, NEW_GENERAL_VAL = range(2)


async def general_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        general_settings_keyboard = [
            [
                InlineKeyboardButton(
                    text="تغيير الرسالة الترحيبية 👋🏻",
                    callback_data="start_msg",
                ),
            ],
            back_to_admin_home_page_button[0],
        ]
        await update.callback_query.edit_message_text(
            text="اختر أحد الخيارات",
            reply_markup=InlineKeyboardMarkup(general_settings_keyboard),
        )
        return GENERAL_OPTION


async def choose_general_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        back_buttons = [
            build_back_button("back_to_choose_general_option"),
            back_to_admin_home_page_button[0],
        ]
        general_option = update.callback_query.data
        context.user_data["general_option"] = general_option
        await update.callback_query.edit_message_text(
            text=(
                "أرسل القيمة الجديدة\n"
                f"القيمة الحالية: {context.bot_data.get(general_option, "")}"
            ),
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return NEW_GENERAL_VAL


back_to_choose_general_option = general_settings


async def get_new_general_val(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        general_option = context.user_data["general_option"]
        context.bot_data[general_option] = update.message.text
        await update.message.reply_text(
            text="تمت العملية بنجاح ✅",
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


general_settings_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            general_settings,
            "^general_settings$",
        ),
    ],
    states={
        GENERAL_OPTION: [
            CallbackQueryHandler(choose_general_option, "^start_msg$"),
        ],
        NEW_GENERAL_VAL: [
            MessageHandler(
                filters=filters.TEXT & ~filters.COMMAND,
                callback=get_new_general_val,
            ),
        ],
    },
    fallbacks=[
        admin_command,
        back_to_admin_home_page_handler,
        CallbackQueryHandler(
            back_to_choose_general_option, "^back_to_choose_general_option$"
        ),
    ],
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

hide_ids_keyboard_handler = CallbackQueryHandler(
    callback=hide_ids_keyboard, pattern="^hide ids keyboard$"
)

find_id_handler = MessageHandler(
    filters=filters.StatusUpdate.USERS_SHARED | filters.StatusUpdate.CHAT_SHARED,
    callback=find_id,
)
