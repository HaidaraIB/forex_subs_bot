from telegram import Update, Chat, BotCommandScopeChat
from telegram.ext import CommandHandler, ContextTypes, Application, ConversationHandler
import models
from custom_filters import Admin
from common.decorators import check_if_user_banned_dec, add_new_user_dec
from common.constants import *
from common.common import (
    build_user_keyboard,
    build_admin_keyboard,
    check_hidden_keyboard,
)
import os


async def inits(app: Application):
    await models.Admin.add_new_admin(admin_id=int(os.getenv("OWNER_ID")))


async def set_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    st_cmd = ("start", "start command")
    commands = [st_cmd]
    if Admin().filter(update):
        commands.append(("admin", "admin command"))
    await context.bot.set_my_commands(
        commands=commands, scope=BotCommandScopeChat(chat_id=update.effective_chat.id)
    )


@add_new_user_dec
@check_if_user_banned_dec
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:

        await set_commands(update, context)

        if context.user_data.get("free_used", None) == None:
            context.user_data["free_used"] = False

        await update.message.reply_text(
            text=context.bot_data.get("start_msg", "أهلا بك...")
        )
        await update.message.reply_text(
            text=HOME_PAGE_TEXT,
            reply_markup=build_user_keyboard(context.user_data["free_used"]),
        )
        return ConversationHandler.END


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await set_commands(update, context)
        await update.message.reply_text(
            text="أهلاً بك...",
            reply_markup=check_hidden_keyboard(context),
        )

        await update.message.reply_text(
            text="تعمل الآن كآدمن 🕹",
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


start_command = CommandHandler(command="start", callback=start)
admin_command = CommandHandler(command="admin", callback=admin)
