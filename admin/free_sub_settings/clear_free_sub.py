from telegram import Update, Chat, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from custom_filters import Admin

from admin.free_sub_settings.common import build_clear_free_sub_keyboard
from common.common import build_back_button, build_admin_keyboard
from common.back_to_home_page import (
    back_to_admin_home_page_button,
    back_to_admin_home_page_handler,
)
from common.constants import HOME_PAGE_TEXT

from start import admin_command

CHOOSE_CLEAR_FREE_SUB, USER_IDS = range(2)


async def clear_free_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        keyboard = build_clear_free_sub_keyboard()
        keyboard.append(back_to_admin_home_page_button[0])
        await update.callback_query.edit_message_text(
            text="هل تريد؟",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return CHOOSE_CLEAR_FREE_SUB


async def choose_clear_free_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.callback_query.data.startswith("all_clear"):
            for user_id in context.application.user_data:
                if context.application.user_data[user_id].get("free_used", False):
                    context.application.user_data[user_id]["free_used"] = False
            await update.callback_query.answer(
                text="تم تصفير التجربة المجانية للجميع بنجاح",
                show_alert=True,
            )
            await update.callback_query.edit_message_text(
                text=HOME_PAGE_TEXT,
                reply_markup=build_admin_keyboard(),
            )
            return ConversationHandler.END

        elif update.callback_query.data.startswith("specific_clear"):
            back_buttons = [
                build_back_button("back_to_choose_clear_free_sub"),
                back_to_admin_home_page_button[0],
            ]
            await update.callback_query.edit_message_text(
                text=(
                    "أرسل آيديات المستخدمين الذين تريد تصفير التجربة المجانية لديهم سطراً سطراً كما في المثال:\n\n"
                    "1241414124\n"
                    "1312412512\n"
                    "3241412421\n"
                ),
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
            return USER_IDS


back_to_choose_clear_free_sub = clear_free_sub


async def get_user_ids(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        user_ids = update.message.text.split("\n")
        success_count = 0
        for user_id in user_ids:
            try:
                if context.application.user_data[int(user_id)].get("free_used", False):
                    context.application.user_data[int(user_id)]["free_used"] = False
                    success_count += 1
            except:
                await update.message.reply_text(
                    text=f"حصل خطأ أثناء تصفير التجربة المجانية للمستخدم صاحب الآيدي <code>{user_id}</code>"
                )
        await update.message.reply_text(
            text=f"تم تصفير التجربة المجانية ل{success_count} من أصل {len(user_ids)}",
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


clear_free_sub_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            clear_free_sub,
            "^clear free sub$",
        ),
    ],
    states={
        CHOOSE_CLEAR_FREE_SUB: [
            CallbackQueryHandler(
                choose_clear_free_sub,
                "^((all)|(specific))_clear_free_sub$",
            ),
        ],
        USER_IDS: [
            MessageHandler(
                filters=filters.Regex("(^\d+\n?$)+"),
                callback=get_user_ids,
            )
        ],
    },
    fallbacks=[
        admin_command,
        back_to_admin_home_page_handler,
        CallbackQueryHandler(
            back_to_choose_clear_free_sub, "^back_to_choose_clear_free_sub$"
        ),
    ],
)
