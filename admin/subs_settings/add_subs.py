from telegram import Update, Chat, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatMemberStatus
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from common.constants import TIMEZONE
from datetime import datetime, timedelta
from custom_filters import Admin
from admin.subs_settings.subs_settings import subs_settings_handler, subs_settings
from admin.subs_settings.common import build_subs_settings_keyboard
from common.common import build_back_button, build_confirmation_keyboard
from common.back_to_home_page import (
    back_to_admin_home_page_button,
    back_to_admin_home_page_handler,
)
import models
from start import admin_command
import re
from jobs import kick_user, remind_user

USERS, CODES, CONFIRM_ADD = range(3)


async def add_subs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        back_buttons = [
            build_back_button("back_to_subs_settings"),
            back_to_admin_home_page_button[0],
        ]
        await update.callback_query.edit_message_text(
            text="أرسل آيديات المستخدمين سطراً سطراً",
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return USERS


async def get_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        back_buttons = [
            build_back_button("back_to_get_users"),
            back_to_admin_home_page_button[0],
        ]
        if update.message:
            user_ids = list(
                dict.fromkeys(map(int, update.message.text.split("\n"))).keys()
            )
            for user_id in user_ids:
                try:
                    await context.bot.get_chat(chat_id=user_id)
                except:
                    await update.message.reply_text(
                        text=f"لم يتم العثور على المستخدم <code>{user_id}</code>",
                    )
                    return

            context.user_data["user_ids_to_add_subs_for"] = user_ids
            await update.message.reply_text(
                text="أرسل الأكواد سطراً سطراً",
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
        else:
            await update.callback_query.edit_message_text(
                text="أرسل الأكواد سطراً سطراً",
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )

        return CODES


back_to_get_users = add_subs


async def get_codes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        user_ids = context.user_data["user_ids_to_add_subs_for"]
        raw_codes = update.message.text.split("\n")

        if len(user_ids) != len(raw_codes):
            await update.message.reply_text(
                text="عدد الأكواد لا يساوي عدد المستخدمين ❗️",
            )
            return

        codes = []
        for c in raw_codes:
            sent_code = re.sub(r"[^\w\s\-+=/:?,.]", "", c)
            code = models.Code.get_by(code=sent_code)
            if not code or code.user_id:
                await update.message.reply_text(
                    text=(
                        f"الكود <code>{c}</code> غير موجود ❗️"
                        if not code
                        else f"الكود <code>{c}</code> مستخدم من قبل ❗️"
                    )
                )
                return
            codes.append(sent_code)

        context.user_data["code_to_subs_for"] = codes
        keyboard = build_confirmation_keyboard("add_subs")
        keyboard.append(build_back_button("back_to_get_codes"))
        keyboard.append(back_to_admin_home_page_button[0])
        await update.message.reply_text(
            text=(
                "هل أنت متأكد من إضافة الاشتراكات\n"
                + "\n".join([f"<code>{code}</code>" for code in codes])
                + "\n"
                "للمستخدمين\n"
                + "\n".join(
                    [
                        f"<b>{models.User.get_users(user_id=user_id).name}</b>"
                        for user_id in user_ids
                    ]
                )
            ),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return CONFIRM_ADD


back_to_get_codes = get_users


async def confirm_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.callback_query.data.startswith("yes"):
            codes = context.user_data["code_to_subs_for"]
            user_ids = context.user_data["user_ids_to_add_subs_for"]
            for user_id, sent_code in zip(user_ids, codes):
                user = models.User.get_users(user_id=user_id)
                code = models.Code.get_by(code=sent_code)

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
                    f"مدة الاشتراك: <code>{code.period}</code> أيام\n\n"
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
                ends_at = starts_at + timedelta(days=int(code.period))

                code_chats = models.CodeChat.get(attr="code", val=sent_code, all=True)
                for chat in code_chats:
                    jobs = context.job_queue.get_jobs_by_name(
                        name=f"{user_id} {chat.chat_id}"
                    )
                    if not jobs:
                        jobs = context.job_queue.get_jobs_by_name(name=f"{user_id}")
                    if jobs:
                        ends_at += (
                            jobs[0].next_t - datetime.now(TIMEZONE) - timedelta(days=2)
                        )
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

                remind_jobs = context.job_queue.get_jobs_by_name(
                    name=f"remind {user_id}"
                )
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
                if (
                    context.application.user_data[user_id].get("wanna_reminder", None)
                    == None
                ):
                    context.application.user_data[user_id]["wanna_reminder"] = True

                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"تمت إضافة اشتراك ل {f'@{user.username}' if user.username else f'<b>{user.name}</b>'} بنجاح ✅",
                )
            await update.callback_query.answer(
                text="تمت العملية بنجاح ✅",
                show_alert=True,
            )

        await update.callback_query.delete_message()

        keyboard = build_subs_settings_keyboard()
        keyboard.append(back_to_admin_home_page_button[0])
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="إعدادات الاشتراكات",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return ConversationHandler.END


add_subs_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            add_subs,
            "^add_subs$",
        ),
    ],
    states={
        USERS: [
            MessageHandler(
                filters=filters.Regex(r"^-?[0-9]+(?:\n-?[0-9]+)*$"),
                callback=get_users,
            ),
        ],
        CODES: [
            MessageHandler(
                filters=filters.TEXT & ~filters.COMMAND,
                callback=get_codes,
            )
        ],
        CONFIRM_ADD: [
            CallbackQueryHandler(
                confirm_add,
                "^((yes)|(no))_add_subs$",
            ),
        ],
    },
    fallbacks=[
        back_to_admin_home_page_handler,
        admin_command,
        subs_settings_handler,
        CallbackQueryHandler(back_to_get_users, "^back_to_get_users$"),
        CallbackQueryHandler(back_to_get_codes, "^back_to_get_codes$"),
    ],
)
