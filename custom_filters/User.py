from telegram import Update
from telegram.ext.filters import UpdateFilter
import models


class User(UpdateFilter):
    def filter(self, update: Update):
        return update.effective_user.id not in [
            admin.id for admin in models.Admin.get_admin_ids()
        ]
