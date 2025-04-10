from telegram import (
    Chat,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    ReplyKeyboardMarkup,
    KeyboardButtonRequestChat,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from admin.chats_settings.notify_none_members import notify_none_members_handler
from admin.chats_settings.common import back_to_chats_settings
from custom_filters import Admin
import models
from start import admin_command
from common.constants import *

NEW_CHAT = range(1)


async def add_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.delete_message()
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=(
                "اختر القناة أو المجموعة التي تريد إضافتها بالضغط على الزر أدناه\n\n"
                "يمكنك إلغاء العملية بالضغط على /admin."
            ),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(
                            text="اختيار قناة",
                            request_chat=KeyboardButtonRequestChat(
                                request_id=6, chat_is_channel=True
                            ),
                        ),
                        KeyboardButton(
                            text="اختيار مجموعة",
                            request_chat=KeyboardButtonRequestChat(
                                request_id=7, chat_is_channel=False
                            ),
                        ),
                    ]
                ],
                resize_keyboard=True,
            ),
        )
        return NEW_CHAT


async def new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.message:
            chat_id = update.effective_message.chat_shared.chat_id
        else:
            chat_id = int(update.effective_message.text)

        context.user_data["chat_id"] = chat_id

        notify_none_members_button = InlineKeyboardButton(
            text="إرسال روابط للمشتركين الذين غادروا وما زال اشتراكهم فعالاً",
            callback_data="notify_none_members",
        )
        if models.Chat.get(attr="chat_id", val=chat_id):
            await update.message.reply_text(
                text=(
                    "هذه القناة/المجموعة مضافة بالفعل هل تريد إرسال روابط للمشتركين الذين غادروا وما زال اشتراكهم فعالاً؟\n"
                    "للإلغاء اضغط /admin"
                ),
                reply_markup=InlineKeyboardMarkup.from_button(
                    notify_none_members_button
                ),
            )
            return

        try:
            chat = await context.bot.get_chat(chat_id=chat_id)
        except:
            await update.message.reply_text(
                text="لم يتم العثور على القناة/المجموعة تأكد من الآيدي المرسل أو من أن البوت آدمن فيها"
            )
            return

        await models.Chat.add(
            chat_id=chat_id,
            username=f"@{chat.username}" if chat.username else "لا يوجد",
            name=(
                chat.title
                if chat.title
                else (
                    chat.first_name + chat.last_name
                    if chat.last_name
                    else chat.first_name
                )
            ),
        )
        await update.message.reply_text(
            text="تمت الإضافة بنجاح ✅",
            reply_markup=ReplyKeyboardRemove(),
        )
        await update.message.reply_text(
            text=(
                "هل تريد إرسال روابط للمشتركين الذين غادروا وما زال اشتراكهم فعالاً؟\n"
                "اضغط /admin للإلغاء"
            ),
            reply_markup=InlineKeyboardMarkup.from_button(notify_none_members_button),
        )


add_chat_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            callback=add_chat,
            pattern="^add_chat$",
        ),
    ],
    states={
        NEW_CHAT: [
            MessageHandler(
                filters=filters.StatusUpdate.CHAT_SHARED,
                callback=new_chat,
            ),
            MessageHandler(
                filters=filters.Regex("^-?[0-9]+$"),
                callback=new_chat,
            ),
            notify_none_members_handler,
        ],
    },
    fallbacks=[
        admin_command,
        CallbackQueryHandler(
            callback=back_to_chats_settings,
            pattern="^back_to_chats_settings$",
        ),
    ],
)
