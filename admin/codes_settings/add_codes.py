from telegram import Chat, Update, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from common.common import build_admin_keyboard, build_back_button
from common.back_to_home_page import (
    back_to_admin_home_page_button,
    back_to_admin_home_page_handler,
)
from custom_filters.Admin import Admin
import models
from common.constants import *
from start import admin_command

CODES, PERIOD, CONFIRM_ADD = range(3)


async def add_codes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.edit_message_text(
            text="أرسل الأكواد",
            reply_markup=InlineKeyboardMarkup(back_to_admin_home_page_button),
        )
        return CODES


async def get_codes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        back_buttons = [
            build_back_button("back_to_get_codes"),
            back_to_admin_home_page_button[0],
        ]
        if update.message:
            context.user_data["codes_to_add"] = update.message.text.split("\n")
            await update.message.reply_text(
                text="أرسل صلاحية هذه الأكواد باليوم",
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
        else:
            await update.callback_query.edit_message_text(
                text="أرسل صلاحية هذه الأكواد باليوم",
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )

        return PERIOD


back_to_get_codes = add_codes


async def get_period(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        back_buttons = [
            build_back_button("back_to_get_period"),
            back_to_admin_home_page_button[0],
        ]
        if update.message:
            period = int(update.message.text)
            context.user_data["codes_period_to_add"] = period
        else:
            period = context.user_data["codes_period_to_add"]

        await update.message.reply_text(
            text=(
                "الأكواد:\n\n"
                + "\n".join(context.user_data["codes_to_add"])
                + "\n"
                + f"صلاحيتها: {period} يوم\n\n"
                + "هل أنت متأكد من هذه الإضافة؟\n\n"
                + "للتأكيد اكتب كلمة <b>تأكيد</b>"
            ),
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return CONFIRM_ADD


back_to_get_period = get_codes


async def confirm_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        added_codes_count = 0
        duplicate_codes = []
        if update.message.text == "تأكيد":
            codes = context.user_data["codes_to_add"]
            for code in codes:
                c = f"<code>{code}</code>\n"
                res = await models.Code.add(
                    code=code,
                    user_id=0,
                    period=context.user_data["codes_period_to_add"],
                )
                # when the code is not unique
                if not res:
                    duplicate_codes.append(c)
                    continue
                added_codes_count += 1
            await update.message.reply_text(
                text=(
                    f"تمت إضافة {added_codes_count} كود بنجاح\n\n"
                    + (
                        f"تم العثور على {len(duplicate_codes)} كود مكرر لم تتم إضافته:\n\n"
                        + "\n".join(duplicate_codes)
                        if len(duplicate_codes) > 0
                        else ""
                    )
                ),
            )
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=HOME_PAGE_TEXT,
                reply_markup=build_admin_keyboard(),
            )
            return ConversationHandler.END


add_codes_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=add_codes, pattern="^add codes$")],
    states={
        CODES: [
            MessageHandler(
                filters=filters.TEXT & ~filters.COMMAND,
                callback=get_codes,
            )
        ],
        PERIOD: [
            MessageHandler(
                filters=filters.Regex("^\d+$"),
                callback=get_period,
            )
        ],
        CONFIRM_ADD: [
            MessageHandler(
                filters=filters.Regex("^تأكيد$"),
                callback=confirm_add,
            )
        ],
    },
    fallbacks=[
        admin_command,
        back_to_admin_home_page_handler,
        CallbackQueryHandler(back_to_get_codes, "back_to_get_codes"),
        CallbackQueryHandler(back_to_get_period, "back_to_get_period"),
    ],
)
