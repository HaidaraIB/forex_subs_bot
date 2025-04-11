from telegram import Update, Chat, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
from common.common import build_confirmation_keyboard, build_back_button
from custom_filters import Admin
import models
from common.back_to_home_page import (
    back_to_admin_home_page_handler,
    back_to_admin_home_page_button,
)
from start import admin_command
from admin.user_settings.show_user import back_to_user_info_handler, back_to_user_info

CONFIRM_CANCEL_SUB = range(1)


async def cancel_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        user_id = int(update.callback_query.data.split("_")[-1])
        user = models.User.get_users(user_id=user_id)
        if not user.cur_sub or user.cur_sub == "Free":
            await update.callback_query.answer(
                text=(
                    "الاشتراك الحالي للمستخدم هو التجربة المجانية ❗️"
                    if user.cur_sub == "Free"
                    else "المستخدم ليس من المشتركين ❗️"
                ),
                show_alert=True,
            )
            return
        keyboard = build_confirmation_keyboard(f"cancel_sub_{user_id}")
        keyboard.append(build_back_button(f"back_to_user_info_{user_id}"))
        keyboard.append(back_to_admin_home_page_button[0])
        await update.callback_query.edit_message_text(
            text=(
                update.effective_message.text_html
                + "\n\n"
                + f"هل أنت متأكد من إلغاء اشتراك هذا المستخدم؟"
            ),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return CONFIRM_CANCEL_SUB


async def confirm_cancel_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.callback_query.data.startswith("yes"):
            user_id = int(update.callback_query.data.split("_")[-1])
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
            code_chats = models.CodeChat.get(attr="code", val=user.cur_sub, all=True)
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
                    jobs = context.job_queue.get_jobs_by_name(
                        name=f"{user_id}"
                    )
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

            await update.callback_query.answer(
                text="تم إلغاء الاشتراك بنجاح ✅",
                show_alert=True,
            )

        await back_to_user_info(update=update, context=context)

        return ConversationHandler.END


cancel_sub_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            cancel_sub,
            "^cancel_sub_",
        ),
    ],
    states={
        CONFIRM_CANCEL_SUB: [
            CallbackQueryHandler(
                confirm_cancel_sub,
                "^((yes)|(no))_cancel_sub",
            ),
        ]
    },
    fallbacks=[
        admin_command,
        back_to_admin_home_page_handler,
        back_to_user_info_handler,
    ],
)
