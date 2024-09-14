from telegram import (
    Update,
    InlineKeyboardButton,
    Chat,
)

from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
)

from common.decorators import check_if_user_member_decorator
from common.common import build_user_keyboard, build_admin_keyboard
from common.constants import *

from custom_filters import User, Admin


back_to_admin_home_page_button = [
    [
        InlineKeyboardButton(
            text=BACK_TO_HOME_PAGE_TEXT,
            callback_data="back to admin home page",
        )
    ],
]

back_to_user_home_page_button = [
    [
        InlineKeyboardButton(
            text=BACK_TO_HOME_PAGE_TEXT,
            callback_data="back to user home page",
        )
    ],
]


@check_if_user_member_decorator
async def back_to_user_home_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and User().filter(update):
        await update.callback_query.edit_message_text(
            text=HOME_PAGE_TEXT,
            reply_markup=build_user_keyboard(),
        )
        return ConversationHandler.END


async def back_to_admin_home_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.edit_message_text(
            text=HOME_PAGE_TEXT,
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


back_to_user_home_page_handler = CallbackQueryHandler(
    back_to_user_home_page, "^back to user home page$"
)
back_to_admin_home_page_handler = CallbackQueryHandler(
    back_to_admin_home_page, "^back to admin home page$"
)
