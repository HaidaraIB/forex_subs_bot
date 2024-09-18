from telegram import Update
from telegram.ext import CallbackQueryHandler, InvalidCallbackData
from start import start_command, admin_command
from common.common import invalid_callback_data, create_folders

from common.back_to_home_page import (
    back_to_admin_home_page_handler,
    back_to_user_home_page_handler,
)

from common.error_handler import error_handler

from user.user_calls import *
from user.stop_reminder import *
from user.check_code import *
from user.check_period import *
from user.free_sub import *
from user.join_private_channel import *

from admin.admin_calls import *
from admin.admin_settings import *
from admin.broadcast import *
from admin.ban import *
from admin.statistics import *
from admin.codes_settings import *

from models import create_tables

from MyApp import MyApp


def main():
    create_folders()
    create_tables()

    app = MyApp.build_app()

    app.add_handler(
        CallbackQueryHandler(
            callback=invalid_callback_data, pattern=InvalidCallbackData
        )
    )
    # ADMIN SETTINGS
    app.add_handler(admin_settings_handler)
    app.add_handler(show_admins_handler)
    app.add_handler(add_admin_handler)
    app.add_handler(remove_admin_handler)

    app.add_handler(broadcast_message_handler)

    app.add_handler(ban_unban_user_handler)

    app.add_handler(statistics_handler)

    # CODES SETTINGS
    app.add_handler(add_codes_handler)
    app.add_handler(show_used_codes_handler)
    app.add_handler(show_unused_codes_handler)

    # USER
    app.add_handler(stop_reminder_handler)
    app.add_handler(check_code_handler)
    app.add_handler(check_period_handler)
    app.add_handler(join_private_channel_handler)
    app.add_handler(free_sub_handler)

    app.add_handler(admin_command)
    app.add_handler(start_command)
    app.add_handler(find_id_handler)
    app.add_handler(hide_ids_keyboard_handler)
    app.add_handler(back_to_user_home_page_handler)
    app.add_handler(back_to_admin_home_page_handler)

    app.add_error_handler(error_handler)

    app.run_polling(allowed_updates=Update.ALL_TYPES)