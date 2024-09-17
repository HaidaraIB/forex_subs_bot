from telegram import Update, Chat
from telegram.ext import ContextTypes, CallbackQueryHandler
import datetime
from common.constants import *
import models

def calc_period(seconds: int):
    days = int(seconds // (3600 * 24))
    hours = int((seconds % (3600 * 24)) // 3600)
    left_minutes = (seconds % 3600) // 60
    left_seconds = seconds - (days * (3600 * 24)) - (hours * 3600) - (left_minutes * 60)

    days_text = f"{days} يوم " if days else ""
    hours_text = f"{hours} ساعة " if hours else ""
    minutes_text = f"{int(left_minutes)} دقيقة " if left_minutes else ""
    seconds_text = f"{int(left_seconds)} ثانية" if left_seconds else ""

    return days_text + hours_text + minutes_text + seconds_text


async def check_period(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        jobs = context.job_queue.get_jobs_by_name(name=str(update.effective_user.id))
        if jobs:
            job = jobs[0]
            diff = job.next_t - datetime.datetime.now(TIMEZONE)
            seconds = diff.total_seconds() - (2 * 24 * 60 * 60)
            user = models.User.get_users(user_id=update.effective_user.id)
            if seconds <= 0:
                await update.callback_query.answer(
                    f"اشتراكك منتهي، لديك {calc_period(abs(seconds))} مهلة قبل أن يتم إخراجك من القناة",
                    show_alert=True,
                )

            await update.callback_query.answer(
                text=calc_period(seconds),
                show_alert=True,
            )
        else:
            await update.callback_query.answer(
                "ليس لديك اشتراكات!",
                show_alert=True,
            )


check_period_handler = CallbackQueryHandler(check_period, "^check_period$")
