from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from common.constants import STORE_LINK
import models


async def kick_user(context: ContextTypes.DEFAULT_TYPE):
    await models.User.add_sub(user_id=context.job.user_id, sub=None)
    await context.bot.unban_chat_member(
        chat_id=context.job.chat_id, user_id=context.job.user_id
    )


async def remind_user(context: ContextTypes.DEFAULT_TYPE):
    if context.application.user_data[context.job.user_id].get("wanna_reminder", True):
        await context.bot.send_message(
            chat_id=context.job.user_id,
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
            user_id=context.job.user_id,
            chat_id=context.job.chat_id,
            name=f"remind {context.job.user_id}",
            data=context.job.data,
            job_kwargs={
                "id": f"remind {context.job.user_id}",
                "misfire_grace_time": None,
                "coalesce": True,
            },
        )
