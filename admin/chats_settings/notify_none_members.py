from telegram import (
    Chat,
    Update,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
from telegram.constants import ChatMemberStatus
from custom_filters import Admin
import asyncio
import models


async def notify_none_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        asyncio.create_task(send_none_members_new_invite_link(context))
        await update.callback_query.delete_message()
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=(
                "يقوم البوت بإرسال روابط جديدة للمشتركين الذين غادروا وما زال اشتراكهم فعالاً، يمكنك متابعة استخدام البوت بشكل طبيعي\n"
                "اضغط /admin للمتابعة"
            ),
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END


async def send_none_members_new_invite_link(context: ContextTypes.DEFAULT_TYPE):
    subscribers = models.User.get_users(subsicribers=True)
    code_chats = models.CodeChat.get(
        attr="chat_id", val=context.user_data["chat_id"], all=True
    )
    for subscriber in subscribers:
        if subscriber.cur_sub not in [code_chat.code for code_chat in code_chats]:
            continue
        member = await context.bot.get_chat_member(
            chat_id=context.user_data["chat_id"],
            user_id=subscriber.id,
        )

        if member.status == ChatMemberStatus.LEFT:
            link = await context.bot.create_chat_invite_link(
                chat_id=context.user_data["chat_id"],
                member_limit=1,
            )
            await models.InviteLink.add(
                link=link.invite_link,
                code=subscriber.cur_sub,
                user_id=subscriber.id,
                chat_id=context.user_data["chat_id"],
            )
            chat = await context.bot.get_chat(chat_id=context.user_data["chat_id"])
            await context.bot.send_message(
                chat_id=subscriber.id,
                text=f"رصد البوت مغادرتك القناة/المجموعة {chat.title if chat.title else (chat.first_name + chat.last_name)} فقام بإنشاء رابط اشتراك جديد لمرة واحدة، سارع للعودة قبل انتهاء فترة الاشتراك الخاصة بك",
                reply_markup=InlineKeyboardMarkup.from_button(
                    InlineKeyboardButton(
                        text="انضم الآن",
                        url=link.invite_link,
                    )
                ),
                disable_web_page_preview=True,
            )


notify_none_members_handler = CallbackQueryHandler(
    notify_none_members, "^notify_none_members$"
)
