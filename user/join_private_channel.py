from telegram import Update, error
from telegram.ext import ContextTypes, ChatMemberHandler
import models


async def join_private_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chats = models.Chat.get()
    if (
        update.chat_member.chat.id not in [chat.chat_id for chat in chats]
        or not update.chat_member.invite_link
    ):
        return

    link = models.InviteLink.get_by(link=update.chat_member.invite_link.invite_link)

    if not link:
        return

    await models.InviteLink.use(invite_link=update.chat_member.invite_link.invite_link)
    try:
        await context.bot.revoke_chat_invite_link(
            chat_id=update.chat_member.chat.id,
            invite_link=update.chat_member.invite_link.invite_link,
        )
    except error.BadRequest:
        pass


join_private_channel_handler = ChatMemberHandler(
    callback=join_private_channel, chat_member_types=ChatMemberHandler.CHAT_MEMBER
)
