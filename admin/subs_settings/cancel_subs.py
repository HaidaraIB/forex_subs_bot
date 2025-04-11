from telegram import Update, Chat, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
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

USERS, CONFIRM_CANCEL = range(2)


async def cancel_subs(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        if update.message:
            user_ids = set(map(int, update.message.text.split("\n")))
            context.user_data["user_ids_to_cancel_subs_for"] = user_ids
        else:
            user_ids = context.user_data["user_ids_to_cancel_subs_for"]

        user_names = []
        for user_id in user_ids:
            user = models.User.get_users(user_id=user_id)
            if user:
                if not user.cur_sub or user.cur_sub == "Free":
                    continue
                user_names.append(
                    f"@{user.username}" if user.username else f"<b>{user.name}</b>"
                )

        text = "هل أنت متأكد من أنك تريد إلغاء الاشتراكات للمستخدمين\n" + "\n".join(
            user_names
        )
        keyboard = build_confirmation_keyboard(f"cancel_subs")
        keyboard.append(build_back_button(f"back_to_get_users"))
        keyboard.append(back_to_admin_home_page_button[0])

        if update.message:
            await update.message.reply_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        else:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        return CONFIRM_CANCEL


back_to_get_users = cancel_subs


async def confirm_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.callback_query.data.startswith("yes"):
            for user_id in context.user_data["user_ids_to_cancel_subs_for"]:
                user = models.User.get_users(user_id=user_id)

                # clearing user's current subsicription
                await models.User.add_sub(user_id=user_id, sub=None)

                # remove remind_user job
                remind_jobs = context.job_queue.get_jobs_by_name(
                    name=f"remind {user_id}"
                )
                if remind_jobs:
                    remind_jobs[0].schedule_removal()

                # kicking the user from the chats associated with the code
                code_chats = models.CodeChat.get(
                    attr="code", val=user.cur_sub, all=True
                )
                for code_chat in code_chats:
                    await context.bot.unban_chat_member(
                        chat_id=code_chat.chat_id,
                        user_id=user_id,
                    )
                    # remove the kick_user job of this chat
                    jobs = context.job_queue.get_jobs_by_name(
                        name=f"{user_id} {code_chat.chat_id}"
                    )
                    if not jobs:
                        jobs = context.job_queue.get_jobs_by_name(name=f"{user_id}")
                    if jobs:
                        jobs[0].schedule_removal()

                # revoking the chats' invite links associated with the code
                invite_links = models.InviteLink.get_by(code=code_chat.code)
                if invite_links:
                    for invite_link in invite_links:
                        await context.bot.revoke_chat_invite_link(
                            chat_id=invite_link.chat_id,
                            invite_link=invite_link.link,
                        )

                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"تم إلغاء اشتراك {f'@{user.username}' if user.username else f'<b>{user.name}</b>'} بنجاح ✅",
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

        return ConversationHandler.END


cancel_subs_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            cancel_subs,
            "^cancel_subs$",
        ),
    ],
    states={
        USERS: [
            MessageHandler(
                filters=filters.Regex(r"^-?[0-9]+(?:\n-?[0-9]+)*$"),
                callback=get_users,
            ),
        ],
        CONFIRM_CANCEL: [
            CallbackQueryHandler(
                confirm_cancel,
                "^((yes)|(no))_cancel_subs$",
            ),
        ],
    },
    fallbacks=[
        admin_command,
        back_to_admin_home_page_handler,
        subs_settings_handler,
        CallbackQueryHandler(back_to_get_users, "^back_to_get_users$"),
    ],
)
