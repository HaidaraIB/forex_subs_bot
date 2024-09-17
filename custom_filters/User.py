from telegram import Update
from telegram.ext.filters import UpdateFilter
import models


class User(UpdateFilter):
    def filter(self, update: Update):
        return update.effective_user.id in [user.id for user in models.User.get_users()]
