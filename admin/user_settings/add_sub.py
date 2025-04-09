from telegram import (
    Update,
    Chat,
    ReplyKeyboardMarkup,
    KeyboardButton,
    KeyboardButtonRequestUsers,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from custom_filters import Admin
import models
from common.back_to_home_page import back_to_admin_home_page_handler
from start import admin_command


async def add_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        pass
