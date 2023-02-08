from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import sqlite3 as sq
import random


TOKEN_API = "5503411089:AAFo_Hm5I31sX584rgwtpO8lMFTKCobhZaY"

async def on_startup(_):
    await db_start()
    
    scheduler.add_job(food_degr_system, trigger="interval", days=2)
    scheduler.add_job(salary_system, trigger="cron", day_of_week='fri')
    scheduler.add_job(income_system, trigger="cron", day_of_week='fri')
    scheduler.start()


async def db_start():
    global db, cur

    db = sq.connect('users.db')
    cur = db.cursor()

async def edit_profile(money, food, name):
    cur.execute("UPDATE profile SET money = '{}', food = '{}' WHERE name == '{}'".format(money, food, name))
    db.commit()

async def edit_city(money, food, city_name):
    cur.execute("UPDATE city SET money = '{}', food = '{}' WHERE city_name == '{}'".format(money, food, city_name))
    db.commit()


bot = Bot(TOKEN_API)
dp = Dispatcher(bot, storage=MemoryStorage())
scheduler = AsyncIOScheduler()


async def food_degr_system():
    for i in cur.execute("SELECT * FROM profile").fetchall():
        name = i[0]
        money = int(i[2])
        food = int(i[3])


        count_f = random.randrange(2, 10, 1)
        if food > 0:
            food = food - count_f
        elif food <= 0:
            money = money - 50

        await edit_profile(money, food, name)

async def salary_system():
    for i in cur.execute("SELECT * FROM profile").fetchall():
        name = i[0]
        salary = int(i[1])
        money = int(i[2])
        food = i[3]

        money = money + salary
        
        await edit_profile(money, food, name)

async def income_system():
    for i in cur.execute("SELECT * FROM city").fetchall():
        city_name = i[0]
        money = i[2]
        income = i[3]
        consumption = i[4]
        
        money = money + (income - consumption)

        cur.execute("UPDATE city SET money = '{}' WHERE city_name == '{}'".format(money, city_name))
        db.commit()



def get_main_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton(text='Империя')
    b2 = KeyboardButton(text='Город')
    b3 = KeyboardButton(text='Личные')
    b4 = KeyboardButton(text='Сменить персонажа')
    kb.add(b1).add(b2).add(b3).add(b4)

    return kb

def get_empire_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton(text='Отчет страны')
    b2 = KeyboardButton(text='Сменить должность')
    b3 = KeyboardButton(text='Сменить зарплату')
    b4 = KeyboardButton(text='Отмена')
    kb.add(b1).add(b2).add(b3).add(b4)

    return kb

def get_city_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton(text='Сардэс')
    b2 = KeyboardButton(text='Салмайа')
    b3 = KeyboardButton(text='Свельхейм')
    b4 = KeyboardButton(text='Рузис')
    b5 = KeyboardButton(text='Прервать')
    kb.add(b1, b2).add(b3, b4).add(b5)

    return kb

def get_maincity_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton(text='Постройка зданий')
    b2 = KeyboardButton(text='Найм войск')
    b3 = KeyboardButton(text='Торговля')
    b4 = KeyboardButton(text='Просмотреть отчет')
    b5 = KeyboardButton(text='Отмена')
    kb.add(b1, b2).add(b3, b4).add(b5)

    return kb

def get_city_trade_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton(text='Купить еды')
    b2 = KeyboardButton(text='Купить дерево')
    b3 = KeyboardButton(text='Купить камень')
    b4 = KeyboardButton(text='Купить уголь')
    b5 = KeyboardButton(text='Отмена')
    kb.add(b1, b2).add(b3, b4).add(b5)

    return kb

def get_personal_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton(text='Купить еды')
    b2 = KeyboardButton(text='Отчет')
    b3 = KeyboardButton(text='Отмена')
    kb.add(b1).add(b2).add(b3)
    
    return kb

def get_cancel() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton(text='Отмена'))

    return kb

def get_abort() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton(text='Прервать'))

    return kb



class ClientStatesGroup(StatesGroup):

    name_state = State()
    city_state = State()
    
    main_state = State()
    main_personal_state = State()
    food_state = State()
    report_state = State()
    
    main_city_state = State()
    main_city_trade_state = State()
    main_city_trade_food_state = State()
    main_city_trade_wood_state = State()

    main_empire_state = State()
    main_empire_name_state = State()
    main_empire_post_state = State()
    main_empire_salary_name_state = State()
    main_empire_salary_state = State()




@dp.message_handler(Text(equals='Отмена'), state='*')
async def cancel_command(message: types.Message):
    await message.answer('Действие отменено', reply_markup=get_main_keyboard())
    await ClientStatesGroup.main_state.set()
    

