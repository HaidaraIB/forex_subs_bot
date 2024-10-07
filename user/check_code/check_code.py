from telegram import Update, Chat, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from common.common import build_back_button, build_periods_keyboard
from common.constants import *
from common.back_to_home_page import (
    back_to_user_home_page_handler,
    back_to_user_home_page_button,
)
from jobs import kick_user, remind_user
import re
import models
from start import start_command
from datetime import datetime, timedelta


GET_CODE = 0


async def check_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        jobs = context.job_queue.get_jobs_by_name(name=str(update.effective_user.id))
        if jobs:
            diff = jobs[0].next_t - datetime.now(TIMEZONE)
            seconds = diff.total_seconds()
            days = int(seconds // (3600 * 24))
            if days > 3:
                await update.callback_query.answer(
                    text="لا يمكنك إرسال كود جديد حتى يتبقى لنهاية اشتراكك 3 أيام أو أقل",
                    show_alert=True,
                )
                return ConversationHandler.END

        periods = models.Code.get_by(unique_period=True)
        periods_keyboard = build_periods_keyboard(periods)
        if not periods_keyboard:
            await update.callback_query.answer(
                text="ليس لدينا اشتراكات بعد",
                show_alert=True,
            )
            return

        await update.callback_query.edit_message_text(
            text="أرسل الكود",
            reply_markup=InlineKeyboardMarkup(back_to_user_home_page_button),
        )
        return GET_CODE


async def get_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        back_buttons = [
            build_back_button("back_to_get_code"),
            back_to_user_home_page_button[0],
        ]

        sent_code = re.sub("[^\w\s]", "", update.effective_message.text)
        code = models.Code.get_by(code=sent_code)
        if not code:
            await update.message.reply_text(
                text="كود خاطئ ❗️ الرجاء إعادة المحاولة.",
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
            return
        elif code.user_id:
            await update.message.reply_text(
                text="هذا الكود مستخدم من قبل.",
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
            return

        period = code.period

        sat_sun_text = (
            "نظراً لأن السوق لا يزال مغلقاً فلن يتم إحتساب اليوم من ضمن فترة الإشتراك.\n\n"
            "سيتم حساب مدة الإشتراك بدايةً من يوم الإثنين.\n\n"
            "وعسى الله يوفقكم..🤍"
        )
        after_7_text = (
            "نظراً لأنه لم يتبقى على نهاية اليوم سوى عدة ساعات، فلن يتم إحتساب هذا اليوم من ضمن مدة الإشتراك.\n\n"
            "سيتم حساب مدة الإشتراك بدايةً من الغد\n\n"
            "وعسى الله يوفقكم..🤍\n\n"
        )
        text = (
            "تم تفعيل العضوية بقناة صفقات النخبة الخاصة\n\n"
            f"مدة الاشتراك: <code>{period}</code> أيام\n\n"
            "ملاحظات:\n\n"
            "<b>سيتم تذكيرك قبل 3 أيام من نهاية اشتراكك، مرة كل 12 ساعة.</b>\n\n"
            "<b>لن تستطيع إرسال كود جديد حتى يتبقى على نهاية اشتراكك 3 أيام أو أقل.</b>\n\n"
        )
        now = datetime.now(TIMEZONE).replace(microsecond=0)
        weekday = now.weekday()
        if weekday not in [5, 6] and now.hour < 19:
            starts_at = now
        elif weekday in [5, 6] and now.hour >= 19:
            starts_at = now + timedelta(days=8 - weekday)
            text += after_7_text + "———-\n\n" + sat_sun_text
        elif weekday in [5, 6]:
            starts_at = now + timedelta(days=7 - weekday)
            text += sat_sun_text
        elif now.hour >= 19:
            starts_at = now + timedelta(days=1)
            text += after_7_text
        ends_at = starts_at + timedelta(days=int(period))

        jobs = context.job_queue.get_jobs_by_name(name=str(update.effective_user.id))
        if jobs:
            link = None
            diff = jobs[0].next_t - datetime.now(TIMEZONE)
            seconds = diff.total_seconds()
            days = int(seconds // (3600 * 24))
            if days <= 3:
                remind_jobs = context.job_queue.get_jobs_by_name(
                    name=f"remind {update.effective_user.id}"
                )
                remind_jobs[0].schedule_removal()
                ends_at += diff - timedelta(days=2)
                jobs[0].schedule_removal()
        else:
            link = await context.bot.create_chat_invite_link(
                chat_id=PRIVATE_CHANNEL_ID, member_limit=1
            )
            await models.InviteLink.add(
                link=link.invite_link,
                code=code.code,
                user_id=update.effective_user.id,
            )

        await models.Code.use(
            code=code.code,
            user_id=update.effective_user.id,
            starts_at=starts_at,
            ends_at=ends_at,
        )
        await models.User.add_sub(
            user_id=update.effective_user.id,
            sub=code.code,
        )

        context.job_queue.run_once(
            kick_user,
            when=ends_at + timedelta(days=2),
            user_id=update.effective_user.id,
            chat_id=PRIVATE_CHANNEL_ID,
            name=str(update.effective_user.id),
            data=getattr(link, "invite_link", None),
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
            data=0,
            name=f"remind {update.effective_user.id}",
            job_kwargs={
                "id": f"remind {update.effective_user.id}",
                "misfire_grace_time": None,
                "coalesce": True,
            },
        )
        context.user_data["wanna_reminder"] = True
        if jobs:
            await update.message.reply_text(
                text=text,
                disable_web_page_preview=True,
            )
        else:
            await update.message.reply_text(
                text=text,
                reply_markup=InlineKeyboardMarkup.from_button(
                    InlineKeyboardButton(
                        text="انضم الآن",
                        url=link.invite_link,
                    )
                ),
                disable_web_page_preview=True,
            )
        return ConversationHandler.END


check_code_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            check_code,
            "^enter code$",
        )
    ],
    states={
        GET_CODE: [
            MessageHandler(
                filters=filters.TEXT & ~filters.COMMAND,
                callback=get_code,
            ),
        ],
    },
    fallbacks=[
        start_command,
        back_to_user_home_page_handler,
    ],
)
