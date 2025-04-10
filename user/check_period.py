from telegram import Update, Chat, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
import datetime
from common.constants import *
import models


def get_period_in_seconds(
    context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int
):
    seconds = 0
    jobs = context.job_queue.get_jobs_by_name(
        name=f"{user_id} {chat_id}",
    )
    if not jobs:
        jobs = context.job_queue.get_jobs_by_name(name=f"{user_id}")
    if jobs:
        job = jobs[0]
        diff = job.next_t - datetime.datetime.now(TIMEZONE)
        seconds = diff.total_seconds() - (2 * 24 * 60 * 60)
    return seconds


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
        user = models.User.get_users(user_id=update.effective_user.id)
        if user.cur_sub:
            chat = models.CodeChat.get(attr="code", val=user.cur_sub)
            seconds = get_period_in_seconds(
                context=context,
                chat_id=chat.chat_id,
                user_id=update.effective_user.id,
            )
            store_button = InlineKeyboardMarkup.from_button(
                InlineKeyboardButton(
                    text="رابط المتجر",
                    url=context.bot_data.get("store_link", "https://elite-orca.com/"),
                )
            )
            if seconds <= 0:
                await update.callback_query.edit_message_text(
                    f"اشتراكك منتهي، لديك {calc_period(abs(seconds))} مهلة قبل أن يتم إخراجك من القناة ⚠️",
                    reply_markup=store_button,
                )
                return

            await update.callback_query.edit_message_text(
                text=calc_period(seconds),
                reply_markup=store_button,
            )
        else:
            await update.callback_query.answer(
                "ليس لديك اشتراكات ❗️",
                show_alert=True,
            )


check_period_handler = CallbackQueryHandler(check_period, "^check_period$")