@dp.message_handler(Text(equals='Прервать'), state='*')
async def abort_command(message: types.Message, state: FSMContext):
    if state is None:
        return

    await state.finish()
    await message.answer("Процесс был прерван! Введите /start, чтобы начать!", reply_markup=ReplyKeyboardRemove())

@dp.message_handler(Text(equals=['Постройка зданий', 'Найм войск', 'Купить камень', 'Купить уголь']), state = "*")
async def check_food(message: types.Message):
    await message.delete()
    await message.answer('Данная функция пока еще в разработке!', reply_markup=get_maincity_keyboard())

# /START
@dp.message_handler(commands = ['start'], state=None)
async def start_command(message: types.Message):
    await ClientStatesGroup.name_state.set()
    await message.answer('Добро пожаловать в Телеграмм Бота по экономике Империи! \nВведите имя вашего персонажа', reply_markup=get_abort())
        
    
    

@dp.message_handler(lambda message: message.text.isdigit(), state = ClientStatesGroup.name_state)
async def check_name(message: types.Message):
    await message.reply('Неверный формат, используйте буквы')

@dp.message_handler(state=ClientStatesGroup.name_state)
async def load_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

        user_name = cur.execute("SELECT name FROM profile WHERE name == '{key}'".format(key=data['name'])).fetchone()
        if not user_name:
            cur.execute("INSERT INTO profile VALUES(?, ?, ?, ?, ?, ?, ?)", (data['name'], message.from_user.id, 0, 1000, 0, 'Безработный', ''))
            db.commit()
            await ClientStatesGroup.city_state.set()
            await message.answer(f"Приветствовую вас, {data['name']}. Выберите город, где находится ваш персонаж", reply_markup=get_city_keyboard())
        elif user_name[0] == message.text:
            user_id = cur.execute("SELECT user_id FROM profile WHERE name == '{key}'".format(key=data['name'])).fetchone()
            if message.from_user.id == int(user_id[0]):
                data['city'] = cur.execute("SELECT city_name FROM profile WHERE name == '{key}'".format(key=data['name'])).fetchone()
                await message.answer(f"Рад видеть вас, {data['name']}.", reply_markup=get_main_keyboard())
                await ClientStatesGroup.main_state.set()
            elif message.from_user.id != int(user_id[0]):
                await message.reply('Это имя пренадлежит другому персонажу, введите другое')

