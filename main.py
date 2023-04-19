import telebot
from telebot import types
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
from telebot import custom_filters

state_storage = StateMemoryStorage()

API_TOKEN = '6219528902:AAF7a-Yrg3yw25EaV4xBXCNXy3nltSDR0Fo'

bot = telebot.TeleBot(API_TOKEN, state_storage=state_storage)


class UserStates(StatesGroup):
    body_mass = State()
    body_height = State()
    height = State()
    systolic_blood_pressure = State()  # Изменение систолического артериального давления
    heart_rate = State()  # Изменение частоты сердечных сокращений
    respiratory_rate = State()  # Изменение частоты дыхательных движений
    diuresis = State()  # Диурез
    end = State()  # Окончание работы


class UserData:
    def __init__(self):
        pass

systolic_blood_pressure_buttons = [
            [types.InlineKeyboardButton(text="Значения в пределах нормы", callback_data="CAD_NORM")],
            [types.InlineKeyboardButton(text="Снижение САД на 20-50", callback_data="CAD_1")],
            [types.InlineKeyboardButton(text="Снижение САД на 50-80", callback_data="CAD_2")],
            [types.InlineKeyboardButton(text="Снижение САД на более 80", callback_data="CAD_3")],
            [types.InlineKeyboardButton(text="Новое кровотечение", callback_data="START")],
        ]
systolic_blood_pressure_keyboard = types.InlineKeyboardMarkup(systolic_blood_pressure_buttons)

heart_rate_buttons = [
    [types.InlineKeyboardButton(text="Значения в пределах нормы", callback_data="HR_NORM")],
    [types.InlineKeyboardButton(text="Повышение ЧСС на 1-20 уд", callback_data="HR_1")],
    [types.InlineKeyboardButton(text="Повышение ЧСС на 20-40 уд", callback_data="HR_2")],
    [types.InlineKeyboardButton(text="Повышение ЧСС Сна более 40 уд", callback_data="HR_3")],
    [types.InlineKeyboardButton(text="Новое кровотечение", callback_data="START")]
]
heart_rate_buttons_keyboard = types.InlineKeyboardMarkup(heart_rate_buttons)

respiratory_rate_buttons = [
        [types.InlineKeyboardButton(text="ЧДД менее 26/мин",        callback_data="BR_1")],
        [types.InlineKeyboardButton(text="ЧДД 26-30/мин",           callback_data="BR_2")],
        [types.InlineKeyboardButton(text="ЧДД более 30/мин",        callback_data="BR_3")],
        [types.InlineKeyboardButton(text="Новое кровотечение",   callback_data="START")]
    ]
respiratory_rate_keyboard = types.InlineKeyboardMarkup(respiratory_rate_buttons)

diuresis_buttons = [
    [types.InlineKeyboardButton(text="Значения в пределах нормы", callback_data="DIURES_NORM")],
    [types.InlineKeyboardButton(text="Диурез более 20-30 мл/ч", callback_data="DIURES_1")],
    [types.InlineKeyboardButton(text="Диурез 5-20 мл/ч", callback_data="DIURES_2")],
    [types.InlineKeyboardButton(text="Анурия", callback_data="DIURES_3")],
    [types.InlineKeyboardButton(text="Новое кровотечение", callback_data="START")]
]
diuresis_keyboard = types.InlineKeyboardMarkup(diuresis_buttons)

FIRST_SCALE_STATES = ((UserStates.body_mass, 'Введите массу тела пациентки по примеру: 60.5', None),
                      (UserStates.body_height, 'Введите рост пациентки по примеру: 178', None),
                      (UserStates.systolic_blood_pressure, 'Изменение систоличесокго артериального давления (САД)\n\nИли по копке можете вернуться в главное меню', systolic_blood_pressure_keyboard),
                      (UserStates.heart_rate, 'Изменение частоты сердечных сокращений(ЧСС)\n\nИли по копке можете вернуться в главное меню', heart_rate_buttons_keyboard),
                      (UserStates.respiratory_rate, 'Изменение частоты дыхательных движений(ЧДД)\n\nИли по копке можете вернуться в главное меню', respiratory_rate_keyboard),
                      (UserStates.diuresis, 'Диурез (мл/ч)\n\nИли по копке можете вернуться в главное меню', diuresis_keyboard),
                      (UserStates.end, 'Результат', None))

SECOND_SCALE_STATES = ((UserStates.body_mass, 'Введите массу тела пациентки по примеру: 60.5', None),
                      (UserStates.body_height, 'Введите рост пациентки по примеру: 178', None),
                      (UserStates.systolic_blood_pressure, 'Изменение систоличесокго артериального давления (САД)\n\nИли по копке можете вернуться в главное меню', systolic_blood_pressure_keyboard),
                      (UserStates.heart_rate, 'Изменение частоты сердечных сокращений(ЧСС)\n\nИли по копке можете вернуться в главное меню', heart_rate_buttons_keyboard),
                      (UserStates.respiratory_rate, 'Изменение частоты дыхательных движений(ЧДД)\n\nИли по копке можете вернуться в главное меню', respiratory_rate_keyboard),
                      (UserStates.end, 'Результат', None))


class UserScale:
    def __init__(self, scale_states):
        self.scale_states = scale_states
        self.current_state = 0

    def next(self):
        self.current_state += 1
        return self.scale_states[self.current_state - 1]


