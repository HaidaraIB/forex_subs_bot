from telegram import InlineKeyboardButton, InlineKeyboardMarkup, error
from telegram.ext import ContextTypes
from common.constants import STORE_LINK, PRIVATE_CHANNEL_IDS
import models
import asyncio


async def kick_user(context: ContextTypes.DEFAULT_TYPE):
    await models.User.add_sub(user_id=context.user.id, sub=None)
    await context.bot.unban_chat_member(
        chat_id=context.job.chat_id, user_id=context.user.id
    )
    if context.job.data:
        await context.bot.revoke_chat_invite_link(
            chat_id=context.job.chat_id,
            invite_link=context.job.data,
        )


async def remind_user(context: ContextTypes.DEFAULT_TYPE):
    if (
        context.application.user_data[context.user.id].get("wanna_reminder", True)
        and context.job.data < 4
    ):
        await context.bot.send_message(
            chat_id=context.user.id,
            text="تذكير: سينتهي اشتراكك خلال ثلاثة أيام",
            reply_markup=InlineKeyboardMarkup.from_row(
                [
                    InlineKeyboardButton(
                        text="رابط المتجر",
                        url=STORE_LINK,
                    ),
                    InlineKeyboardButton(
                        text="إيقاف التذكير",
                        callback_data="stop_reminder",
                    ),
                ]
            ),
        )
        context.job_queue.run_once(
            remind_user,
            when=12 * 60 * 60,
            user_id=context.user.id,
            name=f"remind {context.user.id}",
            data=context.job.data + 1,
            job_kwargs={
                "id": f"remind {context.user.id}",
                "misfire_grace_time": None,
                "coalesce": True,
            },
        )


async def send_invite_links(context: ContextTypes.DEFAULT_TYPE):
    OLD_CHANNEL_ID = -1002350872608
    NEW_CHANNEL_ID = -1002392883539
    users = models.User.get_users()
    for user in users:
        jobs = context.job_queue.get_jobs_by_name(name=str(user.id))
        if jobs:
            job = jobs[0]
            job.schedule_removal()
            context.job_queue.run_once(
                kick_user,
                when=job.next_t,
                user_id=user.id,
                chat_id=OLD_CHANNEL_ID,
                name=f"{user.id} {OLD_CHANNEL_ID}",
                data=job.data,
                job_kwargs={
                    "id": f"{user.id} {OLD_CHANNEL_ID}",
                    "misfire_grace_time": None,
                    "coalesce": True,
                },
            )
            chat_member = await context.bot.get_chat_member(
                chat_id=NEW_CHANNEL_ID, user_id=user.id
            )
            if chat_member.status in [
                chat_member.MEMBER,
                chat_member.OWNER,
                chat_member.ADMINISTRATOR,
            ]:
                continue

            try:
                link = await context.bot.create_chat_invite_link(
                    chat_id=NEW_CHANNEL_ID, member_limit=1
                )
            except error.RetryAfter as r:
                await asyncio.sleep(r.retry_after)
                link = await context.bot.create_chat_invite_link(
                    chat_id=NEW_CHANNEL_ID, member_limit=1
                )
            context.job_queue.run_once(
                kick_user,
                when=job.next_t,
                user_id=user.id,
                chat_id=NEW_CHANNEL_ID,
                name=f"{user.id} {NEW_CHANNEL_ID}",
                data=link.invite_link,
                job_kwargs={
                    "id": f"{user.id} {NEW_CHANNEL_ID}",
                    "misfire_grace_time": None,
                    "coalesce": True,
                },
            )
            await context.bot.send_message(
                chat_id=user.id,
                text=(
                    "السلام عليكم ورحمة الله وبركاته\n\n"
                    "لجميع المشتركين سوينا لكم قناة ثانية بنفس الاشتراك\n\n"
                    "القناة الثانية رح تكون لصفقات نواف وفريق ايليت\n"
                    "والقناة الأولى رح تستمر على نفس وضعها الحالي\n\n\n"
                    "يعني قناتين بإشتراك واحد‼️\n\n\n"
                    "انضموا للقناة الآن"
                ),
                reply_markup=InlineKeyboardMarkup.from_button(
                    InlineKeyboardButton(
                        text="انضم الآن",
                        url=link.invite_link,
                    )
                ),
                disable_web_page_preview=True,
            )
