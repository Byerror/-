from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)


user_markup = ReplyKeyboardMarkup(
    [
        [
            KeyboardButton("⚡️ Профиль"),
            KeyboardButton("🔗 Реферальная система")
        ],
        [
            KeyboardButton("💌 О нас")
        ]
    ],
    resize_keyboard=True
)


profile_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton("💸 Вывести деньги", callback_data="withdraw_money")],
        [InlineKeyboardButton("🫣 Скрыть имя", callback_data="hidden_user")]
    ]
)


admin_markup = InlineKeyboardMarkup(
inline_keyboard=[
        [
            InlineKeyboardButton(
                "⚡️ Рассылка",
                callback_data="mailing"
            ),
            InlineKeyboardButton(
                "⛑ Включение акции 1.1х",
                callback_data="promo_1x1"
            ),
            InlineKeyboardButton(
                "😈 Изменить скам сумму",
                callback_data="scam_config"
            )
        ]
    ]
)


back_markup = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(
        "◀️ Отмена",
        callback_data="cancel"
    )]]
)


accept_mailing = InlineKeyboardMarkup(
    inline_keyboard=[[
        InlineKeyboardButton(
            "✅ Начать",
            callback_data="start_mailing"
        ),
        InlineKeyboardButton(
            "◀️ Отмена",
            callback_data="cancel"
        )
    ]]
)


close_mailing = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(
        "💢 Понятно",
        callback_data="close_mailing"
    )]]
)
