import asyncio
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.types import Message
from json import loads, dumps

from database import DataBase
from filters import UserStates
import keyboards


INCORRECT_VALUES = ".,'+)(*&^%$#@!:;'?/\\"

async def check_spam(msg: Message, state: FSMContext, verify_state, db: DataBase, timer=15, callback=None):
    if await state.get_state() == verify_state:
        data1 = await state.get_data()
        counter1 = data1['spam']
        time1 = data1['start_operation']

        await asyncio.sleep(timer)

        if await state.get_state() == verify_state:
            data2 = await state.get_data()
            counter2 = data2['spam']
            time2 = data2['start_operation']

            if counter1 == counter2 and time1 == time2:
                if callback:
                    await callback.edit_reply_markup(reply_markup=None)

                text = 'Превышено время ожидания! ⏱️ \nОперация отменена'
                await msg.answer(text)
                await state.clear()

                kb, text2 = await keyboards.get_main_keyboard(msg, db)
                await msg.answer(text2, reply_markup=kb, parse_mode=ParseMode.HTML)
            else:
                return

async def check_spam_balance(msg: Message, state: FSMContext, db: DataBase):
    if await state.get_state() == UserStates.set_balance:
        spam1 = await state.get_data()
        spam1 = spam1['spam']

        await asyncio.sleep(120)

        if await state.get_state() == UserStates.set_balance:
            spam2 = await state.get_data()
            spam2 = spam2['spam']

            if spam1 == spam2:
                await msg.answer(keyboards.bad_expect_balance)
                await state.clear()
                db.insert_db(msg.from_user.id, '0')

                kb, text = await keyboards.get_main_keyboard(msg, db)
                await msg.answer(text, reply_markup=kb, parse_mode=ParseMode.HTML)

async def check_how_much_spam(msg: Message, state: FSMContext, db: DataBase, howmuch=5):
    data = await state.get_data()
    value = data['spam']

    if value > howmuch:
        await msg.answer('Слишком много неудачных попыток! 🫣\nОперация отменена')
        await state.clear()

        kb, text = await keyboards.get_main_keyboard(msg, db)
        await msg.answer(text, reply_markup=kb, parse_mode=ParseMode.HTML)
        return True
    else:
        return False

async def add_spam(state: FSMContext):
    data = await state.get_data()
    value = data['spam'] + 1
    await state.update_data(spam=value)


def verify_user(user_id, db: DataBase):
    if len(db.select_everything_db(user_id)) == 0:
        return False
    else:
        return True

def check_current_balance(user_id, sum_operation, db: DataBase):
    res = db.select_db(user_id, 'balance')
    balance = int(res[0][0])

    if balance + int(sum_operation) > 5000000:
        return 'Превышено максимальное допусимое значение баланса! 🤥\nОперация невозможна'

    if balance + int(sum_operation) < -5000000:
        return 'Слишком маленький баланс! 🫡\nОперация невозможна'

    return 'success'

def check_balance(balance):
    try:
        for i in INCORRECT_VALUES:
            if i in balance:
                return 'Некорректное значение! 🙄'

        if balance[0] == '0' and len(balance) > 1:
            return 'Значение не может начинаться с нуля 😐'

        balance = int(balance)
        if balance < -5000000:
            return 'Слишком маленькое значение 😒'
        if balance > 5000000:
            return 'Слишком большое значение 😦'

        return 'success'

    except ValueError:
        return 'Некорректное значение! 🙄'

def check_target(target):
    try:
        for i in INCORRECT_VALUES:
            if i in target:
                return 'Некорректное значение! 🙄'

        if target[0] == '0' and len(target) > 1:
            return 'Значение не может начинаться с нуля 😐'

        target = int(target)
        if target < -5000000:
            return 'Слишком маленькое значение 🫨'
        if target > 5000000:
            return 'Хватит строить нереалистичные планы 🤨'

        return 'success'

    except ValueError:
        return 'Некорректное значение! 🙄'

def check_name_operation(name):
    if len(name) < 2:
        return 'Слишком короткое описание! 😐'
    if len(name) > 16:
        return 'Превышена максимальная длина описания! 🫤'
    else:
        return 'success'

def check_sum_operation(value):
    try:
        for i in INCORRECT_VALUES:
            if i in value:
                return 'Некорректное значение! 🙄'

        if value == '0':
            return 'Бессмысленная операция 😐'
        if value[0] == '0':
            return 'Значение не может начинаться с нуля 😐'

        value = int(value)
        if value < 1:
            return 'Требуется использовать только положительные числа 🫤'
        if value > 400000:
            return 'Слишком большое значение 🤓'

        return 'success'

    except ValueError:
        return 'Некорректное значение! 🙄'


def get_string(dictionary):
    return dumps(dictionary)

def get_dictionary(string):
    return loads(string)