@dp.message_handler(Text(equals=['Сардэс', 'Салмайа', 'Свельхейм', 'Рузис']), state=ClientStatesGroup.city_state)
async def check_city(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['city'] = message.text
        await message.answer(f"Что-ж {data['name']}, добро пожаловать!", reply_markup=get_main_keyboard())
    
        cur.execute("UPDATE profile SET city_name = '{}' WHERE name == '{}'".format(data['city'], data['name']))
        db.commit()
    print(data)
    await ClientStatesGroup.main_state.set()


@dp.message_handler(Text(equals='Сменить персонажа'), state=ClientStatesGroup.main_state)
async def remake_char(message: types.Message):
    await message.answer('Введите имя вашего персонажа', reply_markup=get_abort())
    await message.delete()
    await ClientStatesGroup.name_state.set()

@dp.message_handler(Text(equals='Личные'), state=ClientStatesGroup.main_state)
async def buy_food(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        for i in cur.execute("SELECT * FROM profile WHERE name == '{key}'".format(key=data['name'])).fetchall():
            data['money'] = i[3]
            data['food'] = i[4]
        print(data)

    await ClientStatesGroup.main_personal_state.set()
    await message.answer('Что именно вы хотите посмотреть?', reply_markup=get_personal_keyboard())


@dp.message_handler(Text(equals='Империя'), state=ClientStatesGroup.main_state)
async def city_command(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['post'] = cur.execute("SELECT post FROM profile WHERE name == '{key}'".format(key=data['name'])).fetchone()
        post = cur.execute("SELECT post FROM empire WHERE post == '{key}'".format(key=data['post'][0])).fetchone()
        if data['post'] == post:
            await message.answer('Вы вошли в меню империи! Что хотите сделать?', reply_markup=get_empire_keyboard())
            await ClientStatesGroup.main_empire_state.set()
        elif data['post'] != post:
            await message.answer('Вы не являетесь правителем империи!')
            print(data)

@dp.message_handler(Text(equals='Отчет страны'), state=ClientStatesGroup.main_empire_state)
async def show_report(message: types.Message):
    for i in cur.execute("SELECT * FROM empire").fetchall():
        await message.answer(text=f'Отчет Империи Вандорис:\nВо главе государства: {i[1]}')
    for i in cur.execute("SELECT * FROM city").fetchall():
        await message.answer(text=f'Отчет города {i[0]}:\nКазна: {i[2]}\nДоход: {i[3]} талеров\nРасход: {i[4]} талеров\nСклад:\nЕда: {i[5]}\nДерево: {i[6]}\nКамень: {i[7]}\nЖелезо: {i[8]}\nУголь: {i[9]}\nАрмия: {i[10]}')
    await message.answer('Отчет проведен успешно!', reply_markup=get_cancel())

@dp.message_handler(Text(equals='Сменить должность'), state=ClientStatesGroup.main_empire_state)
async def city_command(message: types.Message):
    await ClientStatesGroup.main_empire_name_state.set()
    await message.answer('Введите имя персонажа, кому хотели бы сменить должность', reply_markup=get_abort())

@dp.message_handler(lambda message: message.text.isdigit(), state = ClientStatesGroup.main_empire_name_state)
async def check_changename(message: types.Message):
    await message.reply('Неверный формат, используйте буквы')

@dp.message_handler(state = ClientStatesGroup.main_empire_name_state)
async def load_changename(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['input_name'] = message.text
        name = cur.execute("SELECT name FROM profile WHERE name == '{key}'".format(key=data['input_name'])).fetchone()
        print(data['input_name'])
        if data['input_name'] == name[0]:
            await message.reply('Имя принято. Введите должность', reply_markup=get_abort())
            await ClientStatesGroup.main_empire_post_state.set()
        elif data['input_name'] != name[0]:
            await message.reply('Такого имени не существует', reply_markup=get_abort())

@dp.message_handler(Text(equals=['Королева', 'Король', 'Глава', 'Император', 'Регент', 'Безработный']), state = ClientStatesGroup.main_empire_post_state)
async def check_changepost(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        input_post = message.text
        cur.execute("UPDATE profile SET post = '{}' WHERE name == '{}'".format(input_post, data['input_name']))
        db.commit()
        await message.reply('Должность успешно изменена.', reply_markup=get_empire_keyboard())
        await ClientStatesGroup.main_empire_state.set()


@dp.message_handler(Text(equals='Сменить зарплату'), state=ClientStatesGroup.main_empire_state)
async def city_command(message: types.Message):
    await ClientStatesGroup.main_empire_salary_name_state.set()
    await message.answer('Введите имя персонажа, кому хотели бы сменить зарплату', reply_markup=get_abort())

@dp.message_handler(lambda message: message.text.isdigit(), state = ClientStatesGroup.main_empire_salary_name_state)
async def check_changename(message: types.Message):
    await message.reply('Неверный формат, используйте буквы')

@dp.message_handler(state = ClientStatesGroup.main_empire_salary_name_state)
async def load_changename(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['input_name'] = message.text
        name = cur.execute("SELECT name FROM profile WHERE name == '{key}'".format(key=data['input_name'])).fetchone()
        if data['input_name'] == name[0]:
            await message.reply('Имя принято. Введите должность', reply_markup=get_abort())
            await ClientStatesGroup.main_empire_salary_state.set()
        else:
            await message.reply('Такого имени не существует', reply_markup=get_abort())

@dp.message_handler(lambda message: not message.text.isdigit(), state = ClientStatesGroup.main_empire_salary_state)
async def check_changename(message: types.Message):
    await message.reply('Неверный формат, введите число')

@dp.message_handler(state = ClientStatesGroup.main_empire_salary_state)
async def check_changepost(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        input_salary = message.text
        cur.execute("UPDATE profile SET salary = '{}' WHERE name == '{}'".format(input_salary, data['input_name']))
        db.commit()
        await message.reply('Зарплата успешно изменена.', reply_markup=get_empire_keyboard())
        await ClientStatesGroup.main_empire_state.set()


@dp.message_handler(Text(equals='Город'), state=ClientStatesGroup.main_state)
async def city_command(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['post'] = cur.execute("SELECT post FROM profile WHERE name == '{key}'".format(key=data['name'])).fetchone()
        post = cur.execute("SELECT post FROM city WHERE city_name == '{key}'".format(key=data['city'][0])).fetchone()
        if data['post'] == post:
            await message.answer('Вы вошли в меню своего города! Что хотите сделать?', reply_markup=get_maincity_keyboard())
            for i in cur.execute("SELECT * FROM city WHERE city_name == '{key}'".format(key=data['city'][0])).fetchall():
                data['money'] = i[2]
                data['food'] = i[5]
                data['wood'] = i[6]
            print(data)
            await ClientStatesGroup.main_city_state.set()
        elif data['post'] != post:
            await message.answer('Вы не являетесь правителем этого города!')
            print(data)


@dp.message_handler(Text(equals='Торговля'), state=ClientStatesGroup.main_city_state)
async def add_food(message: types.Message):
    await ClientStatesGroup.main_city_trade_state.set()
    await message.answer('Выберите один из вариантов', reply_markup=get_city_trade_keyboard())


@dp.message_handler(Text(equals='Отчет'), state=ClientStatesGroup.main_personal_state)
async def show_report(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        for i in cur.execute("SELECT * FROM profile WHERE name == '{key}'".format(key=data['name'])).fetchall():
            await message.answer(text=f'Отчет:\nВаша должность: {i[5]}\nГород: {i[6]}\nТалеры: {i[3]}\nВаша зарплата(каждую пятницу): {i[2]} талеров\nЕда(каждые два дня): {i[4]}', reply_markup=get_cancel())


@dp.message_handler(Text(equals='Купить еды'), state=ClientStatesGroup.main_personal_state)
async def add_food(message: types.Message):
    await ClientStatesGroup.food_state.set()
    await message.answer('На данный момент еда стоит 50 талеров. \nВведите желаемое количество', reply_markup=get_cancel())
    await message.delete()

@dp.message_handler(lambda message: not message.text.isdigit(), state = ClientStatesGroup.food_state)
async def check_food(message: types.Message):
    await message.answer('Неверный формат. Введите число!')

@dp.message_handler(state = ClientStatesGroup.food_state)
async def load_food(message: types.Message, state: FSMContext):
    count = int(message.text)
    async with state.proxy() as data:
        money = int(data['money'])
        food = int(data['food'])
        if money >= count * 50:
            money = money - (count * 50)
            food = count + food
            await message.answer(f'Вы купили {count} еды.', reply_markup=get_main_keyboard())
            await edit_profile(money, food, data['name'])
        else:
            await message.answer(f"У вас недостаточно денег! Сейчас у вас {data['money']} талеров.", reply_markup=get_main_keyboard())

        await ClientStatesGroup.main_state.set()

@dp.message_handler(Text(equals='Просмотреть отчет'), state=ClientStatesGroup.main_city_state)
async def show_report(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        for i in cur.execute("SELECT * FROM city WHERE city_name == '{key}'".format(key=data['city'][0])).fetchall():
            await message.answer(text=f'Отчет города {i[0]}:\nКазна: {i[2]}\nДоход: {i[3]} талеров\nРасход: {i[4]} талеров\nСклад:\nЕда: {i[5]}\nДерево: {i[6]}\nКамень: {i[7]}\nЖелезо: {i[8]}\nУголь: {i[9]}\nАрмия: {i[10]}', reply_markup=get_cancel())

@dp.message_handler(Text(equals='Купить еды'), state=ClientStatesGroup.main_city_trade_state)
async def add_food(message: types.Message):
    await ClientStatesGroup.main_city_trade_food_state.set()
    await message.answer('На данный момент еда стоит 50 талеров. \nВведите желаемое количество', reply_markup=get_cancel())
    await message.delete()

@dp.message_handler(lambda message: not message.text.isdigit(), state = ClientStatesGroup.main_city_trade_food_state)
async def check_food(message: types.Message):
    await message.answer('Введите число!')

@dp.message_handler(state=ClientStatesGroup.main_city_trade_food_state)
async def load_city_food(message: types.Message, state: FSMContext):
    count = int(message.text)
    async with state.proxy() as data:
        money = int(data['money'])
        food = int(data['food'])
        if money >= count * 50:
            money = money - (count * 50)
            food = count + food
            await message.answer(f'Вы купили {count} еды.', reply_markup=get_maincity_keyboard())
            await edit_city(money, food, data['city'][0])
        else:
            await message.answer(f"У вас недостаточно денег! Сейчас у вас {data['money']} талеров.", reply_markup=get_maincity_keyboard())

        await ClientStatesGroup.main_city_state.set()

@dp.message_handler(Text(equals='Купить дерево'), state=ClientStatesGroup.main_city_trade_state)
async def add_wood(message: types.Message):
    await ClientStatesGroup.main_city_trade_wood_state.set()
    await message.answer('На данный момент дерево стоит 20 талеров. \nВведите желаемое количество', reply_markup=get_cancel())
    await message.delete()

@dp.message_handler(lambda message: not message.text.isdigit(), state = ClientStatesGroup.main_city_trade_wood_state)
async def check_wood(message: types.Message):
    await message.answer('Неверный формат. Введите число!')

@dp.message_handler(state=ClientStatesGroup.main_city_trade_wood_state)
async def load_city_wood(message: types.Message, state: FSMContext):
    count = int(message.text)
    async with state.proxy() as data:
        money = int(data['money'])
        wood = int(data['wood'])
        if money >= count * 20:
            money = money - (count * 20)
            wood = count + wood
            await message.answer(f'Вы купили {count} дерева.', reply_markup=get_maincity_keyboard())
            cur.execute("UPDATE city SET money = '{}', wood = '{}' WHERE city_name == '{}'".format(money, wood, data['city'][0]))
            db.commit()
        else:
            await message.answer(f"У вас недостаточно денег! Сейчас у вас {data['money']} талеров.", reply_markup=get_maincity_keyboard())

        await ClientStatesGroup.main_city_state.set()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)