users_scale = {}
users_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    """
    Начало диалога с ботом
    """
    buttons = [
        [types.InlineKeyboardButton(
            text="Начать", callback_data="START")],
    ]

    keyboard = types.InlineKeyboardMarkup(buttons)
    bot.send_message(
        message.chat.id,
        text=f'Привет, {message.from_user.first_name}, я бот для оценки риска развития и степени тяжести кровотечений '
             f'в родах, нажми кнопку, чтобы начать.',
        reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('START'))
def new_bleeding(call):
    buttons = [
        [types.InlineKeyboardButton(text="Шкала 1", callback_data="first_scale")],
        [types.InlineKeyboardButton(text="Шкала 2", callback_data="second_scale")]]
    keyboard = types.InlineKeyboardMarkup(buttons)
    users_data[call.message.chat.id] = UserData()
    bot.send_message(call.message.chat.id, text='Выберите шкалу', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data in ('CAD_NORM', 'CAD_1', 'CAD_2', 'CAD_3'))
def cad_query(call):
    if call.data == 'CAD_NORM':
        users_data[call.message.chat.id].systolic_blood_pressure = 0
    elif call.data == 'CAD_1':
        users_data[call.message.chat.id].systolic_blood_pressure = 1
    elif call.data == 'CAD_2':
        users_data[call.message.chat.id].systolic_blood_pressure = 2
    elif call.data == 'CAD_3':
        users_data[call.message.chat.id].systolic_blood_pressure = 3

    state, text, keyboard = users_scale[call.message.chat.id].next()
    bot.set_state(call.message.chat.id, state, call.message.chat.id)
    bot.send_message(call.message.chat.id, text=text, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data in ('HR_NORM', 'HR_1', 'HR_2', 'HR_3'))
def hr_query(call):
    if call.data == 'HR_NORM':
        users_data[call.message.chat.id].heart_rate = 0
    elif call.data == 'HR_1':
        users_data[call.message.chat.id].heart_rate = 1
    elif call.data == 'HR_2':
        users_data[call.message.chat.id].heart_rate = 2
    elif call.data == 'HR_3':
        users_data[call.message.chat.id].heart_rate = 3

    state, text, keyboard = users_scale[call.message.chat.id].next()
    bot.set_state(call.message.chat.id, state, call.message.chat.id)
    bot.send_message(call.message.chat.id, text=text, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data in ('BR_1', 'BR_2', 'BR_3'))
def br_query(call):
    if call.data == 'BR_1':
        users_data[call.message.chat.id].respiratory_rate = 1
    elif call.data == 'BR_2':
        users_data[call.message.chat.id].respiratory_rate = 2
    elif call.data == 'BR_3':
        users_data[call.message.chat.id].respiratory_rate = 3

    state, text, keyboard = users_scale[call.message.chat.id].next()
    bot.set_state(call.message.chat.id, state, call.message.chat.id)
    bot.send_message(call.message.chat.id, text=text, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data in ('DIURES_NORM', 'DIURES_1', 'DIURES_2', 'DIURES_3'))
def diures_query(call):
    if call.data == 'DIURES_NORM':
        users_data[call.message.chat.id].diures = 0
    elif call.data == 'DIURES_1':
        users_data[call.message.chat.id].diures = 1
    elif call.data == 'DIURES_2':
        users_data[call.message.chat.id].diures = 2
    elif call.data == 'DIURES_3':
        users_data[call.message.chat.id].diures = 3

    state, text, keyboard = users_scale[call.message.chat.id].next()
    bot.set_state(call.message.chat.id, state, call.message.chat.id)
    bot.send_message(call.message.chat.id, text=text, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "first_scale":
        users_scale[call.message.chat.id] = UserScale(FIRST_SCALE_STATES)
    elif call.data == "second_scale":
        users_scale[call.message.chat.id] = UserScale(SECOND_SCALE_STATES)

    state, text, keyboard = users_scale[call.message.chat.id].next()
    bot.set_state(call.message.chat.id, state, call.message.chat.id)
    bot.send_message(call.message.chat.id, text=text)

# Any state
@bot.message_handler(state="*", commands=['cancel'])
def any_state(message):
    """
    Cancel state
    """
    bot.send_message(message.chat.id, "Your state was cancelled.")
    bot.delete_state(message.from_user.id, message.chat.id)

@bot.message_handler(state=UserStates.body_mass)
def ask_body_mass(message):
    state, text, keyboard = users_scale[message.chat.id].next()

    bot.set_state(message.chat.id, state, message.chat.id)
    bot.send_message(message.chat.id, text=text)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        users_data[message.chat.id].body_mass_index = message.text


@bot.message_handler(state=UserStates.body_height)
def ask_body_height(message):
    state, text, keyboard = users_scale[message.chat.id].next()

    bot.set_state(message.chat.id, state, message.chat.id)
    bot.send_message(message.chat.id, text=text, reply_markup=keyboard)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        users_data[message.chat.id].body_height = message.text

@bot.message_handler(state=UserStates.systolic_blood_pressure)
def ask_systolic_blood_pressure(message):
    print("systolic_blood_pressure")
    print(message.text)
    state, text, keyboard = users_scale[message.chat.id].next()

    bot.set_state(message.chat.id, state, message.chat.id)
    bot.send_message(message.chat.id, text=text)

@bot.message_handler(state=UserStates.heart_rate)
def heart_rate(message):
    print("heart_rate", message.text)
    state, text = users_scale[message.chat.id].next()

    bot.set_state(message.chat.id, state, message.chat.id)
    bot.send_message(message.chat.id, text=text)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['heart_rate'] = message.text

bot.add_custom_filter(custom_filters.StateFilter(bot))

bot.infinity_polling(skip_pending=True)
