from telegram import Update, Chat, InlineKeyboardMarkup, InputMediaDocument
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
import pandas as pd
import sqlite3 as sqlite
import models
from custom_filters import Admin
from admin.statistics.common import stringify_statistics, build_statistics_keyboard
from common.back_to_home_page import (
    back_to_admin_home_page_button,
    back_to_admin_home_page_handler,
)
from common.common import build_admin_keyboard
from start import admin_command

CHOOSE_STATISTIC = 0


async def statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        keyboard = build_statistics_keyboard()
        keyboard.append(back_to_admin_home_page_button[0])
        await update.callback_query.edit_message_text(
            text="اختر:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return CHOOSE_STATISTIC


async def choose_statistic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if "in_bot" in update.callback_query.data:
            all_users = models.User.get_users()
            subsicribers = models.User.get_users(subsicribers=True)
            await update.callback_query.edit_message_text(
                text=stringify_statistics(
                    subsicribers=len(subsicribers), all_users=len(all_users)
                ),
                reply_markup=build_admin_keyboard(),
            )
        else:

            connection = sqlite.connect('data/database.sqlite3')
            pd.read_sql_query("SELECT * FROM users", connection).to_excel(
                "excels/users.xlsx"
            )
            pd.read_sql_query("SELECT * FROM codes", connection).to_excel(
                "excels/codes.xlsx"
            )
            pd.read_sql_query("SELECT * FROM invite_links", connection).to_excel(
                "excels/invite_links.xlsx"
            )
            connection.close()

            await context.bot.send_media_group(
                chat_id=update.effective_chat.id,
                media=[
                    InputMediaDocument(media=open("excels/users.xlsx", mode="br")),
                    InputMediaDocument(media=open("excels/codes.xlsx", mode="br")),
                    InputMediaDocument(
                        media=open("excels/invite_links.xlsx", mode="br")
                    ),
                ],
            )

            await update.callback_query.delete_message()

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="تم إرسال ملفات الإكسل في الأعلى",
                reply_markup=build_admin_keyboard(),
            )
        return ConversationHandler.END


statistics_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            statistics,
            "^statistics$",
        ),
    ],
    states={
        CHOOSE_STATISTIC: [
            CallbackQueryHandler(
                choose_statistic,
                "^((excel)|(in_bot))_statistics$",
            ),
        ]
    },
    fallbacks=[
        admin_command,
        back_to_admin_home_page_handler,
    ],
)
