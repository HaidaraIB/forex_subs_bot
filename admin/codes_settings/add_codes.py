from telegram import Chat, Update, InlineKeyboardMarkup, InlineKeyboardButton
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
from admin.codes_settings.common import codes_settings_handler

CODES, PERIOD, CHATS, CONFIRM_ADD = range(4)


async def add_codes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        chats = models.Chat.get()
        if not chats:
            await update.callback_query.answer(
                text="ليس لديك قنوات/مجموعات بعد ❗️",
                show_alert=True,
            )
            return
        back_buttons = [
            build_back_button("back_to_codes_settings"),
            back_to_admin_home_page_button[0],
        ]
        await update.callback_query.edit_message_text(
            text="أرسل الأكواد",
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return CODES


async def get_codes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        back_buttons = [
            build_back_button("back_to_get_codes"),
            back_to_admin_home_page_button[0],
        ]
        if update.message:
            raw_codes = set(update.message.text.split("\n"))
            codes = []
            for raw_code in raw_codes:
                code = models.Code.get_by(code=raw_code)
                if not code:
                    codes.append(raw_code)
            context.user_data["codes_to_add"] = codes
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
        if update.message:
            period = update.message.text
            context.user_data["period"] = period
        context.user_data["chats_to_link"] = []
        chats = models.Chat.get()
        keyboard = [
            [
                InlineKeyboardButton(
                    text=f"{chat.name} 🔴", callback_data=f"link_code_{chat.chat_id}"
                )
            ]
            for chat in chats
        ]
        keyboard.append(build_back_button("back_to_get_period"))
        keyboard.append(back_to_admin_home_page_button[0])
        await update.message.reply_text(
            text=("اختر القنوات/الغروبات\n" "عند الانتهاء أرسل <b>تم</b>"),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return CHATS


async def choose_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        chat_id = int(update.callback_query.data.split("_")[-1])
        if chat_id not in context.user_data["chats_to_link"]:
            context.user_data["chats_to_link"].append(chat_id)
        else:
            context.user_data["chats_to_link"].remove(chat_id)
        chats = models.Chat.get()
        keyboard = [
            [
                InlineKeyboardButton(
                    text=f"{chat.name} {'🟢' if chat.chat_id in context.user_data['chats_to_link'] else '🔴'}",
                    callback_data=f"link_code_{chat.chat_id}",
                )
            ]
            for chat in chats
        ]
        keyboard.append(build_back_button("back_to_get_period"))
        keyboard.append(back_to_admin_home_page_button[0])
        await update.callback_query.answer(
            text="تمت العملية بنجاح ✅",
            show_alert=True,
        )
        await update.callback_query.edit_message_text(
            text=("اختر القنوات/الغروبات\n" "عند الانتهاء أرسل <b>تم</b>"),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return CHATS


back_to_get_period = get_codes


async def done_linking_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if not context.user_data["chats_to_link"]:
            await update.message.reply_text(text="لم تقم باختيار أي قناة/مجموعة ❗️")
            return
        back_buttons = [
            build_back_button("back_to_choose_chats"),
            back_to_admin_home_page_button[0],
        ]

        await update.message.reply_text(
            text=(
                "الأكواد:\n\n"
                + "\n".join(context.user_data["codes_to_add"])
                + "\n"
                + f"صلاحيتها: {context.user_data['period']} يوم\n"
                + "القنوات/المجموعات:\n"
                + "\n".join(
                    [
                        models.Chat.get(attr="chat_id", val=ch).name
                        for ch in context.user_data["chats_to_link"]
                    ]
                )
                + "\n\n"
                + "هل أنت متأكد من هذه الإضافة؟\n"
                + "للتأكيد اكتب كلمة <b>تأكيد</b>"
            ),
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return CONFIRM_ADD


back_to_choose_chats = get_period


async def confirm_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        codes = [
            models.Code(
                code=code,
                user_id=0,
                period=context.user_data["period"],
                chats=[
                    models.Chat.get(attr="chat_id", val=chat_id)
                    for chat_id in context.user_data["chats_to_link"]
                ],
            )
            for code in context.user_data["codes_to_add"]
        ]
        await models.Code.add(codes=codes)
        await update.message.reply_text(
            text=f"تمت العملية بنجاح ✅",
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


add_codes_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            callback=add_codes,
            pattern="^add_codes$",
        )
    ],
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
        CHATS: [
            CallbackQueryHandler(
                choose_chats,
                "^link_code",
            ),
            MessageHandler(
                filters=filters.Regex("^تم$"),
                callback=done_linking_chats,
            ),
        ],
        CONFIRM_ADD: [
            MessageHandler(
                filters=filters.Regex("^تأكيد$"),
                callback=confirm_add,
            )
        ],
    },
    fallbacks=[
        codes_settings_handler,
        admin_command,
        back_to_admin_home_page_handler,
        CallbackQueryHandler(back_to_get_codes, "^back_to_get_codes$"),
        CallbackQueryHandler(back_to_get_period, "^back_to_get_period$"),
        CallbackQueryHandler(back_to_choose_chats, "^back_to_choose_chats$"),
    ],
)
