from aiogram import types, html


async def get_main_keyboard(update, db):
    data = db.select_everything_db(update.from_user.id)
    data = data[0]
    balance = data[0]
    target = data[1]

    text = f"Money Keeper 🌍\n"\
           f"Профиль пользователя {html.bold(html.quote(update.from_user.full_name))} \n"\
           f"<b>Текущий баланс 💰:</b> {balance} \n"\
           f"<b>Цель 📊:</b> {target}"

    kb = [
        [
            types.KeyboardButton(text='Внести расход 📉'),
            types.KeyboardButton(text='Внести доход 📈'),
            types.KeyboardButton(text='Сменить цель 📊')
        ],
        [
            types.KeyboardButton(text='Показать последние операции 🗂️')
        ]
    ]

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder='Выбери действие'
    )

    return keyboard, text

async def get_confirmation():
    kb = [
        [types.InlineKeyboardButton(text='Подтвердить ✅', callback_data='confirmation')],
        [types.InlineKeyboardButton(text='Отклонить ❌', callback_data='refusal')]
    ]

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard


hello_text = ("Я - бот-помощник в учёте финансов 😇\n"
              "Отправь свой текущий баланс и мы приступим к работе")

bad_balance = ("Слишком много неудачных попыток! 🤕\n"
               "Система выбрала баланс по умолчанию")

bad_expect_balance = ('Превышено время ожидания! ⏱️\n'
                      'Система выбрала баланс по умолчанию')

