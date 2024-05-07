from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from filters import ChatTypeFilter, UserStates
from database import DataBase
from time import time
import verifications
import keyboards


start_router = Router()
router1 = Router()
router2 = Router()
router_filter = Router()

start_router.message.filter(ChatTypeFilter(chat_type='private'), F.text)
router1.message.filter(ChatTypeFilter(chat_type='private'), F.text)
router2.message.filter(ChatTypeFilter(chat_type='private'), F.text)
router_filter.message.filter(ChatTypeFilter(chat_type='private'))


@start_router.message(Command('start'))
async def start_command(msg: Message, state: FSMContext, db: DataBase):
    await state.clear()
    res = db.select_everything_db(msg.from_user.id)

    if len(res) == 0:
        await state.set_state(UserStates.set_balance)
        await state.update_data(spam=0)
        await msg.answer(keyboards.hello_text)
        await verifications.check_spam_balance(msg, state, db)
    else:
        kb, text = await keyboards.get_main_keyboard(msg, db)
        await msg.answer(text, reply_markup=kb, parse_mode=ParseMode.HTML)

@start_router.message(UserStates.set_balance)
async def set_balance(msg: Message, state: FSMContext, db: DataBase):
    await verifications.add_spam(state)
    res = verifications.check_balance(msg.text)

    if res == 'success' and await state.get_state() == UserStates.set_balance:
        db.insert_db(msg.from_user.id, msg.text)
        await msg.reply('Отлично! 😀')
        await state.clear()

        kb, text = await keyboards.get_main_keyboard(msg, db)
        await msg.answer(text, reply_markup=kb, parse_mode=ParseMode.HTML)
    else:
        data = await state.get_data()
        if data['spam'] > 5:
            await msg.answer(keyboards.bad_balance)
            await state.clear()
            db.insert_db(msg.from_user.id, '0')

            kb, text = await keyboards.get_main_keyboard(msg, db)
            await msg.answer(text, reply_markup=kb, parse_mode=ParseMode.HTML)
        else:
            text = res + '\nПопробуй ввести еще раз'
            await msg.reply(text)
            await verifications.check_spam_balance(msg, state, db)


@router1.message(F.text == 'Сменить цель 📊', StateFilter(None))
async def set_target(msg: Message, state: FSMContext, db: DataBase):
    if not verifications.verify_user(msg.from_user.id, db):
        return

    await state.set_state(UserStates.set_target)
    await state.update_data(spam=0, start_operation=time())
    await msg.reply('Введи новое числовое значение', reply_markup=ReplyKeyboardRemove())
    await verifications.check_spam(msg, state, UserStates.set_target, db, timer=30)

@router1.message(UserStates.set_target)
async def get_target(msg: Message, state: FSMContext, db: DataBase):
    await verifications.add_spam(state)
    res = verifications.check_target(msg.text)

    if res == 'success' and await state.get_state() == UserStates.set_target:
        db.update_db(msg.from_user.id, 'target', msg.text)
        await state.clear()
        await msg.reply('Отлично! 😀')

        kb, text = await keyboards.get_main_keyboard(msg, db)
        await msg.answer(text, reply_markup=kb, parse_mode=ParseMode.HTML)
    else:
        if not await verifications.check_how_much_spam(msg, state, db, howmuch=3):
            text = res + '\nПопробуй ввести еще раз'
            await msg.reply(text)
            await verifications.check_spam(msg, state, UserStates.set_target, db, timer=30)

@router1.message(F.text == 'Показать последние операции 🗂️', StateFilter(None))
async def get_last_operations(msg: Message, db: DataBase):
    if not verifications.verify_user(msg.from_user.id, db):
        return

    res = db.select_db(msg.from_user.id, 'operations')
    res = verifications.get_dictionary(res[0][0])
    res = res['operations']

    if len(res) == 0:
        await msg.reply('У тебя нет последних операций 😧')
    else:
        text = ''
        for i in res:
            text = text + ': '.join(i) + '\n'

        await msg.reply(text)


@router2.message(F.text == 'Внести доход 📈', StateFilter(None))
async def get_income(msg: Message, state: FSMContext, db: DataBase):
    if not verifications.verify_user(msg.from_user.id, db):
        return

    await state.set_state(UserStates.get_name_operation)
    await state.update_data(
        spam=0,
        start_operation=time(),
        type_operation='+'
    )

    await msg.reply('Введи описание операции \n(не более 16 символов)', reply_markup=ReplyKeyboardRemove())
    await verifications.check_spam(msg, state, UserStates.get_name_operation, db, timer=30)

