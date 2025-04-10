from telegram import InlineKeyboardButton
import models


def stringify_user(user: models.User, period: str):
    return (
        "معلومات مستخدم 👤\n\n"
        f"الآيدي: <code>{user.id}</code>\n"
        f"اسم المستخدم: {f'@{user.username}' if user.username else '<i>لا يوجد</i>'}\n"
        f"الاسم الكامل: <b>{user.name}</b>\n"
        f"كود الاشتراك الأخير: {f'<code>{user.cur_sub}</code>' if user.cur_sub else '<i>لا يوجد</i>'}\n"
        f"الفترة المتبقية في الإشتراك:\n<b>{period if period else 'غير محدد'}</b>"
    )


def build_user_info_keyboard(user_id: int):
    keyboard = [
        [
            InlineKeyboardButton(
                text="إلغاء الاشتراك الحالي ❌",
                callback_data=f"cancel_sub_{user_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="إضافة اشتراك جديد 🆕",
                callback_data=f"add_sub_{user_id}",
            ),
        ],
    ]
    return keyboard
