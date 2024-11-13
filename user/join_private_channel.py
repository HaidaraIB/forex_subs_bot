from telegram import Update
from telegram.ext import ContextTypes, ChatMemberHandler
import models
from common.constants import PRIVATE_CHANNEL_IDS


async def join_private_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if (
        update.chat_member.chat.id not in [PRIVATE_CHANNEL_IDS]
        or not update.chat_member.invite_link
    ):
        return

    link = models.InviteLink.get_by(link=update.chat_member.invite_link.invite_link)

    if not link:
        return

    await models.InviteLink.use(invite_link=update.chat_member.invite_link.invite_link)

    await context.bot.revoke_chat_invite_link(
        chat_id=update.chat_member.chat.id,
        invite_link=update.chat_member.invite_link.invite_link,
    )


join_private_channel_handler = ChatMemberHandler(
    callback=join_private_channel, chat_member_types=ChatMemberHandler.CHAT_MEMBER
)
