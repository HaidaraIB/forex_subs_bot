from telegram import Chat, Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler,MessageHandler, filters
import models
from custom_filters import Admin
from common.back_to_home_page import back_to_admin_home_page_button, back_to_admin_home_page_handler
from common.common import build_back_button, build_admin_keyboard
from start import admin_command
from admin.codes_settings.common import codes_settings_handler

CODES, CONFIRM_DELETE = range(2)


async def delete_codes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        back_buttons = [
            build_back_button("back_to_codes_settings"),
            back_to_admin_home_page_button[0],
        ]
        await update.callback_query.edit_message_text(
            text="أرسل الأكواد التي تريد حذفها سطراً سطراً",
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )

        return CODES


async def get_codes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        back_buttons = [
            build_back_button("back_to_get_codes"),
            back_to_admin_home_page_button[0],
        ]
        raw_codes = update.message.text.split("\n")
        codes = []
        for c in raw_codes:
            code = models.Code.get_by(code=c)
            if code and not code.user_id:
                codes.append(c)
        context.user_data["codes_to_delete"] = codes
        await update.message.reply_text(
            text=(
                f"تم التعرف على <b>{len(codes)}</b> كود غير مستخدم من أصل <b>{len(raw_codes)}</b> مرسلة\n\n"
                "اكتب <b>تأكيد الحذف</b> ليقوم البوت بحذفها"
            ),
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return CONFIRM_DELETE


back_to_get_codes  = delete_codes

async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await models.Code.delete(codes=context.user_data['codes_to_delete'])
        await update.message.reply_text(
            text=f"تم حذف <b>{len(context.user_data["codes_to_delete"])}</b> كود بنجاح ✅",
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


delete_codes_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            delete_codes,
            "^delete_codes$",
        ),
    ],
    states={
        CODES: [
            MessageHandler(
                filters=filters.TEXT & ~filters.COMMAND,
                callback=get_codes,
            ),
        ],
        CONFIRM_DELETE: [
            MessageHandler(
                filters=filters.Regex("^تأكيد الحذف$"),
                callback=confirm_delete,
            ),
        ],
    },
    fallbacks=[
        codes_settings_handler,
        admin_command,
        back_to_admin_home_page_handler,
        CallbackQueryHandler(back_to_get_codes, '^back_to_get_codes$')
    ]
)
