from telegram import Chat, Update, error
from telegram.ext import ContextTypes, CallbackQueryHandler
from common.common import build_admin_keyboard
from custom_filters.Admin import Admin
import models


async def show_codes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        used_dict = {
            "NO": "غير مستخدمة",
            "YES": "مستخدمة",
        }
        used = update.callback_query.data.split(" ")[1]
        res = models.Code.get_by(used=True if used == "YES" else False)

        if not res:
            await update.callback_query.answer(f"ليس لديك أكواد {used_dict[used]}!")
            return

        try:
            codes = list(map(lambda x: f"<code>{x.code}</code>", res))
            await update.callback_query.edit_message_text(
                text=f'أكواد {used_dict[used]}:\n{"\n\n".join(codes)}',
                reply_markup=None,
            )
        except error.BadRequest:
            codes = list(map(lambda x: x.code, res))
            with open("codes.txt", mode="w", encoding="utf-8") as f:
                f.write("\n\n".join(codes))
            await update.callback_query.edit_message_text(
                text=f"العدد كبير جداً لذلك سيتم إرسالهم ضمن ملف.", reply_markup=None
            )
            await context.bot.send_document(
                chat_id=update.effective_chat.id, document="codes.txt", filename="codes"
            )

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="القائمة الرئيسية🔝",
            reply_markup=build_admin_keyboard(),
        )


show_unused_codes_handler = CallbackQueryHandler(
    callback=show_codes,
    pattern="^show NO codes$",
)
show_used_codes_handler = CallbackQueryHandler(
    callback=show_codes,
    pattern="^show YES codes$",
)
