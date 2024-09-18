from telegram import Update, Chat, error, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler
import asyncio
import models
from jobs import kick_user, remind_user
from datetime import datetime, timedelta
from common.constants import *


async def free_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        if context.user_data.get("free_used", False):
            await update.callback_query.answer(
                text="لقد قمت باستخدام الاشتراك المجاني بالفعل ❗️",
                show_alert=True,
            )
            return

        chat_member = await context.bot.get_chat_member(
            chat_id=PRIVATE_CHANNEL_ID, user_id=update.effective_user.id
        )
        if chat_member.status in [
            chat_member.MEMBER,
            chat_member.OWNER,
            chat_member.ADMINISTRATOR,
        ]:
            await update.callback_query.answer(
                text="أنت مشترك في القناة بالفعل ❗️",
                show_alert=True,
            )
            return

        try:
            link = await context.bot.create_chat_invite_link(
                chat_id=PRIVATE_CHANNEL_ID, member_limit=1
            )
        except error.RetryAfter as r:
            await update.callback_query.answer(
                text=f"نتيجة الضغط الكبير عليك الانتظار {r.retry_after} ثانية ليتم توليد الرابط الخاص بك، شاكرين تفهمكم.",
                show_alert=True,
            )
            await asyncio.sleep(r.retry_after)
            link = await context.bot.create_chat_invite_link(
                chat_id=PRIVATE_CHANNEL_ID, member_limit=1
            )
        await models.InviteLink.add(
            link=link.invite_link,
            code="Free",
            user_id=update.effective_user.id,
        )
        await models.User.add_sub(
            user_id=update.effective_user.id,
            sub="Free",
        )

        now = datetime.now(TIMEZONE).replace(microsecond=0)
        weekday = now.weekday()
        if weekday not in [5, 6] and now.hour < 19:
            starts_at = now
        elif weekday in [5, 6]:
            starts_at = now + timedelta(days=7 - weekday)
        elif now.hour >= 19:
            starts_at = now + timedelta(days=1)
        ends_at = starts_at + timedelta(days=FREE_SUB_PERIOD)

        context.job_queue.run_once(
            kick_user,
            when=ends_at + timedelta(days=2),
            user_id=update.effective_user.id,
            chat_id=PRIVATE_CHANNEL_ID,
            name=str(update.effective_user.id),
            data={
                "invite_link": link.invite_link,
            },
            job_kwargs={
                "id": str(update.effective_user.id),
                "misfire_grace_time": None,
                "coalesce": True,
            },
        )
        context.job_queue.run_once(
            remind_user,
            when=ends_at - timedelta(days=3),
            user_id=update.effective_user.id,
            chat_id=PRIVATE_CHANNEL_ID,
            name=f"remind {update.effective_user.id}",
            data={
                "invite_link": link.invite_link,
            },
            job_kwargs={
                "id": f"remind {update.effective_user.id}",
                "misfire_grace_time": None,
                "coalesce": True,
            },
        )
        await update.callback_query.edit_message_text(
            text=f"اضغط الزر أدناه للانضمام لقناتنا الخاصة",
            reply_markup=InlineKeyboardMarkup.from_button(
                InlineKeyboardButton(
                    text="انضم الآن",
                    url=link.invite_link,
                )
            ),
            disable_web_page_preview=True,
        )
        context.user_data["free_used"] = True


free_sub_handler = CallbackQueryHandler(free_sub, "^try for free$")