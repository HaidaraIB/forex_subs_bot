from telegram import (
    Update,
    Chat,
    ReplyKeyboardMarkup,
    KeyboardButton,
    KeyboardButtonRequestUsers,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.constants import ChatMemberStatus
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from custom_filters import Admin
import models
from common.back_to_home_page import (
    back_to_admin_home_page_handler,
    back_to_admin_home_page_button,
)
from start import admin_command
from common.common import build_back_button
from common.constants import TIMEZONE
import re
from datetime import datetime, timedelta
from jobs import kick_user, remind_user
from admin.user_settings.show_user import back_to_user_info_handler

CODE = range(1)


async def add_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if not update.callback_query.data.startswith("back"):
            user_id = int(update.callback_query.data.split("_")[-1])

        back_buttons = [
            build_back_button(f"back_to_user_info_{user_id}"),
            back_to_admin_home_page_button[0],
        ]
        await update.callback_query.edit_message_text(
            text=(
                update.effective_message.text_html
                + "\n\n"
                + "قم بالرد على هذه الرسالة بكود الاشتراك"
            ),
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return CODE


async def get_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        user_id = update.message.reply_to_message.reply_markup.inline_keyboard[0][
            0
        ].callback_data.split("_")[-1]
        sent_code = re.sub(r"[^\w\s\-+=/:?,.]", "", update.effective_message.text)
        code = models.Code.get_by(code=sent_code)

        back_buttons = [
            build_back_button(f"back_to_user_info_{user_id}"),
            back_to_admin_home_page_button[0],
        ]
        if not code:
            await update.message.reply_text(
                text="كود خاطئ الرجاء إعادة المحاولة ❗️",
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
            return
        elif code.user_id:
            await update.message.reply_text(
                text="هذا الكود مستخدم من قبل ❗️",
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
            "تم {} العضوية بقناة صفقات النخبة الخاصة: <code>{}</code>\n\n"
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

        code_chats = models.CodeChat.get(attr="code", val=sent_code, all=True)
        for chat in code_chats:
            jobs = context.job_queue.get_jobs_by_name(name=f"{user_id} {chat.chat_id}")
            if not jobs:
                jobs = context.job_queue.get_jobs_by_name(name=f"{user_id}")
            if jobs:
                ends_at += jobs[0].next_t - datetime.now(TIMEZONE) - timedelta(days=2)
                jobs[0].schedule_removal()

            member = await context.bot.get_chat_member(
                chat_id=chat.chat_id,
                user_id=user_id,
            )

            if member.status == ChatMemberStatus.LEFT:
                link = await context.bot.create_chat_invite_link(
                    chat_id=chat.chat_id,
                    member_limit=1,
                )
                await models.InviteLink.add(
                    link=link.invite_link,
                    code=code.code,
                    user_id=user_id,
                    chat_id=chat.chat_id,
                )
            else:
                link = None

            context.job_queue.run_once(
                kick_user,
                when=ends_at + timedelta(days=2),
                user_id=user_id,
                chat_id=chat.chat_id,
                name=f"{user_id} {chat.chat_id}",
                data=getattr(link, "invite_link", None),
                job_kwargs={
                    "id": f"{user_id} {chat.chat_id}",
                    "misfire_grace_time": None,
                    "coalesce": True,
                },
            )
            chat = await context.bot.get_chat(chat_id=chat.chat_id)
            if link:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=text.format("تفعيل", chat.title),
                    reply_markup=InlineKeyboardMarkup.from_button(
                        InlineKeyboardButton(
                            text="انضم الآن",
                            url=link.invite_link,
                        )
                    ),
                    disable_web_page_preview=True,
                )
            else:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=text.format("تجديد", chat.title),
                    disable_web_page_preview=True,
                )

        await models.Code.use(
            code=code.code,
            user_id=user_id,
            starts_at=starts_at,
            ends_at=ends_at,
        )
        await models.User.add_sub(
            user_id=user_id,
            sub=code.code,
        )

        remind_jobs = context.job_queue.get_jobs_by_name(name=f"remind {user_id}")
        if remind_jobs:
            remind_jobs[0].schedule_removal()
        context.job_queue.run_once(
            remind_user,
            when=ends_at - timedelta(days=3),
            user_id=user_id,
            data=0,
            name=f"remind {user_id}",
            job_kwargs={
                "id": f"remind {user_id}",
                "misfire_grace_time": None,
                "coalesce": True,
            },
        )
        if context.application.user_data[user_id].get("wanna_reminder", None) == None:
            context.application.user_data[user_id]["wanna_reminder"] = True

        await update.message.reply_text(
            text=("تمت إضافة الاشتراك بنجاح ✅\n\n" "اضغط /admin للمتابعة")
        )
        return ConversationHandler.END


add_sub_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            add_sub,
            "^add_sub_",
        ),
    ],
    states={
        CODE: [
            MessageHandler(
                filters=filters.REPLY & filters.TEXT & ~filters.COMMAND,
                callback=get_code,
            ),
        ],
    },
    fallbacks=[
        back_to_admin_home_page_handler,
        admin_command,
        back_to_user_info_handler,
    ],
)
