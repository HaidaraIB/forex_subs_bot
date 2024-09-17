from telegram import Update, Chat
from telegram.ext import ContextTypes, CallbackQueryHandler


async def stop_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        if context.user_data.get("wanna_remincer", True):
            context.user_data["wanna_reminder"] = False
            await update.callback_query.answer(
                text="لن يتم تذكيرك بعد الآن",
                show_alert=True,
            )
        await update.callback_query.answer(
            text="لقد قمت بإيقاف التذكير بالفعل",
            show_alert=True,
        )


stop_reminder_handler = CallbackQueryHandler(stop_reminder, "^stop_reminder$")