@router2.message(F.text == 'Внести расход 📉', StateFilter(None))
async def get_spending(msg: Message, state: FSMContext, db: DataBase):
    if not verifications.verify_user(msg.from_user.id, db):
        return

    await state.set_state(UserStates.get_name_operation)
    await state.update_data(
        spam=0,
        start_operation=time(),
        type_operation='-'
    )

    await msg.reply('Введи описание операции \n(не более 16 символов)', reply_markup=ReplyKeyboardRemove())
    await verifications.check_spam(msg, state, UserStates.get_name_operation, db, timer=30)

@router2.message(UserStates.get_name_operation)
async def get_name_operation(msg: Message, state: FSMContext, db: DataBase):
    await verifications.add_spam(state)
    res = verifications.check_name_operation(msg.text)

    if res == 'success' and await state.get_state() == UserStates.get_name_operation:
        await state.set_state(UserStates.get_sum_operation)
        await state.update_data(spam=0, name_operation=msg.text)
        await msg.answer('Введи сумму операции')
        await verifications.check_spam(msg, state, UserStates.get_sum_operation, db, timer=30)
    else:
        if not await verifications.check_how_much_spam(msg, state, db, howmuch=3):
            text = res + '\nПопробуй ввести еще раз'
            await msg.reply(text)
            await verifications.check_spam(msg, state, UserStates.get_name_operation, db, timer=30)

@router2.message(UserStates.get_sum_operation)
async def get_sum_operation(msg: Message, state: FSMContext, db: DataBase):
    await verifications.add_spam(state)
    res = verifications.check_sum_operation(msg.text)

    if res == 'success' and await state.get_state() == UserStates.get_sum_operation:
        user_data = await state.get_data()
        start_operation = user_data['start_operation']
        type_operation = user_data['type_operation']
        name_operation = user_data['name_operation']
        sum_operation = f'{type_operation}{msg.text}'

        check_balance = verifications.check_current_balance(msg.from_user.id, sum_operation, db)
        if check_balance == 'success':
            await state.set_state(UserStates.confirm_operation)
            await state.set_data({})
            await state.update_data(
                name_operation=name_operation,
                sum_operation=sum_operation,
                spam=0,
                start_operation=start_operation
            )

            kb = await keyboards.get_confirmation()
            bot_msg = await msg.answer(
                        text=f'Подтверди внесение операции: \n"{name_operation}": {sum_operation}',
                        reply_markup=kb
            )
            await verifications.check_spam(msg, state, UserStates.confirm_operation, db, callback=bot_msg, timer=25)
        else:
            await msg.reply(check_balance)
            await state.clear()
            kb, text = await keyboards.get_main_keyboard(msg, db)
            await msg.answer(text, reply_markup=kb, parse_mode=ParseMode.HTML)
    else:
        if not await verifications.check_how_much_spam(msg, state, db, howmuch=5):
            text = res + '\nПопробуй ввести еще раз'
            await msg.reply(text)
            await verifications.check_spam(msg, state, UserStates.get_sum_operation, db, timer=30)

@router2.callback_query(F.data == 'refusal', UserStates.confirm_operation)
async def refuse_operation(callback: CallbackQuery, state: FSMContext, db: DataBase):
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer('Операция отклонена ❌')

    kb, text = await keyboards.get_main_keyboard(callback, db)
    await callback.message.answer(text, reply_markup=kb, parse_mode=ParseMode.HTML)

@router2.callback_query(F.data == 'confirmation', UserStates.confirm_operation)
async def confirm_operation(callback: CallbackQuery, state: FSMContext, db: DataBase):
    data = await state.get_data()
    name_operation = data['name_operation']
    sum_operation = data['sum_operation']
    await state.clear()

    balance = db.select_db(callback.from_user.id, 'balance')
    operations = db.select_db(callback.from_user.id, 'operations')
    balance = int(balance[0][0])
    operations = verifications.get_dictionary(operations[0][0])

    if sum_operation[0] == '+':
        balance += int(sum_operation[1:])
    else:
        balance -= int(sum_operation[1:])

    if len(operations['operations']) > 20:
        operations['operations'].pop(0)

    lst = [name_operation, sum_operation]
    operations['operations'].append(lst)
    operations = verifications.get_string(operations)

    db.update_db(callback.from_user.id, 'balance', balance)
    db.update_db(callback.from_user.id, 'operations', operations)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer('Операция подтверждена ✅')
    kb, text = await keyboards.get_main_keyboard(callback, db)
    await callback.message.answer(text, reply_markup=kb, parse_mode=ParseMode.HTML)


@router_filter.message(F.text)
async def filter_message(msg: Message, state: FSMContext, db: DataBase):
    if not verifications.verify_user(msg.from_user.id, db):
        await start_command(msg, state, db)
        return

    kb = None
    if not await state.get_state():
        kb, text = await keyboards.get_main_keyboard(msg, db)

    await msg.reply('Я тебя не понимаю!', reply_markup=kb)
