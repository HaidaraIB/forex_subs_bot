from telegram import Update
from telegram.ext import ContextTypes
import functools
import models


def check_if_user_banned_dec(func):
    @functools.wraps(func)
    async def wrapper(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        user = models.User.get_users(user_id=update.effective_user.id)
        if user.is_banned:
            return
        return await func(update, context, *args, **kwargs)

    return wrapper


def add_new_user_dec(func):
    @functools.wraps(func)
    async def wrapper(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        old_user = models.User.get_users(user_id=update.effective_user.id)
        if not old_user:
            new_user = update.effective_user
            await models.User.add_new_user(
                user_id=new_user.id,
                username=new_user.username,
                name=new_user.full_name,
            )
        return await func(update, context, *args, **kwargs)

    return wrapper
